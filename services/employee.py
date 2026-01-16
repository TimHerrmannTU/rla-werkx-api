from sqlalchemy import func, and_
from sqlalchemy.orm import Session

from datetime import date
import calendar

from models.employee import Employee
from models.calendar import Holiday
from models.log import LogDailySummary

class EmployeeService:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, active_only: bool = True):
        query = self.db.query(Employee)
        if active_only:
            query = query.filter(Employee.is_active == True)
        return query.order_by(func.lower(Employee.name)).all()
    
    def get_id_map(self, active_only: bool = False):
        employees = self.get_all(active_only)
        return {emp.name: emp.id for emp in employees}

    def get_by_id(self, emp_id: str):
        return self.db.query(Employee).filter(Employee.id == emp_id).first()
    
    def get_month_data(self, emp_id: str, year: int, month: int):
        # 1. Define Range
        num_days = calendar.monthrange(year, month)[1]
        
        # Legacy Format Helpers
        # Generate strings "d20250101" to "d20250131" for DB querying
        start_str = f"d{year}{month:02d}01"
        end_str   = f"d{year}{month:02d}{num_days:02d}"

        # 2. Fetch Data (Bulk Fetch using String Range)
        entries = self.db.query(LogDailySummary).filter(
            LogDailySummary.emp_id == emp_id,
            LogDailySummary.date_str >= start_str,
            LogDailySummary.date_str <= end_str
        ).all()
        
        holidays = self.db.query(Holiday).filter(
            Holiday.date_str >= start_str,
            Holiday.date_str <= end_str
        ).all()

        # 3. Create Lookups
        entry_map = {e.date_str: e for e in entries}
        holiday_map = {h.date_str: h for h in holidays}

        # 4. Generate & Merge
        days = []
        for d in range(1, num_days + 1):
            current = date(year, month, d)
            legacy_id = f"d{current.strftime('%Y%m%d')}"
            
            # Context Logic
            holiday = holiday_map.get(legacy_id)
            entry = entry_map.get(legacy_id)
            is_weekend = current.weekday() >= 5 

            if holiday:
                is_holiday = True
                holiday_name = holiday.name
                # Use DB factor (usually 0.0 or 0.5)
                target_factor = holiday.target_factor
            else:
                is_holiday = False
                holiday_name = None
                # Default Logic: Weekend=0, Weekday=1
                target_factor = 0.0 if is_weekend else 1.0

            days.append({
                "date": current, # Pydantic will serialize to YYYY-MM-DD
                "date_legacy": legacy_id,
                "is_weekend": is_weekend,
                "is_holiday": is_holiday,
                "holiday_name": holiday_name,
                "target_factor": target_factor,
                
                # Entry Data
            })

        return days