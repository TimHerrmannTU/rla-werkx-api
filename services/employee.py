from datetime import date
from collections import defaultdict
from typing import Optional

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session, joinedload

from schemas.calendar import CalendarDayRead
from schemas.employee import EmployeeDetailedView
from schemas.employeeHourTarget import EmployeeHourTargetRead
from schemas.employeeVacationClaim import EmployeeVacationClaimRead
from schemas.log import DailyLogRead

from crud.log import get_employee_logs, get_employee_logs_within_range
from crud.calendar import get_calendar_days, get_calendar_days_within_range
from crud.employee import employee_crud
from crud.employeeHourTarget import hour_contract_crud
from crud.employeeVacationClaim import vacation_contract_crud
from crud.project import project_crud

#########################################
# ENDPOINT /employees/detailed/{emp_id} #
#########################################

def get_employee_detailed(db: Session, emp_id: str) -> Optional[EmployeeDetailedView]:
    emp = employee_crud.get_with_details(db, emp_id)
    if not emp: return None # gate
    
    claim_history = _build_vacation_claim_history(db, emp)
    view = EmployeeDetailedView.model_validate(emp)
    view.vacation_claims = claim_history
    
    return view
    
def _build_vacation_claim_history(db: Session, emp: EmployeeDetailedView) -> list[EmployeeVacationClaimRead]:
        
    vacation_rules = vacation_contract_crud.get_all(db)
    existing_claims = {claim.year: claim for claim in emp.vacation_claims}
    
    first_year = emp.first_work_year
    current_year = date.today().year

    claim_history = [
        existing_claims.get(year) or _generate_virtual_claim(vacation_rules, emp.id, first_year, year)
        for year in range(first_year, current_year + 1)
    ]

    return claim_history

def _generate_virtual_claim(vacation_rules: list[EmployeeVacationClaimRead], emp_id: str, first_year: int, year: int) -> EmployeeVacationClaimRead:
    seniority = year - first_year
    claim_in_days = _get_claim_by_seniority(vacation_rules, seniority)
    return EmployeeVacationClaimRead(
        id=-1,
        employee_id=emp_id,
        year=year,
        days=claim_in_days
    )
    
def _get_claim_by_seniority(rules: list[EmployeeVacationClaimRead], seniority: int) -> float:
    for rule in rules:
        if rule.min_years <= seniority <= rule.max_years:
            return rule.days
    return 0.0

##########################################
# ENDPOINT /logs/{emp_id}/{year}/{month} #
##########################################

def get_employee_month_view(db: Session, emp_id: str, year: int, month: int) -> dict:
    days = get_calendar_days(db, year, month)
    timesheet = _build_timesheet(db, emp_id, year, month)
    
    first_day = date(year, month, 1)
    lt_target, lt_actual = _get_employee_hour_stats(db, emp_id, first_day)

    return {
        "meta": {
            "lt_target": round(lt_target, 2),
            "lt_actual": round(lt_actual, 2),
            "lt_overtime": round(lt_actual - lt_target, 2)
        },
        "days": {
            str(day.date): {
                "meta": jsonable_encoder(day),
                "log": timesheet.get(day.date)
            } for day in days
        }
    }
    
def _build_timesheet(db: Session, emp_id: str, year: int, month: int) -> list:
    
    contract = hour_contract_crud.get_for_month(db, emp_id, year, month)
    
    days = get_calendar_days(db, year, month)
    logs = get_employee_logs(db, emp_id, year, month)
    
    log_map = {l.date: l for l in logs}
    
    timesheet = {
        str(day.date): log_map.get(day.date) or _create_empty_log(day, contract)
        for day in days
    } 
    
    return timesheet 

def _create_empty_log(day: CalendarDayRead, contract: EmployeeHourTargetRead):
    tgt = 0.0 # weekend or free
    if day.holiday and contract:
        tgt = contract.weekly_target * day.holiday.target_factor
    elif contract:
        spread = contract.target_spread
        tgt = contract.weekly_target * (spread[day.date.weekday()] / sum(spread))
    
    return {
        "id": -1,
        "status": "A",
        "status_target_factor": 1.0,
        "status_note": "",
        "target_hours": tgt,
        "general_note": "",
        "project_hours": [],
        "timeframes": [],
    }

def _get_employee_hour_stats(db: Session, emp_id: str, calc_end: Optional[date] = None) -> tuple[float, float]:
    
    emp = employee_crud.get_with_details(db, emp_id)
    if not emp: return 0.0, 0.0
    
    contracts = emp.hour_targets
    
    calc_start = emp.start_tracking_date
    if calc_end is None: calc_end = date.today()

    days = get_calendar_days_within_range(db, calc_start, calc_end)
    logs = get_employee_logs_within_range(db, emp_id, calc_start, calc_end)
    
    log_map = {l.date: l for l in logs}
    
    actual_sum = sum(sum(p.time for p in log.project_hours) for log in logs)
    target_sum = _get_target_sum(days, log_map, contracts)
    
    return target_sum, actual_sum

def _get_target_sum(days: list[CalendarDayRead], log_map: dict[date, DailyLogRead], contracts: list[EmployeeHourTargetRead]) -> float:
    target_sum = sum(c.starting_balance for c in contracts if c.starting_balance)
    for day in days:
        log = log_map.get(day.date)
        if log: 
            target_sum += log.target_hours
        else:
            base_target_factor = _get_target_factor_of_holiday(day)
            if day.is_weekend or base_target_factor == 0.0: continue # GATE
            target_sum += _get_target_from_contract(base_target_factor, day, contracts)
    return target_sum

def _get_target_factor_of_holiday(day: CalendarDayRead) -> float:
    base_target_factor = 1.0
    if day.holiday: 
        base_target_factor *= day.holiday.target_factor
    return base_target_factor

def _get_target_from_contract(base_target_factor: float, day: CalendarDayRead, contracts: list[EmployeeHourTargetRead]) -> float:
    hour_target = 0
    
    relevant_contract = _find_contract_for_date(day.date, contracts)
    if relevant_contract:
        hour_target = _get_hours_from_spread(relevant_contract, day.weekday) * base_target_factor

    return hour_target

def _find_contract_for_date(target_date: date, contracts: list[EmployeeHourTargetRead]) -> EmployeeHourTargetRead | None:
    for contract in contracts:
        is_after_start = (contract.valid_start is None) or (contract.valid_start <= target_date)
        is_before_stop = (contract.valid_stop is None ) or (target_date <= contract.valid_stop)
        if is_after_start and is_before_stop:
            return contract
    return None
    
def _get_hours_from_spread(contract: EmployeeHourTargetRead, weekday: int) -> float:
    spread = contract.target_spread
    spread_sum = sum(spread)
    
    return 0.0 if spread_sum == 0 else contract.weekly_target * (spread[weekday] / spread_sum)
    

##################################
# ENDPOINT /logs/{emp_id}/{year} #
##################################

def get_employee_year_view(db: Session, emp_id: str, year: int) -> dict:
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

#########################################
# ENDPOINT /dashboard/employee/{emp_id} #
#########################################

def get_dashboard(db: Session, emp_id: str, calc_end: Optional[date] = None) -> dict:
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

    db_project_colors = project_crud.get_colors(db, pcm.keys())
    pro_colors = {p.id: p.color for p in db_project_colors}

    for p_id, data in pcm.items():
        if p_id in pro_colors and pro_colors[p_id]:
            data["color"] = pro_colors[p_id]
        data["total"] = sum(data["phases"].values())

    return {
        "meta": {"total": round(total_worktime, 2)},
        "pros": dict(sorted(pcm.items()))
    }