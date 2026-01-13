from sqlalchemy.orm import Session
from sqlalchemy import func
from collections import defaultdict

from models.project import Project
from models.phase import Phase
from models.time_entry import TimeEntry

class ProjectService:
    def __init__(self, db: Session):
        self.db = db

    def get_project_hours(self, project_id: str):
        # Fetch Base Project
        pro = self.db.query(Project).filter(Project.id == project_id).first()
        if not pro: return None # gate

        # Fetch Aggregated Hours (Grouped by Phase AND Employee)
        stats = (
            self.db.query(
                TimeEntry.phase_id,
                TimeEntry.emp_id,
                func.sum(TimeEntry.hours)
            )
            .join(Phase, Phase.id == TimeEntry.phase_id)
            .filter(Phase.parent_id == project_id)
            .group_by(TimeEntry.phase_id, TimeEntry.emp_id)
            .all()
        )

        # Aggregate Stats
        phase_stats = defaultdict(lambda: {"total": 0.0, "emps": defaultdict(float)})
        
        # Project Totals
        pro.total_hours = 0.0
        pro.hours_per_emp = defaultdict(float)

        for phase_id, emp_id, hours in stats:
            h = float(hours or 0)
            # Phase Calc
            phase_stats[phase_id]["total"] += h
            phase_stats[phase_id]["emps"][emp_id] += h
            # Project Calc
            pro.total_hours += h
            pro.hours_per_emp[emp_id] += h

        # Stats to Phases
        for phase in pro.phases:
            stat = phase_stats[phase.id]
            phase.total_hours = round(stat["total"], 2)
            phase.hours_per_emp = {k: round(v, 2) for k, v in stat["emps"].items()}

        pro.total_hours = round(pro.total_hours, 2)
        pro.hours_per_emp = dict(pro.hours_per_emp)
        pro.hours_per_emp = {k: round(v, 2) for k, v in pro.hours_per_emp.items()}

        return pro