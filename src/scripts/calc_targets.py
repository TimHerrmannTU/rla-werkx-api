import sys
import os
from tqdm import tqdm
from datetime import date
from sqlalchemy.orm import joinedload

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.database import get_target_session, engine, Base

from src.modules.log.model import LogDailySummary
from src.modules.employee.model import Employee, EmployeeHourTarget
from src.modules.calender.model import CalendarDay, Holiday

def run():
    print("--- Calculating Target Hours (History) ---")
    session = get_target_session()
    
    # 1. Load Context
    print("Loading Calendar & Holidays...")
    days = session.query(CalendarDay).all()
    day_map = {d.date: d for d in days}
    
    holidays = session.query(Holiday).all()
    holiday_map = {h.date: h for h in holidays}
    
    print("Loading Employees...")
    # Eager load targets for in-memory filtering
    employees = session.query(Employee).options(joinedload(Employee.hour_targets)).all()
    
    print(f"Processing {len(employees)} employees...")
    
    for emp in tqdm(employees):
        # Fetch all logs for this user
        logs = session.query(LogDailySummary).filter(
            LogDailySummary.employee_id == emp.id
        ).all()
        
        # Sort contracts once (Newest First) to optimize lookups
        # Logic: We want the contract that covers the date. 
        # If overlaps exist, taking the latest valid_start is usually safe.
        contracts = sorted(
            emp.hour_targets, 
            key=lambda c: c.valid_start or date.min, 
            reverse=True
        )
        
        for log in logs:
            d_obj = log.date
            
            # --- 1. FIND CONTRACT ---
            # Using your requested logic logic adapted for single day iteration
            # Find first contract where: Start <= Day <= End
            contract = next((c for c in contracts if 
                (c.valid_start is None or c.valid_start <= d_obj) and 
                (c.valid_stop is None or c.valid_stop >= d_obj)
            ), None)
            
            # --- 2. CALCULATE BASE ---
            base_hours = 0.0
            if contract:
                spread = contract.target_spread or [1.0]*7
                w_idx = d_obj.weekday()
                base_hours = spread[w_idx] if w_idx < len(spread) else 0.0

            # --- 3. APPLY CONTEXT (Holiday > Weekend > Status) ---
            calendar_day = day_map.get(d_obj)
            holiday = holiday_map.get(d_obj)
            
            final_factor = 1.0
            
            if holiday:
                # Holidays override everything (usually 0.0, or 0.5 for Xmas Eve)
                final_factor = holiday.target_factor if log.status_target_factor == 1.0 else 0; 
            elif calendar_day and calendar_day.is_weekend:
                # Weekends are 0.0 (unless your spread handles this, but safe to force 0)
                final_factor = 0.0
            else:
                # Normal Day: Apply User Status (Sick/Vacation/Present)
                # log.status_target_factor comes from migration (fehltage table)
                # 1.0 = Present, 0.0 = Full Sick, 0.5 = Half Day
                final_factor = log.status_target_factor

            log.target_hours = round(base_hours * final_factor, 2)
            
        session.flush() # Flush per user
        
    session.commit()
    print("✅ Target Hours Calculated.")

if __name__ == "__main__":
    run()