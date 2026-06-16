from datetime import date, timedelta
from typing import Optional, List, Dict, Generator
from collections import defaultdict
from sqlalchemy.orm import Session

from models.employee import Employee
from models.project import Project

from crud.project import project_crud

############################################
# ENDPOINT /dashboard/project/{project_id} #
############################################

class GetProjectDashboard:

    def __init__(self, db):
        self.db = db
        
        self.phase_stats = defaultdict(lambda: {"total": 0.0, "emps": defaultdict(float)})
        self.flag_stats  = defaultdict(lambda: {"total": 0.0, "emps": defaultdict(float)})
        self.emp_totals  = defaultdict(float) 
        self.timeline    = defaultdict(float)
        self.grand_total = 0.0
        
    def execute(self, project_id: str) -> Optional[Project]:
        pro = project_crud.get(self.db, project_id)
        stats = project_crud.get_stats(self.db, project_id)
        if not pro or not stats: return None # GUARD

        unique_emp_ids = {row.employee_id for row in stats if row.employee_id}
        emp_rows = (
            self.db.query(
                Employee.id,
                Employee.name
            ).filter(
                Employee.id.in_(unique_emp_ids)
            ).all()
        )
        pro.emp_map = {e.id: e.name for e in emp_rows}
        
        self._create_empty_timeline(stats)
        self._calculate_aggregates(stats)
        self._inject_stats(pro.phases, self.phase_stats)
        self._inject_stats(pro.flags,  self.flag_stats)

        # Final formatting and rounding
        self.grand_total = round(self.grand_total, 2)
        pro.hours_per_emp = dict(sorted(
            {k: round(v, 2) for k, v in self.emp_totals.items()}.items(), 
            key=lambda x: x[1], 
            reverse=True
        ))
        pro.timeline = {k: round(v, 2) for k, v in self.timeline.items()}

        return pro
    
    def _create_empty_timeline(self, stats):
        entry_dates = sorted({row.date for row in stats})
        if entry_dates: # Initialize timeline with zeros for the full range
            for d in self._date_range_generator(entry_dates[0], entry_dates[-1]):
                self.timeline[d] = 0.0
                
    def _calculate_aggregates(self, stats):
        for phase_id, flag_id, d, emp_id, hours in stats:
            h = float(hours or 0)
            
            self.grand_total += h
            self.emp_totals[emp_id] += h
            self.timeline[d] += h

            if phase_id:
                self.phase_stats[phase_id]["total"] += h
                self.phase_stats[phase_id]["emps"][emp_id] += h

            if flag_id:
                self.flag_stats[flag_id]["total"] += h
                self.flag_stats[flag_id]["emps"][emp_id] += h
    
    def _date_range_generator(self, start_date: date, end_date: date) -> Generator[date, None, None]:
        curr_date = start_date
        while curr_date <= end_date:
            yield curr_date
            curr_date += timedelta(days=1)

    def _inject_stats(self, items: List, stats_map: Dict):
        for item in items:
            stat = stats_map.get(item.id, {"total": 0.0, "emps": {}})
            item.total_hours = round(stat["total"], 2)
            # Sort employees by hours descending
            item.hours_per_emp = dict(sorted(
                {k: round(v, 2) for k, v in stat["emps"].items()}.items(),
                key=lambda x: x[1],
                reverse=True
            ))