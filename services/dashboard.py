from datetime import date, timedelta
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import extract, func

from models.project import Project, ProjectPhase
from models.log import *

class DashboardService:
    def __init__(self, db: Session):
        self.db = db

    def get_project_stats(self, start_date: date, end_date: date):
        payload = {}

        ###################
        # TOP 10 PROJECTS #
        ###################        
        def fetch_totals(s, e): # HELPER FUNCTION
            results = (
                self.db.query(LogProjectHour.project_id, func.sum(LogProjectHour.time))
                    .join(LogDailySummary)
                    .filter(
                        LogDailySummary.date >= s, 
                        LogDailySummary.date <= e,
                        LogProjectHour.project_id.notlike("AA%") # Exclude Internal
                    )
                    .group_by(LogProjectHour.project_id)
                    .all()
            )
            return {pid: float(hours) for pid, hours in results}
        
        # fetch current and previous timeframe for trend
        duration = (end_date - start_date).days + 1
        current_data  = fetch_totals(start_date, end_date)
        previous_data = fetch_totals(start_date - timedelta(days=duration - 1), start_date - timedelta(days=1))

        sorted_pros = sorted(current_data.keys(), key=lambda k: current_data[k], reverse=True)[:10]
        final_pros = []
        for pid in sorted_pros:
            curr_h = current_data[pid]
            prev_h = previous_data.get(pid, 0.0)
            
            # Trend: Difference or Percent? Difference is safer for small numbers.
            diff = curr_h - prev_h
            pct = ((diff / prev_h) * 100) if prev_h > 0 else 100.0 if curr_h > 0 else 0.0
            
            final_pros.append({
                "project_id": pid,
                "hours": round(curr_h, 2),
                "trend_abs": round(diff, 2), # e.g. +50.0 hours
                "trend_pct": round(pct, 1)   # e.g. +20.5%
            })
            
        payload["top_projects"] = final_pros
        
        ######################
        # PHASE DISTRIBUTION #
        ######################
        phase_query = (
            self.db.query(ProjectPhase.phase, func.sum(LogProjectHour.time))
                .join(LogProjectHour, LogProjectHour.phase_id == ProjectPhase.id)
                .join(LogDailySummary)
                .filter(
                    LogDailySummary.date >= start_date, 
                    LogDailySummary.date <= end_date,
                    LogProjectHour.project_id.notlike("AA%") # Exclude Internal
                )
                .group_by(ProjectPhase.phase)
                .order_by(ProjectPhase.phase)
                .all()
        )

        total_hours = sum(hours or 0 for _, hours in phase_query)
        phase_stats = []
        for p_num, h in phase_query:
            share = (h / total_hours * 100) if total_hours > 0 else 0.0
            phase_stats.append({
                "phase": p_num,
                "hours": round(h, 2),
                "share": round(share, 1)
            })

        payload["phase_distribution"] = phase_stats
        
        return payload