import sys
import os
from tqdm import tqdm

from src.core.database import get_legacy_connection, get_target_session, engine, Base

from src.models import LogDailySummary, Employee

from src.scripts.utils import parse_legacy_date

def run():
    print("--- Migration Part 1: The Daily Backbone ---")
    session = get_target_session()
    conn = get_legacy_connection()
    cursor = conn.cursor(dictionary=True)
    
    # 1. Setup Tables (DailySummary only for now)
    Base.metadata.create_all(bind=engine)
    session.query(LogDailySummary).delete() 
    session.commit()

    # 2. CACHE Employees
    valid_emps = {e.id for e in session.query(Employee.id).all()}

    # 3. BUILD THE MASTER LIST
    print("Scanning for active days...")
    unique_days = set()

    # A. Arbeitszeit (Work)
    cursor.execute("SELECT DISTINCT mitarbeiter, datum FROM arbeitszeit")
    for r in cursor.fetchall(): unique_days.add((r['mitarbeiter'], r['datum']))

    # B. Fehltage (Absence)
    cursor.execute("SELECT DISTINCT mitarbeiter, datum FROM fehltage")
    for r in cursor.fetchall(): unique_days.add((r['mitarbeiter'], r['datum']))

    # C. Notizen (General Only -> projekt IS NULL)
    cursor.execute("SELECT DISTINCT mitarbeiter, datum FROM notizen WHERE projekt IS NULL OR projekt = ''")
    for r in cursor.fetchall(): unique_days.add((r['mitarbeiter'], r['datum']))

    # D. Uhrzeiten (Times)
    try:
        cursor.execute("SELECT DISTINCT mitarbeiter, datum FROM uhrzeiten")
        for r in cursor.fetchall(): unique_days.add((r['mitarbeiter'], r['datum']))
    except: pass

    print(f"Found {len(unique_days)} unique active days.")

    # 4. FETCH DETAILS
    print("Loading Absences...")
    cursor.execute("SELECT mitarbeiter, datum, grund, sollfaktor, notiz FROM fehltage")
    absences = {(r['mitarbeiter'], r['datum']): r for r in cursor.fetchall()}

    print("Loading General Notes...")
    cursor.execute("SELECT mitarbeiter, datum, notiz FROM notizen WHERE projekt IS NULL OR projekt = ''")
    notes = {(r['mitarbeiter'], r['datum']): r['notiz'] for r in cursor.fetchall()}

    # 5. INSERT
    batch = []
    
    for emp_id, date_str in tqdm(unique_days, desc="Creating Backbone"):
        if emp_id not in valid_emps: continue
        d_obj = parse_legacy_date(date_str)
        if not d_obj: continue

        abs_entry = absences.get((emp_id, date_str))
        gen_note = notes.get((emp_id, date_str))

        status = 'A'
        factor = 1.0
        status_note = None

        if abs_entry:
            status = abs_entry['grund']
            if abs_entry['sollfaktor'] is not None:
                factor = float(abs_entry['sollfaktor'])
            else: factor = 0.0
            status_note = abs_entry['notiz']

        summary = LogDailySummary(
            employee_id=emp_id,
            date=d_obj,
            status=status,
            status_target_factor=factor,
            status_note=status_note,
            general_note=gen_note
        )
        batch.append(summary)
        
        if len(batch) >= 2000:
            session.add_all(batch)
            session.commit()
            batch = []

    if batch:
        session.add_all(batch)
        session.commit()

    print("✅ Part 1 Complete. Backbone created.")

if __name__ == "__main__":
    run()