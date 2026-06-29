import sys
import os
from tqdm import tqdm

from src.core.database import get_legacy_connection, get_target_session, engine, Base

from src.models import Employee, EmployeeHourTarget, EmployeeVacationClaim

from src.scripts.utils import parse_legacy_date

def run():
    print("--- Migrating Contracts (Soll & Urlaub) ---")
    session = get_target_session()
    conn = get_legacy_connection()
    cursor = conn.cursor(dictionary=True)

    # 1. Init Tables
    Base.metadata.create_all(bind=engine)
    session.query(EmployeeHourTarget).delete()
    session.query(EmployeeVacationClaim).delete()

    # --- PART A: Hour Targets (soll) ---
    print("Reading 'soll'...")
    # Adjust columns based on actual DB
    # Expected: mitarbeiter, sollstunden, wochenverteilung?, anfangsbestand?, datum_von, datum_bis
    cursor.execute("SELECT * FROM soll") 
    rows_soll = cursor.fetchall()

    valid_emp_ids = {id_[0] for id_ in session.query(Employee.id).all()}
    targets = []
    for row in tqdm(rows_soll, desc="Targets"):
        # orphan check
        emp_id = row['mitarbeiter']
        if emp_id not in valid_emp_ids:
            print(f"⚠️ Skipping target for unknown employee: {emp_id}")
            continue # Skip this row
        # Fix spread data-type
        # Transform "1|1|0..." -> [1.0, 1.0, 0.0...]
        weekly_target = float(row.get('soll', 0) or 0)
        legacy_spread = row.get('verteilung') or "1|1|1|1|1|0|0"
        try:
            spread_list = [float(x) for x in legacy_spread.split("|")]
        except ValueError:
            spread_list = [1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0] # Default Mon-Fri
        while len(spread_list) < 7: spread_list.append(0.0)
        
        spread_total = sum(spread_list)
        spread_list = [ weekly_target * x / spread_total for x in spread_list ]
        
        # Map legacy columns to new model
        target = EmployeeHourTarget(
            employee_id=emp_id,
            weekly_target=weekly_target,
            target_spread=spread_list, 
            starting_balance=float(row.get('soll_gesamt', 0) or 0),
            valid_start=parse_legacy_date(row.get('von')),
            valid_stop=parse_legacy_date(row.get('bis'))
        )
        targets.append(target)
    
    session.add_all(targets)
    print(f"   Queued {len(targets)} targets.")

    # --- PART B: Vacation Claims (urlaubsanspruch) ---
    print("Reading 'urlaubsanspruch'...")
    cursor.execute("SELECT * FROM urlaubsanspruch")
    rows_urlaub = cursor.fetchall()
    
    claims = []
    for row in tqdm(rows_urlaub, desc="Vacation"):
        claim = EmployeeVacationClaim(
            employee_id=row['mitarbeiter'],
            year=row.get('jahr') or None,
            days=float(row.get('anspruch', 0))
        )
        claims.append(claim)

    session.add_all(claims)
    print(f"   Queued {len(claims)} claims.")

    # Commit
    session.commit()
    print("✅ Success!")

if __name__ == "__main__":
    run()