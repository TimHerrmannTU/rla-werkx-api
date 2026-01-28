from sqlalchemy.orm import Session
from sqlalchemy import func
from collections import defaultdict

from models.employee import Employee
from models.project import Project, ProjectPhase
from models.log import LogProjectHour, LogDailySummary

from datetime import timedelta
from itertools import batched

class ProjectService:
    def __init__(self, db: Session):
        self.db = db

    def get_project_statistics(self, project_id: str):
        # Fetch Base Project
        pro = self.db.query(Project).filter(Project.id == project_id).first()
        if not pro: return None

        # Aggregation Query
        # Sum hours grouped by Phase and Employee
        stats = (
            self.db.query(
                LogProjectHour.phase_id,
                LogProjectHour.flag_id,
                LogDailySummary.date,
                LogDailySummary.employee_id,
                func.sum(LogProjectHour.time)
            )
            .join(
                LogDailySummary, 
                LogProjectHour.daily_entry_id == LogDailySummary.id
            )
            .filter(LogProjectHour.project_id == project_id)
            .group_by(
                LogProjectHour.phase_id, 
                LogProjectHour.flag_id,
                LogDailySummary.date,
                LogDailySummary.employee_id,
            )
            .all()
        )

        # add emp map to payload
        unique_emp_ids = {row.employee_id for row in stats if row.employee_id}
        emp_rows = (
            self.db.query(Employee.id, Employee.name)
            .filter(Employee.id.in_(unique_emp_ids))
            .all()
        )
        pro.emp_map = {e.id: e.name for e in emp_rows}

        # Calculate Totals
        phase_stats = defaultdict(lambda: {"total": 0.0, "emps": defaultdict(float)})
        flag_stats  = defaultdict(lambda: {"total": 0.0, "emps": defaultdict(float)})
        
        pro.total_hours = 0.0
        pro.hours_per_emp = defaultdict(float)
        pro.timeline = defaultdict(float)
        if stats:
            entry_dates = sorted({row[2] for row in stats})
            if entry_dates:
                date_range = date_range_list(entry_dates[0], entry_dates[-1])
                for date in date_range:
                    pro.timeline[date] = 0

        for phase_id, flag_id, date, emp_id, hours in stats:
            h = float(hours or 0)
            
            # Project Totals
            pro.total_hours += h
            pro.hours_per_emp[emp_id] += h
            pro.timeline[date] += h
            
            # Phase Totals
            if phase_id:
                phase_stats[phase_id]["total"] += h
                phase_stats[phase_id]["emps"][emp_id] += h

            if flag_id:
                flag_stats[flag_id]["total"] += h
                flag_stats[flag_id]["emps"][emp_id] += h

        inject_stats(pro.phases, phase_stats)
        inject_stats(pro.flags, flag_stats)

        # rounding
        pro.total_hours = round(pro.total_hours, 2)
        pro.hours_per_emp = {k: round(v, 2) for k, v in pro.hours_per_emp.items()}
        pro.hours_per_emp = dict(sorted(pro.hours_per_emp.items(), key=lambda x: x[1], reverse=True))
        pro.timeline = {k: round(v, 2) for k, v in pro.timeline.items()}

        return pro
    
####################
# helper functions #
####################
def inject_stats(items, stats_map):
    # Inject into Phase Objects (Monkey Patching)
    for item in items:
        stat = stats_map.get(item.id, {"total": 0.0, "emps": {}})
        item.total_hours = round(stat["total"], 2)
        item.hours_per_emp = {k: round(v, 2) for k, v in stat["emps"].items()}
        item.hours_per_emp = dict(sorted(item.hours_per_emp.items(), key=lambda x: x[1], reverse=True))

def date_range_list(start_date, end_date):
    # Return generator for a list datetime.date objects (inclusive) between start_date and end_date (inclusive).
    curr_date = start_date
    while curr_date <= end_date:
        yield curr_date 
        curr_date += timedelta(days=1)