from datetime import date, timedelta
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import extract, func
from collections import defaultdict

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
                self.db.query(
                    LogProjectHour.project_id, 
                    func.sum(LogProjectHour.time)
                )
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
        top_ids = [pid for pid in sorted_pros]

        final_pros = []
        for pid in sorted_pros:
            curr_h = current_data[pid]
            prev_h = previous_data.get(pid, 0.0)
            
            # Trend: Difference or Percent? Difference is safer for small numbers.
            diff = curr_h - prev_h
            pct = ((diff / prev_h) * 100) if prev_h > 0 else 100.0 if curr_h > 0 else 0.0
            
            final_pros.append({
                "pro_id": pid,
                "hours": round(curr_h, 2),
                "trend_abs": round(diff, 2), # e.g. +50.0 hours
                "trend_pct": round(pct, 1)   # e.g. +20.5%
            })
            
        payload["top_pros"] = final_pros

        ##################
        # TOP 10 HISTORY #
        ##################

        global_totals_query = (
            self.db.query(
                func.date_format(LogDailySummary.date, '%Y-%m').label('month'),
                func.sum(LogProjectHour.time)
            )
            .join(LogDailySummary)
            .filter(
                LogDailySummary.date >= start_date, 
                LogDailySummary.date <= end_date
                # Apply internal filter here too if requested? 
                # Usually 'Total' implies everything, but consistency matters.
            )
            .group_by('month')
            .all()
        )
        global_month_map = {row[0]: float(row[1]) for row in global_totals_query}

        history_query = (
            self.db.query(
                LogProjectHour.project_id,
                Project.color,
                func.date_format(LogDailySummary.date, '%Y-%m').label('month'),
                func.sum(LogProjectHour.time)
            )
            .join(Project, Project.id == LogProjectHour.project_id)
            .join(LogDailySummary)
            .filter(
                LogDailySummary.date >= start_date, 
                LogDailySummary.date <= end_date,
                LogProjectHour.project_id.in_(top_ids)
            )
            .group_by(LogProjectHour.project_id, 'month')
            .order_by('month')
            .all()
        )
        
        color_map = {}
        history_map = defaultdict(dict)
        all_months = set()
        
        for pid, color, month, hours in history_query:
            history_map[pid][month] = float(hours)
            all_months.add(month)
            color_map[pid] = color
            
        sorted_months = sorted(list(all_months))
        
        datasets = []
        for pid in top_ids:
            data_points = []
            for m in sorted_months:
                pro_hours = history_map[pid].get(m, 0.0)
                pro_hours_rel = 100 * pro_hours / global_month_map[m]
                data_points.append(round(pro_hours_rel, 2))
                
            datasets.append({
                "name": pid,
                "data": data_points
            })
            
        payload["history"] = {
            "labels": sorted_months,
            "datasets": datasets
        }
        payload["pro_colors"] = color_map
        
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