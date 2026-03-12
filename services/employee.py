from calendar import monthrange
from datetime import date
from collections import defaultdict
from typing import Optional, Tuple, List, Dict

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session, joinedload, contains_eager
from sqlalchemy import extract
from models.log import LogDailySummary
from models.calendar import CalendarDay
from models.project import Project
from models.employee import Employee, EmployeeHourTarget, EmployeeVacationClaim
from models.config import VacationRule

def get_employee_detailed(db: Session, emp_id: str) -> Optional[Employee]:
    emp = (
        db.query(Employee)
        .options(
            joinedload(Employee.hour_targets),
            joinedload(Employee.vacation_claims)
        )
        .filter(Employee.id == emp_id)
        .first()
    )

    if not emp: return None # gate
    
    first_year = emp.first_work_year
    current_year = date.today().year
    year_lut = {claim.year for claim in emp.vacation_claims}
    final_claims = list(emp.vacation_claims)

    # Calculate missing vacation claims based on seniority rules
    for year in range(first_year, current_year + 1):
        if year not in year_lut:
            seniority = year - first_year
            rule = (
                db.query(VacationRule)
                .filter(
                    VacationRule.min_years <= seniority,
                    VacationRule.max_years >= seniority
                )
                .first()
            )

            final_claims.append(EmployeeVacationClaim(
                year=year,
                days=rule.days if rule else 0.0
            ))

    emp.vacation_claims = final_claims
    return emp

def get_employee_lifetime_stats(db: Session, emp_id: str, calc_end: Optional[date] = None) -> Tuple[float, float]:
    emp = db.query(
        Employee
    ).filter(
        Employee.id == emp_id
    ).first()
    if not emp: return 0.0, 0.0
    
    calc_start = emp.start_tracking_date
    if calc_end is None: calc_end = date.today()

    days = (
        db.query(CalendarDay)
        .options(joinedload(CalendarDay.holiday))
        .filter(
            CalendarDay.date >= calc_start, 
            CalendarDay.date < calc_end
        ).order_by(CalendarDay.date)
        .all()
    )
    
    contracts = db.query(EmployeeHourTarget).filter(EmployeeHourTarget.employee_id == emp_id).all()
    
    logs = (
        db.query(LogDailySummary)
        .options(joinedload(LogDailySummary.project_hours))
        .filter(
            LogDailySummary.employee_id == emp_id,
            LogDailySummary.date >= calc_start,
            LogDailySummary.date < calc_end
        )
        .all()
    )
    
    log_map = {l.date: l for l in logs}
    actual_sum = sum(sum(p.time for p in log.project_hours) for log in logs)
    target_sum = sum(c.starting_balance for c in contracts if c.starting_balance)

    for day in days:
        log = log_map.get(day.date)
        if log:
            target_sum += log.target_hours
            continue
        
        if day.is_weekend: continue

        base_target_factor = 1.0
        if day.holiday: 
            base_target_factor *= day.holiday.target_factor
        if base_target_factor == 0.0: continue
        
        # Determine relevant contract for the specific date
        relevant_contract = None
        if len(contracts) == 1: 
            relevant_contract = contracts[0]
        else:
            for contract in contracts:
                start_ok = (contract.valid_start is None) or (contract.valid_start <= day.date)
                stop_ok = (contract.valid_stop is None) or (day.date <= contract.valid_stop)
                if start_ok and stop_ok:
                    relevant_contract = contract
                    break
        
        if relevant_contract:
            spread = relevant_contract.target_spread
            day_target = relevant_contract.weekly_target * (spread[day.weekday] / sum(spread))
            target_sum += day_target * base_target_factor
    
    return target_sum, actual_sum

def get_employee_month_view(db: Session, emp_id: str, year: int, month: int) -> Dict:
    days = (
        db.query(
            CalendarDay
        ).options(
            joinedload(CalendarDay.holiday)
        ).filter(
            extract('year', CalendarDay.date) == year,
            extract('month', CalendarDay.date) == month
        ).order_by(
            CalendarDay.date
        ).all()
    )
    
    logs = (
        db.query(
            LogDailySummary
        ).options(
            joinedload(LogDailySummary.project_hours), 
            joinedload(LogDailySummary.timeframes)
        ).filter(
            LogDailySummary.employee_id == emp_id,
            extract('year',  LogDailySummary.date) == year,
            extract('month', LogDailySummary.date) == month
        ).all()
    )

    log_map = {l.date: l for l in logs}
    first_day = date(year, month, 1)
    
    contract = (
        db.query(
            EmployeeHourTarget
        ).filter(
            EmployeeHourTarget.employee_id == emp_id,
            (EmployeeHourTarget.valid_start <= first_day) | (EmployeeHourTarget.valid_start == None),
            (EmployeeHourTarget.valid_stop >= first_day)  | (EmployeeHourTarget.valid_stop == None)
        ).first()
    )

    day_list = []
    for day in days:
        log = log_map.get(day.date)        
        if log:
            tgt = log.target_hours
        elif day.is_weekend:
            tgt = 0.0
        elif day.holiday and contract:
            tgt = contract.weekly_target * day.holiday.target_factor
        elif contract:
            spread = contract.target_spread
            tgt = contract.weekly_target * (spread[day.date.weekday()] / sum(spread))
        else:
            tgt = 0.0
        
        day_template = {
            "id": 0,
            "date": day.date,
            "meta": jsonable_encoder(day),
            "employee_id": emp_id,
            "status": "A",
            "status_target_factor": 0.0 if day.is_weekend else 1.0,
            "note": None,
            "target_hours": tgt,
            "total_hours": 0.0,
            "project_hours": [],
            "timeframes": []
        }
        if log:
            day_template["id"] = log.id
            day_template["status"] = log.status
            day_template["status_target_factor"] = log.status_target_factor
            day_template["note"] = log.general_note
            day_template["total_hours"] = sum(p.time for p in log.project_hours)
            day_template["project_hours"] = log.project_hours
            day_template["timeframes"] = jsonable_encoder(log.timeframes)
        day_list.append(day_template)
    
    lt_target, lt_actual = get_employee_lifetime_stats(db, emp_id, first_day)

    return {
        "meta": {
            "lt_target": round(lt_target, 2),
            "lt_actual": round(lt_actual, 2),
            "lt_overtime": round(lt_actual - lt_target, 2)
        },
        "days": day_list
    }

def get_employee_year_view(db: Session, emp_id: str, year: int) -> Dict:
    results = (
        db.query(
            CalendarDay
        ).outerjoin(
            LogDailySummary,
            (LogDailySummary.date == CalendarDay.date) & (LogDailySummary.employee_id == emp_id)
        ).options(
            joinedload(CalendarDay.holiday),
            contains_eager(CalendarDay.daily_logs)
        ).filter(
            extract('year', CalendarDay.date) == year
        ).order_by(
            CalendarDay.date
        ).all()
    )
    return {
        str(day.date): {
            "status": day.daily_logs[0].status if day.daily_logs else ("W" if day.is_weekend else "A"),
            "is_holiday": day.holiday is not None,
            "holiday_name": day.holiday.name if day.holiday else None
        }
        for day in results
    }

def get_dashboard(db: Session, emp_id: str, calc_end: Optional[date] = None) -> Dict:
    emp = db.query(Employee).filter(Employee.id == emp_id).first()
    if not emp: return {"meta": {"total": 0}, "pros": {}}

    calc_start = emp.start_tracking_date
    if calc_end is None: calc_end = date.today()

    logs = (
        db.query(LogDailySummary)
        .options(joinedload(LogDailySummary.project_hours))
        .filter(
            LogDailySummary.employee_id == emp_id,
            LogDailySummary.date >= calc_start,
            LogDailySummary.date < calc_end
        )
        .all()
    )

    pcm = defaultdict(lambda: {"phases": defaultdict(float), "total": 0, "color": "#cccccc"})
    total_worktime = 0.0

    for log in logs:
        for p_log in log.project_hours:
            pcm[p_log.project_id]["phases"][p_log.phase_id] += p_log.time
            total_worktime += p_log.time

    pro_colors = {p.id: p.color for p in db.query(Project.id, Project.color).filter(Project.id.in_(pcm.keys())).all()}

    for p_id, data in pcm.items():
        if p_id in pro_colors and pro_colors[p_id]:
            data["color"] = pro_colors[p_id]
        data["total"] = sum(data["phases"].values())

    return {
        "meta": {"total": round(total_worktime, 2)},
        "pros": dict(sorted(pcm.items()))
    }