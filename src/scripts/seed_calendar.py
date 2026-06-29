import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.db_target import get_target_session, engine
from src.models import Base, CalendarDay
from datetime import date, timedelta
from tqdm import tqdm

def run():
    print("--- Seeding Calendar Days (2000-2049) ---")
    session = get_target_session()
    
    # Create Table
    Base.metadata.create_all(bind=engine)
    
    # Wipe old
    session.query(CalendarDay).delete()
    
    start = date(2000, 1, 1)
    end = date(2049, 12, 31)
    
    current = start
    batch = []
    
    total = (end - start).days + 1
    
    for _ in tqdm(range(total)):
        # Calculate Attributes
        is_weekend = current.weekday() >= 5
        iso_week = current.isocalendar()[1]
        
        day = CalendarDay(
            date=current,
            year=current.year,
            month=current.month,
            day=current.day,
            weekday=current.weekday(),
            week_number=iso_week,
            is_weekend=is_weekend
        )
        batch.append(day)
        
        if len(batch) >= 5000:
            session.add_all(batch)
            session.commit()
            batch = []
            
        current += timedelta(days=1)
        
    if batch:
        session.add_all(batch)
        session.commit()
        
    print("✅ Calendar Days Seeded.")

if __name__ == "__main__":
    run()