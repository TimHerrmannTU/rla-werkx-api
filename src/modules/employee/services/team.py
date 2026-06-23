# src/modules/employee/services/team.py

from datetime import date, timedelta
from collections import defaultdict
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session, joinedload

# Exact imports preserved
from src.modules.log.model import LogDailySummary, LogProjectHour
from src.modules.project.crud.project import project_crud

from src.modules.employee.model import Employee
from src.modules.calender.crud import get_calendar_days_within_range


class GetDashboardTeam:
    """
    Service to compile aggregated project histories (bar charts),
    and employee contribution breakdowns (pie charts) for a team of employees.
    """

    def __init__(
        self,
        db: Session,
        emp_ids: List[str],
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        include_internal: bool = True,
        interval: str = "week"
    ):
        self.db = db
        self.emp_ids = emp_ids
        self.interval = interval
        self.include_internal = include_internal

        # Fallback to a 12-week window if start_date is not provided
        self.end_date = end_date if end_date is not None else date.today()
        if start_date is not None:
            self.start_date = start_date
        else:
            self.start_date = self.end_date - timedelta(weeks=12) + timedelta(days=1)

    def execute(self) -> Dict[str, Any]:
        """
        Orchestrates the bulk queries to build project histories, employee metrics, 
        and target comparisons.
        """
        if not self.emp_ids:
            return self._empty_response()

        # 1. Fetch employees and pre-load their contracts (hour targets) to avoid N+1 queries
        employees = (
            self.db.query(Employee)
            .options(joinedload(Employee.hour_targets))
            .filter(Employee.id.in_(self.emp_ids))
            .all()
        )
        emp_names = {emp.id: emp.name for emp in employees}

        # 2. Fetch all calendar days in the specified range
        calendar_days = get_calendar_days_within_range(self.db, self.start_date, self.end_date)
        if not calendar_days:
            return self._empty_response()

        # 3. Create ISO-week mapping (e.g. '2026-W12') for standard timeline tracking
        day_to_week = {}
        for day in calendar_days:
            iso_year, iso_week, _ = day.date.isocalendar()
            day_to_week[day.date] = f"{iso_year}-W{iso_week:02d}"

        # Chronological weekly bucket labels
        week_keys = sorted(list(set(day_to_week.values())))

        # 4. Fetch actual project hours in bulk
        logs_query = (
            self.db.query(
                LogProjectHour.project_id,
                LogDailySummary.employee_id,
                LogDailySummary.date,
                LogProjectHour.time
            )
            .join(LogDailySummary)
            .filter(
                LogDailySummary.employee_id.in_(self.emp_ids),
                LogDailySummary.date >= self.start_date,
                LogDailySummary.date <= self.end_date
            )
        )

        if not self.include_internal:
            logs_query = logs_query.filter(
                LogProjectHour.project_id.notlike("AA%"),
                LogProjectHour.project_id.notlike("WB%")
            )

        logs_data = logs_query.all()

        # 5. Determine the top 10 projects by total workload in this timeframe
        project_workloads = defaultdict(float)
        for p_id, _, _, time in logs_data:
            project_workloads[p_id] += float(time or 0.0)

        # Sorted in descending order
        sorted_projects = sorted(project_workloads.items(), key=lambda x: x[1], reverse=True)
        top_10_project_ids = {p_id for p_id, _ in sorted_projects[:10]}

        # 6. Process actual hours and contributions
        weekly_project_hours = defaultdict(lambda: defaultdict(float))
        project_employee_hours = defaultdict(lambda: defaultdict(float))
        employee_totals = defaultdict(float)
        weekly_actual_totals = defaultdict(float)
        grand_actual_total = 0.0

        for p_id, emp_id, d, time in logs_data:
            hours = float(time or 0.0)
            week_key = day_to_week.get(d)
            
            # Map tracking parameters
            if week_key:
                weekly_actual_totals[week_key] += hours
            employee_totals[emp_id] += hours
            grand_actual_total += hours

            # Group any project outside the top 10 into "Andere"
            target_project_id = p_id if p_id in top_10_project_ids else "Andere"
            
            if week_key:
                weekly_project_hours[target_project_id][week_key] += hours
            project_employee_hours[target_project_id][emp_id] += hours

        # 7. Fetch logged target hours from the DB
        summary_query = (
            self.db.query(
                LogDailySummary.employee_id,
                LogDailySummary.date,
                LogDailySummary.target_hours
            )
            .filter(
                LogDailySummary.employee_id.in_(self.emp_ids),
                LogDailySummary.date >= self.start_date,
                LogDailySummary.date <= self.end_date
            )
            .all()
        )
        db_targets = {(emp_id, d): float(tgt or 0.0) for emp_id, d, tgt in summary_query}

        # 8. Calculate targets ("how much should everybody have worked")
        weekly_target_totals = defaultdict(float)
        grand_target_total = 0.0

        for emp in employees:
            contracts = emp.hour_targets
            calc_start = emp.start_tracking_date or self.start_date
            
            for day in calendar_days:
                if day.date < calc_start:
                    continue
                    
                week_key = day_to_week[day.date]
                
                # Check DB targets first; fallback to contract rule math if missing
                if (emp.id, day.date) in db_targets:
                    tgt = db_targets[(emp.id, day.date)]
                else:
                    base_target_factor = 1.0
                    if day.holiday:
                        base_target_factor *= float(day.holiday.target_factor or 0.0)
                    
                    if day.is_weekend or base_target_factor == 0.0:
                        tgt = 0.0
                    else:
                        tgt = self._get_target_from_contract(base_target_factor, day, contracts)
                        
                weekly_target_totals[week_key] += tgt
                grand_target_total += tgt

        # 9. Clean, separated datasets for the Bar/Line charts
        project_datasets = []
        # Loop over the sorted projects first to guarantee sorting in descending order of total hours worked
        for p_id, _ in sorted_projects[:10]:
            if p_id in weekly_project_hours:
                week_data = weekly_project_hours[p_id]
                project_datasets.append({
                    "name": p_id,
                    "data": [round(week_data.get(w, 0.0), 2) for w in week_keys]
                })

        # Flat lists mapped to the chronological week_keys
        targets_timeline = [round(weekly_target_totals.get(w, 0.0), 2) for w in week_keys]
        actuals_timeline = [round(weekly_actual_totals.get(w, 0.0), 2) for w in week_keys]

        # 10. Format Pie Chart contribution mappings and retrieve metadata
        project_contributions = {}
        db_project_colors = project_crud.get_colors(self.db, project_employee_hours.keys())
        
        # Build both metadata structures in a single pass to save processing time
        pro_colors = {p.id: p.color for p in db_project_colors}
        pro_meta = {p.id: {"color": p.color, "name": p.name} for p in db_project_colors}

        # Manually append the consolidated "Andere" virtual project metadata
        pro_colors["Andere"] = "#D1D5DB"
        pro_meta["Andere"] = {"color": "#D1D5DB", "name": "Andere"}

        for p_id, emp_hours in project_employee_hours.items():
            project_contributions[p_id] = {
                "total": round(sum(emp_hours.values()), 2),
                "color": pro_colors.get(p_id, "#cccccc"),
                "employees": {
                    emp_names.get(emp_id, emp_id): round(hours, 2)
                    for emp_id, hours in sorted(emp_hours.items(), key=lambda x: x[1], reverse=True)
                }
            }

        team_shares = {
            emp_names.get(emp_id, emp_id): round(hours, 2)
            for emp_id, hours in sorted(employee_totals.items(), key=lambda x: x[1], reverse=True)
        }

        return {
            "team_meta": {
                "total_actual": round(grand_actual_total, 2),
                "total_target": round(grand_target_total, 2),
                "total_overtime": round(grand_actual_total - grand_target_total, 2)
            },
            "project_history": {
                "labels": week_keys,
                "projects": project_datasets, # Standard bar-chart datasets, strictly sorted descending
                "targets": targets_timeline,   # Simple flat array for the line-chart target line [400, 400, 420...]
                "actuals": actuals_timeline    # Simple flat array of total team actual hours [380, 410, 430...]
            },
            "project_totals": project_contributions, # Contribution breakdown per project (Pie/Sunburst Chart support)
            "team_shares": team_shares,              # Overall workload share per employee (Pie Chart support)
            "project_meta": pro_meta                 # Mapping of project IDs to color and name
        }

    def _get_target_from_contract(self, base_target_factor: float, day, contracts) -> float:
        hour_target = 0.0
        relevant_contract = self._find_contract_for_date(day.date, contracts)
        if relevant_contract:
            hour_target = self._get_hours_from_spread(relevant_contract, day.date.weekday()) * base_target_factor
        return hour_target

    def _find_contract_for_date(self, target_date: date, contracts) -> Optional[Any]:
        for contract in contracts:
            is_after_start = (contract.valid_start is None) or (contract.valid_start <= target_date)
            is_before_stop = (contract.valid_stop is None) or (target_date <= contract.valid_stop)
            if is_after_start and is_before_stop:
                return contract
        return None
        
    def _get_hours_from_spread(self, contract, weekday: int) -> float:
        spread = contract.target_spread
        spread_sum = sum(spread)
        return 0.0 if spread_sum == 0 else contract.weekly_target * (spread[weekday] / spread_sum)

    def _empty_response(self) -> Dict[str, Any]:
        return {
            "team_meta": {
                "total_actual": 0.0,
                "total_target": 0.0,
                "total_overtime": 0.0
            },
            "team_shares": {},
            "project_history": {
                "labels": [],
                "projects": [],
                "targets": [],
                "actuals": []
            },
            "project_totals": {},
            "project_meta": {}
        }