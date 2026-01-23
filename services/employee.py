import calendar
from datetime import date

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import extract
from models.log import LogDailySummary
from models.calendar import CalendarDay

from models.employee import Employee, EmployeeHourTarget, EmployeeVacationClaim
from models.config import VacationRule

class EmployeeService:
    def __init__(self, db: Session):
        self.db = db

    def get_detailed(self, emp_id: str):
        emp = self.db.query(Employee).options(
            joinedload(Employee.hour_targets),
            joinedload(Employee.vacation_claims)
        ).filter(Employee.id == emp_id).first()
        
        if not emp: return None # gate
        
        first_year = emp.first_work_year
        current_year = date.today().year

        year_lut = [claim.year for claim in emp.vacation_claims]
        final_claims = emp.vacation_claims or []

        for year in range(first_year, current_year + 1):
            if year not in year_lut:
                seniority = year - first_year
                rule = self.db.query(VacationRule).filter(
                    VacationRule.min_years <= seniority,
                    VacationRule.max_years >= seniority
                ).first()

                days = rule.days if rule else 0.0
                claim_object = EmployeeVacationClaim(
                    year=year,
                    days=days
                )
                final_claims.append(claim_object)

        emp.vacation_claims = final_claims
        return emp

    def get_lifetime_stats(self, emp_id: str, calc_end: date | None = None):
        calc_start = self.db.query(Employee).filter(Employee.id == emp_id).first().start_tracking_date
        if calc_end is None: calc_end = date.today()

        days = self.db.query(CalendarDay).options(
            joinedload(CalendarDay.holiday)
        ).filter(
            CalendarDay.date >= calc_start,
            CalendarDay.date < calc_end
        ).order_by(CalendarDay.date).all()

        contracts = self.db.query(EmployeeHourTarget).filter(
            EmployeeHourTarget.employee_id == emp_id
        ).all()

        # Fetch Logs
        logs = self.db.query(LogDailySummary).options(
            joinedload(LogDailySummary.project_hours),
        ).filter(
            LogDailySummary.employee_id == emp_id,
            LogDailySummary.date >= calc_start,
            LogDailySummary.date < calc_end
        ).all()
        log_map = {l.date: l for l in logs}

        actual_sum = 0.0
        for log in logs: actual_sum += sum(p.time for p in log.project_hours)

        target_sum = 0.0
        for contract in contracts:
            if contract.starting_balance:
                target_sum += contract.starting_balance

        for day in days:
            # pre-calculated target exists? 
            log = log_map.get(day.date)
            if log:
                target_sum += log.target_hours
                continue
            
            if day.is_weekend: 
                continue

            # (half) holiday check
            base_target_factor = 1.0
            if day.holiday: 
                base_target_factor *= day.holiday.target_factor
            if base_target_factor == 0.0:
                continue
            
            # search for relevant contract
            relevant_contract = None
            if len(contracts) == 1: relevant_contract = contracts[0]
            else: # fetch correct contract
                for contract in contracts:
                    start_ok = (contract.valid_start is None) or (contract.valid_start <= day.date)
                    stop_ok  = (contract.valid_stop is None)  or (day.date <= contract.valid_stop)
                    if (start_ok and stop_ok):
                        relevant_contract = contract
                        break
            if relevant_contract is None: 
                print(day.date)
                continue

            # extract relevant contract data
            target_spread = contract.target_spread
            daily_mod = target_spread[day.weekday]
            total_mod = sum(target_spread)

            weekly_target = contract.weekly_target
            day_target = weekly_target = weekly_target * (daily_mod/total_mod)
            
            target_sum += day_target * base_target_factor
        
        return target_sum, actual_sum
                
    def get_month_view(self, emp_id: str, year: int, month: int):
        # Fetch Calendar Range (The Scaffold)
        days = self.db.query(CalendarDay).options(
            joinedload(CalendarDay.holiday)
        ).filter(
            extract('year', CalendarDay.date) == year,
            extract('month', CalendarDay.date) == month
        ).order_by(CalendarDay.date).all()

        # Fetch Logs
        logs = self.db.query(LogDailySummary).options(
            joinedload(LogDailySummary.project_hours),
            joinedload(LogDailySummary.timeframes)
        ).filter(
            LogDailySummary.employee_id == emp_id,
            extract('year', LogDailySummary.date) == year,
            extract('month', LogDailySummary.date) == month
        ).all()

        log_map = {l.date: l for l in logs}

        # Fetch active contract
        first_day_of_month = date(year, month, 1)
        
        contract = self.db.query(EmployeeHourTarget).filter(
            EmployeeHourTarget.employee_id == emp_id,
            (EmployeeHourTarget.valid_start <= first_day_of_month) | (EmployeeHourTarget.valid_start == None),
            (EmployeeHourTarget.valid_stop >= first_day_of_month) | (EmployeeHourTarget.valid_stop == None)
        ).first()
        
        # Merge
        day_list = []
        for day in days:
            log = log_map.get(day.date)

            if log:
                tgt = log.target_hours if log else 0.0
            elif day.is_weekend:
                tgt = 0
            elif day.holiday:
                tgt = contract.weekly_target * day.holiday.target_factor
            else:
                spread = contract.target_spread
                tgt = contract.weekly_target * (spread[day.date.weekday()]/sum(spread)) 
            
            day_list.append({
                # Date Data
                "date": day.date,
                "meta": day,
                
                # General Logging
                "status": log.status if log else "A",
                "status_target_factor": log.status_target_factor if log else (0.0 if day.is_weekend else 1.0),
                "note": log.general_note if log else None,
                
                # Hour Logging
                "target_hours": tgt,
                "total_hours": sum(p.time for p in log.project_hours) if log else 0.0,
                "project_hours": log.project_hours if log else [],
                "timeframes": log.timeframes if log else [],
            })
        
        lt_sum_target, lt_sum_actual = self.get_lifetime_stats(emp_id=emp_id, calc_end=date(year, month, 1))

        return {
            "meta": {
                "lt_target": round(lt_sum_target, 2),
                "lt_actual": round(lt_sum_actual, 2),
                "lt_overtime": round(lt_sum_actual - lt_sum_target, 2)
            },
            "days": day_list
        }