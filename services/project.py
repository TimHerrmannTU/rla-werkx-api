from sqlalchemy.orm import Session
from sqlalchemy import func
from collections import defaultdict

from models.project import Project, ProjectPhase
from models.log import LogProjectHour, LogDailySummary

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
                LogDailySummary.employee_id,
                func.sum(LogProjectHour.time)
            )
            .join(LogDailySummary, LogProjectHour.daily_entry_id == LogDailySummary.id)
            .filter(LogProjectHour.project_id == project_id)
            .group_by(LogProjectHour.phase_id, LogProjectHour.flag_id, LogDailySummary.employee_id)
            .all()
        )

        # Calculate Totals
        phase_stats = defaultdict(lambda: {"total": 0.0, "emps": defaultdict(float)})
        flag_stats  = defaultdict(lambda: {"total": 0.0, "emps": defaultdict(float)})
        
        pro.total_hours = 0.0
        pro.hours_per_emp = defaultdict(float)

        for phase_id, flag_id, emp_id, hours in stats:
            h = float(hours or 0)
            
            # Project Totals
            pro.total_hours += h
            pro.hours_per_emp[emp_id] += h
            
            # Phase Totals
            if phase_id:
                phase_stats[phase_id]["total"] += h
                phase_stats[phase_id]["emps"][emp_id] += h

            if flag_id:
                flag_stats[flag_id]["total"] += h
                flag_stats[flag_id]["emps"][emp_id] += h

        # Inject into Phase Objects (Monkey Patching)
        for phase in pro.phases:
            stat = phase_stats.get(phase.id, {"total": 0.0, "emps": {}})
            phase.total_hours = round(stat["total"], 2)
            phase.hours_per_emp = {k: round(v, 2) for k, v in stat["emps"].items()}
        for flag in pro.flags:
            stat = flag_stats.get(flag.id, {"total": 0.0, "emps": {}})
            flag.total_hours = round(stat["total"], 2)
            flag.hours_per_emp = {k: round(v, 2) for k, v in stat["emps"].items()}

        pro.total_hours = round(pro.total_hours, 2)
        pro.hours_per_emp = {k: round(v, 2) for k, v in pro.hours_per_emp.items()}

        return pro