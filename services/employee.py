from calendar import monthrange
from datetime import date
from collections import defaultdict
from typing import Optional, Tuple, Dict

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session, joinedload

from models.project import Project
from models.employee import Employee, EmployeeHourTarget, EmployeeVacationClaim
from models.config import VacationRule

from crud.log import get_employee_logs, get_employee_logs_within_range
from crud.calendar import get_calendar_days, get_calendar_days_within_range
from crud.employee import employee_crud

def get_employee_detailed(db: Session, emp_id: str) -> Optional[Employee]:
    emp = employee_crud.get_with_details(db, emp_id)
    if not emp: return None # gate
    
    first_year = emp.first_work_year
    current_year = date.today().year
    year_lut = {claim.year for claim in list(emp.vacation_claims)}
    final_claims = list(emp.vacation_claims)

    # Calculate missing vacation claims based on seniority rules
    for year in range(first_year, current_year + 1):
        if year not in year_lut:
            seniority = year - first_year
            rule = (
                db.query(
                    VacationRule
                ).filter(
                    VacationRule.min_years <= seniority,
                    VacationRule.max_years >= seniority
                ).first()
            )

            final_claims.append(EmployeeVacationClaim(
                year=year,
                days=rule.days if rule else 0.0
            ))

    emp.vacation_claims = final_claims
    return emp

def get_employee_lifetime_stats(db: Session, emp_id: str, calc_end: Optional[date] = None) -> Tuple[float, float]:
    
    emp = employee_crud.get_with_details(db, emp_id)
    if not emp: return 0.0, 0.0
    
    contracts = emp.hour_targets
    
    calc_start = emp.start_tracking_date
    if calc_end is None: calc_end = date.today()

    days = get_calendar_days_within_range(db, calc_start, calc_end)
    logs = get_employee_logs_within_range(db, emp_id, calc_start, calc_end)
    
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
    days = get_calendar_days(db, year, month)
    logs = get_employee_logs(db, emp_id, year, month)

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

    for day in days: # pre-populate missing logs with empty data
        log = log_map.get(day.date)  
        if not log:
            tgt = 0.0 # weekend or free
            if day.holiday and contract:
                tgt = contract.weekly_target * day.holiday.target_factor
            elif contract:
                spread = contract.target_spread
                tgt = contract.weekly_target * (spread[day.date.weekday()] / sum(spread))
            
            log_map[day.date] = {
                "id": -1,
                "status": "A",
                "status_target_factor": 1.0,
                "status_note": "",
                "target_hours": tgt,
                "general_note": "",
                "project_hours": [],
                "timeframes": [],
            }
    
    lt_target, lt_actual = get_employee_lifetime_stats(db, emp_id, first_day)

    return {
        "meta": {
            "lt_target": round(lt_target, 2),
            "lt_actual": round(lt_actual, 2),
            "lt_overtime": round(lt_actual - lt_target, 2)
        },
        "days": {
            str(day.date): {
                "meta": jsonable_encoder(day),
                "log": log_map.get(day.date)
            } for day in days
        }
    }

def get_employee_year_view(db: Session, emp_id: str, year: int) -> Dict:
    days = get_calendar_days(db, year)
    logs = get_employee_logs(db, emp_id, year)
    
    log_map = {l.date: l for l in logs}
    
    return {
        "days": {
            str(day.date): {
                "status": log_map[day.date].status if day.date in log_map else "A",
                "status_target_factor": log_map[day.date].status_target_factor if day.date in log_map else 1,
                "is_weekend": day.is_weekend is not None,
                "holiday": day.holiday
            } for day in days if (
                day.date in log_map and 
                log_map[day.date].status != "A" or 
                day.holiday
            ) 
        }
    }

def get_dashboard(db: Session, emp_id: str, calc_end: Optional[date] = None) -> Dict:
    emp = employee_crud.get(db, emp_id)
    if not emp: return {"meta": {"total": 0}, "pros": {}}

    calc_start = emp.start_tracking_date
    if calc_end is None: calc_end = date.today()

    logs = get_employee_logs_within_range(db, emp_id, calc_start, calc_end)

    pcm = defaultdict(lambda: {"phases": defaultdict(float), "total": 0, "color": "#cccccc"}) # project color map ?
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