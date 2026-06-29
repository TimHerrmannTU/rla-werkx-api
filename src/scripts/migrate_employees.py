import sys
import os

from src.core.database import get_legacy_connection, get_target_session, engine, Base

from src.models import Employee, Location

from datetime import datetime
from tqdm import tqdm

from src.scripts.utils import parse_legacy_date

def run():
    print("--- Migrating Employees ---")
    session = get_target_session()
    conn = get_legacy_connection()
    cursor = conn.cursor(dictionary=True)

    session.query(Employee).delete()

    location_map = _get_locations(session)
    color_map = _get_colors(cursor)
    rows = _get_employees(cursor)

    new_objs = []
    for emp in tqdm(rows, desc="Transforming"):
        eid = emp['kuerzel']
        
        # Helper logic for dates
        entry = parse_legacy_date(emp['eintritt'])
        std = parse_legacy_date(emp['beginn_erfassung'])
        if not std: std = entry
        first_job = parse_legacy_date(emp['erste_berufsttgkt'])
        
        fw_year = first_job.year if first_job else (entry.year if entry else None)
        
        emp_color = color_map[eid] if eid in color_map else "#CCCCCC"        
        
        location_id = location_map[emp["standort"]] 

        new_emp = Employee(
            id=eid,
            name=emp['name'],
            email=emp['email'],

            birthday=parse_legacy_date(emp['geburtsdatum']),
            entry_date=entry,
            exit_date=parse_legacy_date(emp['austritt']),
            
            first_work_year=fw_year,
            start_tracking_date=std,
            
            active=(emp['aktiv'] == 1),
            color=emp_color,
            location_id=location_id
        )
        new_objs.append(new_emp)

    # 3. Load
    print(f"Inserting {len(new_objs)} employees...")
    
    # Ensure table exists
    Employee.__table__.create(bind=engine, checkfirst=True)
    
    # Clear and Insert
    session.query(Employee).delete()
    session.add_all(new_objs)
    session.commit()
    
    print(f"✅ Success!")
    session.close()
    conn.close()
    
def _get_employees(cursor):
    print("Reading 'mitarbeiter'...")
    cursor.execute("""
        SELECT kuerzel, name, geburtsdatum, eintritt, austritt, erste_berufsttgkt, beginn_erfassung, aktiv, email, standort
        FROM mitarbeiter
    """)
    return cursor.fetchall()
    
def _get_colors(cursor):
    cursor.execute("""
        SELECT mitarbeiter, farbe FROM farben WHERE projekt IS NULL
    """)
    color_rows = cursor.fetchall()
    
    return {
        row["mitarbeiter"]: row["farbe"]
        for row in color_rows
    }
    
def _get_locations(session):
    
    legacy_locations = ["Dresden", "Berlin"] # id => name

    locations = session.query(Location).all()
    location_map = {loc.name: loc.id for loc in locations} # name => id

    if not set(legacy_locations).issubset(location_map):
        raise Exception("❌ Error: Essential locations not found. Run seed_locations.py first.")
    
    new_location_map = {
        i + 1: location_map[name]
        for i, name in enumerate(legacy_locations)
    }
    
    return new_location_map
        

if __name__ == "__main__":
    run()