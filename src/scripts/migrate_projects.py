import sys
import os
from tqdm import tqdm
import unicodedata

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.database import get_legacy_connection, get_target_session, engine, Base

from src.modules.project.model import Project, ProjectPhase, ProjectPartial, ProjectService, ProjectFlag

from src.core.utils.date_helper import parse_legacy_date

def clean_str(val):
    if isinstance(val, str):
        # Normalizes NFD (decomposed) umlauts to standard NFC (composed) [14]
        return unicodedata.normalize('NFC', val.strip())
    return val

def run():
    print("--- Migrating Projects Structure ---")
    session = get_target_session()
    conn = get_legacy_connection()
    cursor = conn.cursor(dictionary=True)
    
    Base.metadata.create_all(bind=engine)
    
    # Clear Tables (Order matters for FKs)
    session.query(ProjectFlag).delete()
    session.query(ProjectPartial).delete()
    session.query(ProjectService).delete()
    session.query(ProjectPhase).delete()
    session.query(Project).delete()

    # --- 1. PROJECTS (projektgruppen) ---
    print("1. Projects...")
    
    # Cache for color lookup
    cursor.execute("SELECT projekt, farbe FROM farben WHERE mitarbeiter IS NULL")
    colors = {row['projekt']: row['farbe'] for row in cursor.fetchall()}
    
    # Reload cursor for groups
    cursor.execute("SELECT * FROM projektgruppen")
    
    project_objs = []
    for row in cursor.fetchall():
        pid = clean_str(row['kuerzel'])
        p = Project(
            id=pid,
            name=row['voller_name'],
            color=colors.get(pid),
            active=(row['aktiv'] == 1),
            creation_date=parse_legacy_date(row['erstellungs_datum'])
        )
        project_objs.append(p)
    
    session.add_all(project_objs)
    session.commit() # Commit so FKs work

    # --- 2. PHASES (projekte) ---
    print("2. Phases...")
    cursor.execute("SELECT * FROM projekte")
    phases_objs = []
    
    for row in cursor.fetchall():
        parent = row['projekt']
        # Integrity Check: Does parent exist?
        if not session.get(Project, parent):
            print(f"⚠️ Orphan Phase {row['kuerzel']} (Parent {parent} missing)")
            continue
            
        ph = ProjectPhase(
            id=clean_str(row['kuerzel']),
            name=row['voller_name'],
            phase=str(row['leistungsphase']),
            project_id=parent
        )
        phases_objs.append(ph)
        
    session.add_all(phases_objs)
    session.commit()

    # --- 3. PARTIALS & SERVICES ---
    # Need to fetch legacy partials (teilobjekte) and services (bes_leistungen)
    # Assuming tables: 'teilobjekte' (projekt, name) and 'bes_leistungen' (projekt, name)
    
    print("3. Partials & Services...")
    
    # Partials
    cursor.execute("SELECT projekt, name FROM teilobjekte")
    partial_map = {} # (project_id, name) -> new_id
    
    for row in cursor.fetchall():
        pid = row['projekt']
        pname = row['name']
        if not session.get(Project, pid): continue
        
        part = ProjectPartial(name=pname, project_id=pid)
        session.add(part)
        session.flush() # Get ID
        partial_map[(pid, pname)] = part.id


    # Services
    cursor.execute("SELECT projekt, name FROM bes_leistungen")
    service_map = {} 
    
    for row in cursor.fetchall():
        pid = row['projekt']
        pname = row['name']
        if not session.get(Project, pid): continue
        
        svc = ProjectService(name=pname, project_id=pid)
        session.add(svc)
        session.flush()
        service_map[(pid, pname)] = svc.id

    session.commit()

    # --- 4. FLAGS (stundentags) ---
    print("4. Flags...")
    cursor.execute("SELECT * FROM stundentags")
    
    flags_objs = []
    for row in tqdm(cursor.fetchall()):
        pro_id = row['projekt']
        name = row['name']
        
        pro_ref = session.get(Project, pro_id)
        if not pro_ref:
            print(f"⚠️ Orphan Flag {row['id']} (Target {pro_id} missing)")
            continue

        # Resolve Links (Legacy stored Names, we want IDs)
        # kopplung_to -> Partial
        # kopplung_weitere_leistung -> Service
        
        link_p_id = None
        link_s_id = None
        
        if row.get('kopplung_to'):
            link_p_id = partial_map.get((pro_id, row['kopplung_to']))
            
        if row.get('kopplung_weitere_leistung'):
            link_s_id = service_map.get((pro_id, row['kopplung_weitere_leistung']))

        flag = ProjectFlag(
            id=str(row['id']),
            name=name,
            color=row['farbe'],
            project_id=pro_id,
            phase=row.get('phase'),
            time_budget=row.get('budget'),
            linked_partial_id=link_p_id,
            linked_service_id=link_s_id
        )
        flags_objs.append(flag)

    session.add_all(flags_objs)
    session.commit()
    
    print("✅ Projects Structure Migrated.")

if __name__ == "__main__":
    run()