# export_migration_data.py
import json
from database import engine
from sqlalchemy import text

def parse_and_normalize_weights(emp_id, spread):
  days = ["mo", "di", "mi", "do", "fr", "sa", "so"]
  if not spread:
    return {
      "mo": 1.0, "di": 1.0, "mi": 1.0, "do": 1.0, "fr": 1.0,
      "sa": 0.0, "so": 0.0
    }
  if isinstance(spread, list):
    spread = {days[i]: spread[i] for i in range(min(len(spread), len(days)))}
  normalized = {}
  for d in days:
    found_val = 0.0
    for k, v in spread.items():
      if k.lower()[:2] == d:
        found_val = float(v) if v is not None else 0.0
        break
    normalized[d] = found_val
  return normalized

def export_data():
  print("Connecting to MySQL and exporting complete employee lists and location structures...")
  
  with engine.connect() as conn:
    # 1. Fetch complete employee list (including newly added fields)
    emp_query = text("""
      SELECT e.id, e.name, e.email, e.birthday, e.entry_date, e.exit_date, e.color, l.name AS location_name,
             e.first_work_year, e.start_tracking_date
      FROM employees e 
      LEFT JOIN locations l ON e.location_id = l.id
    """)
    emp_result = conn.execute(emp_query)
    
    employees_dict = {}
    for row in emp_result:
      emp_id = row[0]
      employees_dict[emp_id] = {
        "slug": emp_id,
        "name": row[1],
        "email": row[2],
        "birthday": row[3].isoformat() if row[3] else None,
        "entry": row[4].isoformat() if row[4] else None,
        "exit": row[5].isoformat() if row[5] else None,
        "color": row[6],
        "location_name": row[7],
        "firstWorkYear": int(row[8]) if row[8] is not None else None,
        "startTrackingDate": row[9].isoformat() if row[9] else None,
        "sollHistory": [],
        "vacationClaims": []
      }

    # 2. Fetch employee target hours (including starting_balance)
    targets_query = text("""
      SELECT employee_id, weekly_target, target_spread, valid_start, valid_stop, starting_balance 
      FROM employee_hour_targets
    """)
    targets_result = conn.execute(targets_query)
    
    for row in targets_result:
      emp_id = row[0]
      if emp_id not in employees_dict:
        continue
        
      spread = row[2]
      if isinstance(spread, str):
        spread = json.loads(spread)
      
      normalized_distribution = parse_and_normalize_weights(emp_id, spread)
      
      employees_dict[emp_id]["sollHistory"].append({
        "targetHours": float(row[1]) if row[1] is not None else 0.0,
        "startingBalance": float(row[5]) if row[5] is not None else 0.0,
        "start": row[3].isoformat() if row[3] else None,
        "end": row[4].isoformat() if row[4] else None,
        "distribution": normalized_distribution
      })

    # 3. Fetch vacation claims
    vacation_query = text("SELECT employee_id, year, days FROM employee_vacation_claims")
    vacation_result = conn.execute(vacation_query)
    
    for row in vacation_result:
      emp_id = row[0]
      if emp_id not in employees_dict:
        continue
        
      employees_dict[emp_id]["vacationClaims"].append({
        "year": row[1],
        "days": row[2]
      })

  # 4. Save to JSON
  output_file = "migration_data.json"
  with open(output_file, "w") as f:
    json.dump(employees_dict, f, indent=2)

  print(f"Successfully exported comprehensive data to {output_file}")

if __name__ == "__main__":
  export_data()