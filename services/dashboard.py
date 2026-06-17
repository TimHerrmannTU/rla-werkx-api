from datetime import date, timedelta
from typing import Dict, List, Optional
from collections import defaultdict
from sqlalchemy.orm import Session
from sqlalchemy import extract, func

from models.project import Project, ProjectPhase
from models.log import LogDailySummary, LogProjectHour
from crud.project import project_crud


def _get_dashboard_data(
    db: Session,
    start_date: date,
    end_date: date,
    emp_ids: Optional[List[str]] = None,
    include_internal: bool = False,
) -> Dict:
    payload = {}

    # Scopes queries by date, optional team filters, and internal project filters
    def apply_scope(query, s: date, e: date):
        q = query.filter(
            LogDailySummary.date >= s, 
            LogDailySummary.date <= e
        )
        
        # If team IDs are provided, restrict scope to those employees
        if emp_ids is not None:
            q = q.filter(LogDailySummary.employee_id.in_(emp_ids))
            
        if not include_internal:
            q = q.filter(
                LogProjectHour.project_id.notlike("AA%"),
                LogProjectHour.project_id.notlike("WB%")
            )
        return q

    def fetch_totals(s: date, e: date) -> Dict[str, float]:
        query = db.query(
            LogProjectHour.project_id, 
            func.sum(LogProjectHour.time)
        ).join(LogDailySummary)
        
        results = apply_scope(query, s, e).group_by(LogProjectHour.project_id).all()
        return {pid: float(hours) for pid, hours in results}

    # Timeframe calculation for trends
    duration = (end_date - start_date).days + 1
    current_data = fetch_totals(start_date, end_date)
    previous_data = fetch_totals(
        start_date - timedelta(days=duration), 
        start_date - timedelta(days=1)
    )

    # Top 10 Projects
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
    payload["top_pros"] = final_pros

    # History & Totals (Company or Team)
    date_to_key = func.date_format(LogDailySummary.date, '%Y-%m')
    
    monthly_totals_query = apply_scope(
        db.query(date_to_key, func.sum(LogProjectHour.time)).join(LogDailySummary),
        start_date, end_date
    ).group_by(date_to_key).all()

    total_worked = round(sum(hours for _, hours in monthly_totals_query))
    payload["total_worked_company"] = {
        "total": total_worked,
        "avg_per_month": round(total_worked / len(monthly_totals_query)) if monthly_totals_query else 0,
        "per_month": {month: round(hours) for month, hours in monthly_totals_query}
    }

    # Project Specific History (Top 10)
    monthly_project_sums = apply_scope(
        db.query(LogProjectHour.project_id, date_to_key, func.sum(LogProjectHour.time)).join(LogDailySummary),
        start_date, end_date
    ).filter(LogProjectHour.project_id.in_(sorted_pids)).group_by(LogProjectHour.project_id, date_to_key).order_by(date_to_key).all()

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

    payload["top_ten_pro_history"] = {
        "labels": all_months,
        "datasets": datasets
    }

    # Phase Distribution
    phase_query = apply_scope(
        db.query(
            ProjectPhase.phase, 
            func.sum(LogProjectHour.time)
        ).join(
            LogProjectHour, 
            LogProjectHour.phase_id == ProjectPhase.id
        ).join(
            LogDailySummary
        ), start_date, end_date
    ).group_by(
        ProjectPhase.phase
    ).order_by(
        ProjectPhase.phase
    ).all()

    payload["phase_distribution"] = [
        {"phase": p_num, "hours": round(h)} for p_num, h in phase_query
    ]

    # Project Colors & Metadata
    pro_colors = project_crud.get_colors(db, sorted_pids)
    payload["pro_meta"] = {
        id: {"color": color, "name": name} for id, name, color in pro_colors
    }

    return payload

def get_general(
    db: Session, 
    start_date: date, 
    end_date: date, 
    include_internal: bool = False
) -> Dict:
    # Delegates directly to core engine without employee filter
    return _get_dashboard_data(
        db, 
        start_date=start_date, 
        end_date=end_date, 
        include_internal=include_internal
    )


def get_team_stats(
    db: Session, 
    emp_ids: List[str],
    start_date: date, 
    end_date: date, 
    include_internal: bool = True
) -> Dict:
    # Defensive guard for empty arrays
    if not emp_ids:
        return {
            "top_pros": [],
            "total_worked_company": {
                "total": 0,
                "avg_per_month": 0,
                "per_month": {}
            },
            "top_ten_pro_history": {
                "labels": [],
                "datasets": []
            },
            "phase_distribution": [],
            "pro_meta": {}
        }

    # Delegates to core engine with the active team filter
    return _get_dashboard_data(
        db, 
        start_date=start_date, 
        end_date=end_date, 
        emp_ids=emp_ids, 
        include_internal=include_internal
    )