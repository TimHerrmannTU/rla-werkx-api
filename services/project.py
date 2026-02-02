from datetime import date, timedelta
from typing import Optional, List, Dict, Generator
from collections import defaultdict
from sqlalchemy.orm import Session
from sqlalchemy import func

from models.employee import Employee
from models.project import Project
from models.log import LogProjectHour, LogDailySummary

####################
# HELPER FUNCTIONS #
####################

def _date_range_generator(start_date: date, end_date: date) -> Generator[date, None, None]:
    curr_date = start_date
    while curr_date <= end_date:
        yield curr_date
        curr_date += timedelta(days=1)

def _inject_stats(items: List, stats_map: Dict):
    for item in items:
        stat = stats_map.get(item.id, {"total": 0.0, "emps": {}})
        item.total_hours = round(stat["total"], 2)
        # Sort employees by hours descending
        item.hours_per_emp = dict(sorted(
            {k: round(v, 2) for k, v in stat["emps"].items()}.items(),
            key=lambda x: x[1],
            reverse=True
        ))

############
# SERVICES #
############

def get_dashboard(db: Session, project_id: str) -> Optional[Project]:
    pro = db.query(Project).filter(Project.id == project_id).first()
    if not pro: return None

    # Aggregate hours by Phase, Flag, Date, and Employee
    stats = (
        db.query(
            LogProjectHour.phase_id,
            LogProjectHour.flag_id,
            LogDailySummary.date,
            LogDailySummary.employee_id,
            func.sum(LogProjectHour.time)
        ).join(
            LogDailySummary, 
            LogProjectHour.daily_entry_id == LogDailySummary.id
        ).filter(
            LogProjectHour.project_id == project_id
        ).group_by(
            LogProjectHour.phase_id, 
            LogProjectHour.flag_id,
            LogDailySummary.date,
            LogDailySummary.employee_id,
        ).all()
    )

    unique_emp_ids = {row.employee_id for row in stats if row.employee_id}
    emp_rows = db.query(Employee.id, Employee.name).filter(Employee.id.in_(unique_emp_ids)).all()
    pro.emp_map = {e.id: e.name for e in emp_rows}

    phase_stats = defaultdict(lambda: {"total": 0.0, "emps": defaultdict(float)})
    flag_stats  = defaultdict(lambda: {"total": 0.0, "emps": defaultdict(float)})
    
    pro.total_hours = 0.0
    pro.hours_per_emp = defaultdict(float)
    pro.timeline = defaultdict(float)

    if stats:
        entry_dates = sorted({row.date for row in stats})
        if entry_dates: # Initialize timeline with zeros for the full range
            for d in _date_range_generator(entry_dates[0], entry_dates[-1]):
                pro.timeline[d] = 0.0

    for phase_id, flag_id, d, emp_id, hours in stats:
        h = float(hours or 0)
        
        pro.total_hours += h
        pro.hours_per_emp[emp_id] += h
        pro.timeline[d] += h
        
        if phase_id:
            phase_stats[phase_id]["total"] += h
            phase_stats[phase_id]["emps"][emp_id] += h

        if flag_id:
            flag_stats[flag_id]["total"] += h
            flag_stats[flag_id]["emps"][emp_id] += h

    _inject_stats(pro.phases, phase_stats)
    _inject_stats(pro.flags, flag_stats)

    # Final formatting and rounding
    pro.total_hours = round(pro.total_hours, 2)
    pro.hours_per_emp = dict(sorted(
        {k: round(v, 2) for k, v in pro.hours_per_emp.items()}.items(), 
        key=lambda x: x[1], 
        reverse=True
    ))
    pro.timeline = {k: round(v, 2) for k, v in pro.timeline.items()}

    return pro