import sys
import os
from datetime import datetime
from tqdm import tqdm

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.database import get_legacy_connection, get_target_session, engine, Base

from src.modules.calender.model import Holiday
from src.modules.location.model import Location

from src.core.utils.date_helper import parse_legacy_date

def run():
    print("--- Migrating Holidays ---")
    
    # 1. Init Target DB (Create table if missing)
    Base.metadata.create_all(bind=engine)
    session = get_target_session()
    
    # 2. Extract
    print("Extracting from Legacy...")
    legacy_conn = get_legacy_connection()
    cursor = legacy_conn.cursor()

    cursor.execute("SELECT datum, name, standort, sollfaktor FROM feiertage")
    rows = cursor.fetchall()
    cursor.execute("SELECT datum, notiz, sollfaktor FROM sonderdefinitionen")
    rows_special = cursor.fetchall()
    
    print(f"Found {len(rows)} rows.")

    dresden_id = session.query(Location.id).filter_by(name="Dresden").scalar()
    if not dresden_id:
        print("❌ Error: Run seed_locations.py first.")
        return

    # 3. Transform & Load
    new_records = []    
    for row in tqdm(rows, desc="Transforming"):
        date_val = parse_legacy_date(row[0])
        if not date_val: continue
        
        holiday = Holiday(
            date=date_val,
            name=row[1],
            region="DD" if row[2] == "N" else row[2],
            target_factor=row[3] if row[3] is not None else 0.0,
            is_company_holiday=False,
            location_id=dresden_id
        )
        new_records.append(holiday)

    for row in tqdm(rows_special, desc="Transforming"):
        date_val = parse_legacy_date(row[0])
        if not date_val: continue
        
        holiday = Holiday(
            date=date_val,
            name=row[1],
            region="DD",
            target_factor=row[2] if row[2] is not None else 0.0,
            is_company_holiday=True,
            location_id=dresden_id            
        )
        new_records.append(holiday)

    # 4. Commit
    print("Clearing old data...")
    session.query(Holiday).delete()
    
    print("Inserting...")
    session.add_all(new_records)
    session.commit()
    
    print(f"✅ Success! Migrated {len(new_records)} holidays.")
    session.close()
    legacy_conn.close()

if __name__ == "__main__":
    run()