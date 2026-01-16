from sqlalchemy.orm import Session
from sqlalchemy import func
from collections import defaultdict

from models.project import Project, ProjectPhase
from models.log import LogProjectHour, LogDailySummary

class ProjectService:
    def __init__(self, db: Session):
        self.db = db

    def get_project_hours(self, project_id: str):
        # 1. Fetch Base Project (With Phases eager loaded)
        pro = self.db.query(Project).filter(Project.id == project_id).first()
        if not pro: return None

        # 2. Fetch Aggregated Hours (Bottom-Up: Log -> Phase)
        # We query the new 'log_project_hours' table
        stats = (
            self.db.query(
                LogProjectHour.phase_id,
                LogDailySummary.employee_id, # Need to join parent log for emp_id
                func.sum(LogProjectHour.time)
            )
            .join(LogDailySummary, LogProjectHour.daily_entry_id == LogDailySummary.id)
            .join(ProjectPhase, ProjectPhase.id == LogProjectHour.phase_id)
            .filter(ProjectPhase.project_id == project_id) # Use project_id from ProjectPhase
            .group_by(LogProjectHour.phase_id, LogDailySummary.employee_id)
            .all()
        )

        # 3. Aggregate
        phase_stats = defaultdict(lambda: {"total": 0.0, "emps": defaultdict(float)})
        
        pro.total_hours = 0.0
        pro.hours_per_emp = defaultdict(float)

        for phase_id, emp_id, hours in stats:
            h = float(hours or 0)
            
            # Skip if phase_id is None (Direct project booking? Handle separate if needed)
            if not phase_id: continue

            phase_stats[phase_id]["total"] += h
            phase_stats[phase_id]["emps"][emp_id] += h
            
            pro.total_hours += h
            pro.hours_per_emp[emp_id] += h

        # 4. Inject Stats into Phases
        for phase in pro.phases:
            stat = phase_stats[phase.id]
            phase.total_hours = round(stat["total"], 2)
            phase.hours_per_emp = {k: round(v, 2) for k, v in stat["emps"].items()}

        pro.total_hours = round(pro.total_hours, 2)
        pro.hours_per_emp = {k: round(v, 2) for k, v in pro.hours_per_emp.items()}

        return pro