from datetime import date, timedelta
from typing import Dict, Any, List, Optional, Tuple
from collections import defaultdict
from sqlalchemy.orm import Session
from sqlalchemy import func

from models.project import Project, ProjectPhase
from models.log import LogDailySummary, LogProjectHour
from crud.project import project_crud


class GetDashboardGeneral:

    def __init__(
        self,
        db: Session,
        start_date: date,
        end_date: date,
        emp_ids: Optional[List[str]] = None,
        include_internal: bool = False,
        interval: str = "month"
    ):
        self.db = db
        self.start_date = start_date
        self.end_date = end_date
        self.emp_ids = emp_ids
        self.include_internal = include_internal
        self.interval = interval
        
        # Determine the date grouping and format based on the selected interval
        self.date_format = '%Y-%m' if self.interval == "month" else '%x-%v'
        self.date_to_key = func.date_format(LogDailySummary.date, self.date_format)

    @classmethod
    def get_general(
        cls,
        db: Session, 
        start_date: date, 
        end_date: date, 
        include_internal: bool = False,
        interval: str = "month"
    ) -> Dict[str, Any]:
        """
        Retrieves general dashboard data without employee-specific filters.
        """
        instance = cls(
            db=db,
            start_date=start_date,
            end_date=end_date,
            emp_ids=None,
            include_internal=include_internal,
            interval=interval
        )
        return instance.execute()

    @classmethod
    def get_team_stats(
        cls,
        db: Session, 
        emp_ids: List[str],
        start_date: date, 
        end_date: date, 
        include_internal: bool = True,
        interval: str = "month"
    ) -> Dict[str, Any]:
        """
        Retrieves dashboard data filtered by team employee IDs.
        """
        if not emp_ids:
            return cls._empty_response(interval)

        instance = cls(
            db=db,
            start_date=start_date,
            end_date=end_date,
            emp_ids=emp_ids,
            include_internal=include_internal,
            interval=interval
        )
        return instance.execute()

    @staticmethod
    def _empty_response(interval: str) -> Dict[str, Any]:
        """
        Returns a default empty structure when employee list is empty.
        """
        return {
            "top_pros": [],
            "total_worked_company": {
                "total": 0,
                "avg_per_timeframe": 0,
                "per_timeframe": {},
                "mode": interval
            },
            "top_ten_pro_history": {
                "labels": [],
                "datasets": []
            },
            "phase_distribution": [],
            "pro_meta": {}
        }

    def _apply_scope(self, query, start: date, end: date):
        """
        Applies date range, team, and internal filters to the provided query.
        """
        q = query.filter(
            LogDailySummary.date >= start, 
            LogDailySummary.date <= end
        )
        
        if self.emp_ids is not None:
            q = q.filter(LogDailySummary.employee_id.in_(self.emp_ids))
            
        if not self.include_internal:
            q = q.filter(
                LogProjectHour.project_id.notlike("AA%"),
                LogProjectHour.project_id.notlike("WB%")
            )
        return q

    def _fetch_totals(self, start: date, end: date) -> Dict[str, float]:
        """
        Fetches the total hours worked per project within the timeframe.
        """
        query = self.db.query(
            LogProjectHour.project_id, 
            func.sum(LogProjectHour.time)
        ).join(LogDailySummary)
        
        results = self._apply_scope(query, start, end).group_by(LogProjectHour.project_id).all()
        return {pid: float(hours) for pid, hours in results}

    def _get_top_projects(
        self, 
        current_data: Dict[str, float], 
        previous_data: Dict[str, float]
    ) -> Tuple[List[str], List[Dict[str, Any]]]:
        """
        Computes the top 10 projects by current hours worked and includes progress trends.
        """
        sorted_pids = sorted(current_data.keys(), key=lambda k: current_data[k], reverse=True)[:10]
        
        final_pros = []
        for pid in sorted_pids:
            curr_h = current_data[pid]
            prev_h = previous_data.get(pid, 0.0)
            diff = curr_h - prev_h
            pct = ((diff / prev_h) * 100) if prev_h > 0 else (100.0 if curr_h > 0 else 0.0)
            
            final_pros.append({
                "id": pid,
                "hours": round(curr_h, 2),
                "trend_abs": round(diff, 2),
                "trend_pct": round(pct, 1)
            })
            
        return sorted_pids, final_pros

    def _get_total_worked_company(self) -> Dict[str, Any]:
        """
        Retrieves work totals and historical trends across time frames.
        """
        query = self.db.query(
            self.date_to_key, 
            func.sum(LogProjectHour.time)
        ).join(LogDailySummary)

        monthly_totals_query = self._apply_scope(
            query, 
            self.start_date, 
            self.end_date
        ).group_by(self.date_to_key).all()

        total_worked = round(sum(hours for _, hours in monthly_totals_query))
        return {
            "total": total_worked,
            "avg_per_timeframe": round(total_worked / len(monthly_totals_query)) if monthly_totals_query else 0,
            "per_timeframe": {month: round(hours) for month, hours in monthly_totals_query},
            "mode": self.interval
        }

    def _get_top_ten_history(self, sorted_pids: List[str]) -> Dict[str, Any]:
        """
        Compiles the historical breakdown for the top 10 projects.
        """
        query = self.db.query(
            LogProjectHour.project_id, 
            self.date_to_key, 
            func.sum(LogProjectHour.time)
        ).join(LogDailySummary)

        monthly_project_sums = self._apply_scope(
            query, 
            self.start_date, 
            self.end_date
        ).filter(
            LogProjectHour.project_id.in_(sorted_pids)
        ).group_by(
            LogProjectHour.project_id, 
            self.date_to_key
        ).order_by(
            self.date_to_key
        ).all()

        all_months = sorted(list({month for _, month, _ in monthly_project_sums}))
        history_map = defaultdict(dict)
        for pid, month, hours in monthly_project_sums:
            history_map[pid][month] = float(hours)

        datasets = []
        for pid in sorted_pids:
            datasets.append({
                "name": pid,
                "data": [round(history_map[pid].get(m, 0.0), 2) for m in all_months]
            })

        return {
            "labels": all_months,
            "datasets": datasets
        }

    def _get_phase_distribution(self) -> List[Dict[str, Any]]:
        """
        Retrieves the phase distribution details.
        """
        phase_query = self._apply_scope(
            self.db.query(
                ProjectPhase.phase, 
                func.sum(LogProjectHour.time)
            ).join(
                LogProjectHour, 
                LogProjectHour.phase_id == ProjectPhase.id
            ).join(
                LogDailySummary
            ), self.start_date, self.end_date
        ).group_by(
            ProjectPhase.phase
        ).order_by(
            ProjectPhase.phase
        ).all()

        return [
            {"phase": p_num, "hours": round(h)} for p_num, h in phase_query
        ]

    def _get_project_metadata(self, sorted_pids: List[str]) -> Dict[str, Dict[str, str]]:
        """
        Fetches naming and coloring metadata for top projects.
        """
        pro_colors = project_crud.get_colors(self.db, sorted_pids)
        return {
            pid: {"color": color, "name": name} for pid, name, color in pro_colors
        }

    def execute(self) -> Dict[str, Any]:
        """
        Orchestrates the retrieval and assembly of the full dashboard.
        """
        duration = (self.end_date - self.start_date).days + 1
        current_data = self._fetch_totals(self.start_date, self.end_date)
        previous_data = self._fetch_totals(
            self.start_date - timedelta(days=duration), 
            self.start_date - timedelta(days=1)
        )

        sorted_pids, top_pros = self._get_top_projects(current_data, previous_data)

        return {
            "top_pros": top_pros,
            "total_worked_company": self._get_total_worked_company(),
            "top_ten_pro_history": self._get_top_ten_history(sorted_pids),
            "phase_distribution": self._get_phase_distribution(),
            "pro_meta": self._get_project_metadata(sorted_pids)
        }