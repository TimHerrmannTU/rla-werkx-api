from datetime import date
from collections import defaultdict
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func

from src.modules.log.model import LogDailySummary, LogProjectHour
from src.modules.project.crud.project import project_crud

class GetDashboardTeam:
    """
    Service to compile aggregated project and phase dashboard statistics 
    for a team of employees over a given timeframe.
    """

    def __init__(
        self,
        db: Session,
        emp_ids: List[str],
        start_date: date,
        end_date: date,
        include_internal: bool = True
    ):
        self.db = db
        self.emp_ids = emp_ids
        self.start_date = start_date
        self.end_date = end_date
        self.include_internal = include_internal
        
        # Structure matching GetEmployeeDashboard: project_id -> {"phases": {phase_id: hours}, "total": total, "color": color}
        self.pcm = defaultdict(lambda: {"phases": defaultdict(float), "total": 0, "color": "#cccccc"})

    def execute(self) -> Dict[str, Any]:
        """
        Orchestrates query execution and aggregates the team dashboard data.
        """
        # Defensive guard for empty team selection
        if not self.emp_ids:
            return {
                "meta": {"total": 0.0},
                "pros": {}
            }

        total_worktime = self._aggregate_project_hours()
        self._apply_project_metadata()

        return {
            "meta": {"total": round(total_worktime, 2)},
            "pros": dict(sorted(self.pcm.items()))
        }

    def _aggregate_project_hours(self) -> float:
        """
        Queries the database for total hours per project/phase in bulk for the active team.
        """
        query = self.db.query(
            LogProjectHour.project_id,
            LogProjectHour.phase_id,
            func.sum(LogProjectHour.time)
        ).join(LogDailySummary)

        # Apply scoping filters
        query = query.filter(
            LogDailySummary.employee_id.in_(self.emp_ids),
            LogDailySummary.date >= self.start_date,
            LogDailySummary.date <= self.end_date
        )

        # Conditionally filter internal projects if requested
        if not self.include_internal:
            query = query.filter(
                LogProjectHour.project_id.notlike("AA%"),
                LogProjectHour.project_id.notlike("WB%")
            )

        results = query.group_by(LogProjectHour.project_id, LogProjectHour.phase_id).all()

        total_worktime = 0.0
        for p_id, phase_id, time_sum in results:
            hours = float(time_sum) if time_sum else 0.0
            self.pcm[p_id]["phases"][phase_id] = hours
            total_worktime += hours

        return total_worktime

    def _apply_project_metadata(self):
        """
        Applies project-specific metadata (colors) from the project CRUD.
        """
        if not self.pcm:
            return

        db_project_colors = project_crud.get_colors(self.db, self.pcm.keys())
        pro_colors = {p.id: p.color for p in db_project_colors}

        for p_id, data in self.pcm.items():
            if p_id in pro_colors and pro_colors[p_id]:
                data["color"] = pro_colors[p_id]
            data["total"] = sum(data["phases"].values())
    """
    Service to compile team-specific dashboard statistics.
    """

    def __init__(
        self,
        db: Session,
        emp_ids: List[str],
        start_date: date,
        end_date: date,
        include_internal: bool = True,
        interval: str = "month"
    ):
        self.db = db
        self.emp_ids = emp_ids
        self.start_date = start_date
        self.end_date = end_date
        self.include_internal = include_internal
        self.interval = interval

    def execute(self) -> Dict[str, Any]:
        """
        Orchestrates the retrieval and assembly of the team dashboard.
        """
        # Defensive guard for empty team selection
        if not self.emp_ids:
            return self._empty_response()

        # TODO: Implement your updated team metrics and queries here!
        return self._empty_response()

    def _empty_response(self) -> Dict[str, Any]:
        """
        Returns a default empty structure when employee list is empty.
        """
        return {
            "top_pros": [],
            "total_worked_company": {
                "total": 0,
                "avg_per_timeframe": 0,
                "per_timeframe": {},
                "mode": self.interval
            },
            "top_ten_pro_history": {
                "labels": [],
                "datasets": []
            },
            "phase_distribution": [],
            "pro_meta": {}
        }