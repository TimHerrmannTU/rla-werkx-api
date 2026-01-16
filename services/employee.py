from sqlalchemy.orm import Session, joinedload
from sqlalchemy import extract
from models.log import LogDailySummary
from models.calendar import CalendarDay

class EmployeeService:
    def __init__(self, db: Session):
        self.db = db

    def get_month_view(self, emp_id: str, year: int, month: int):
        # 1. Fetch Calendar Range (The Scaffold)
        # We fetch the CalendarDays directly to ensure we have every day
        days = self.db.query(CalendarDay).filter(
            extract('year', CalendarDay.date) == year,
            extract('month', CalendarDay.date) == month
        ).order_by(CalendarDay.date).all()

        # 2. Fetch Logs (Eager Load Children)
        logs = self.db.query(LogDailySummary).options(
            joinedload(LogDailySummary.project_hours),
            joinedload(LogDailySummary.timeframes_work),
            joinedload(LogDailySummary.timeframes_break)
        ).filter(
            LogDailySummary.employee_id == emp_id,
            extract('year', LogDailySummary.date) == year,
            extract('month', LogDailySummary.date) == month
        ).all()

        log_map = {l.date: l for l in logs}

        # 3. Merge
        payload = []
        for day in days:
            log = log_map.get(day.date)
            
            payload.append({
                "date": day.date,
                "is_weekend": day.is_weekend,
                "holiday": day.holiday,
                
                # Log Data (or Defaults)
                "status": log.status if log else "A",
                "status_target_factor": log.status_target_factor if log else (0.0 if day.is_weekend else 1.0),
                "note": log.general_note if log else None,
                
                # Aggregates
                "total_hours": sum(p.time for p in log.project_hours) if log else 0.0,
                
                # Details
                "project_hours": [
                    {
                        "project_id": p.project_id,
                        "phase_id": p.phase_id, 
                        "flag_id": p.flag_id,
                        "time": p.time,
                        "note": p.note,
                        "id": p.id,
                    } for p in (log.project_hours if log else [])
                ]
            })
            
        return payload