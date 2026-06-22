from datetime import date
from typing import Dict, Any, List
from sqlalchemy.orm import Session

class GetDashboardTeam:
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