# export_projects.py
import json
from src.database import engine
from sqlalchemy import text

def export_projects():
  print("Connecting to MySQL and exporting projects data...")
  
  with engine.connect() as conn:
    # 1. Fetch Projects (with name fallback)
    projects_result = conn.execute(text("SELECT id, name, color, active, creation_date FROM projects"))
    projects = []
    for r in projects_result:
      raw_name = r[1]
      fallback_name = raw_name if raw_name and raw_name.strip() else f"Project {r[0]}"
      projects.append({
        "id": r[0],
        "name": fallback_name,
        "color": r[2],
        "active": bool(r[3]) if r[3] is not None else True,
        "creationDate": r[4].isoformat() if r[4] else None
      })

    # 2. Fetch Project Phases (with name fallback)
    phases_result = conn.execute(text("SELECT id, name, phase, project_id FROM project_phases"))
    phases = []
    for r in phases_result:
      raw_name = r[1]
      fallback_name = raw_name if raw_name and raw_name.strip() else f"Phase {r[2] or r[0]}"
      phases.append({
        "id": r[0],
        "name": fallback_name,
        "phase": r[2],
        "project": r[3]
      })

    # 3. Fetch Project Partials (with name fallback)
    partials_result = conn.execute(text("SELECT id, name, project_id FROM project_partials"))
    partials = []
    for r in partials_result:
      raw_name = r[1]
      fallback_name = raw_name if raw_name and raw_name.strip() else f"Partial {r[0]}"
      partials.append({
        "id": int(r[0]),
        "name": fallback_name,
        "project": r[2]
      })

    # 4. Fetch Project Services (with name fallback)
    services_result = conn.execute(text("SELECT id, name, project_id FROM project_services"))
    services = []
    for r in services_result:
      raw_name = r[1]
      fallback_name = raw_name if raw_name and raw_name.strip() else f"Service {r[0]}"
      services.append({
        "id": int(r[0]),
        "name": fallback_name,
        "project": r[2]
      })

    # 5. Fetch Project Flags (with name fallback)
    flags_result = conn.execute(text("""
      SELECT id, name, color, project_id, phase, time_budget, linked_partial_id, linked_service_id 
      FROM project_flags
    """))
    flags = []
    for r in flags_result:
      raw_name = r[1]
      fallback_name = raw_name if raw_name and raw_name.strip() else f"Flag {r[0]}"
      flags.append({
        "id": r[0],
        "name": fallback_name,
        "color": r[2],
        "project": r[3],
        "phase": r[4],
        "timeBudget": float(r[5]) if r[5] is not None else 0.0,
        "linkedPartial": int(r[6]) if r[6] is not None else None,
        "linkedService": int(r[7]) if r[7] is not None else None
      })

  # Export to unified JSON
  output = {
    "projects": projects,
    "phases": phases,
    "partials": partials,
    "services": services,
    "flags": flags
  }

  with open("werkx_projects.json", "w") as f:
    json.dump(output, f, indent=2)

  print("Successfully exported projects data to werkx_projects.json")

if __name__ == "__main__":
  export_projects()