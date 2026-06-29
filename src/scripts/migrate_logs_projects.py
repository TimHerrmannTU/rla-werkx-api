import sys
import os
from collections import defaultdict
from datetime import time
from tqdm import tqdm
import unicodedata

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.database import get_legacy_connection, get_target_session, engine, Base

from src.modules.log.model import LogDailySummary, LogTimeframe, LogProjectHour
from src.modules.project.model import Project, ProjectPhase, ProjectFlag

from src.core.utils.date_helper import parse_legacy_date

def clean_str(val):
    if isinstance(val, str):
        # Normalizes NFD (decomposed) umlauts to standard NFC (composed) [14]
        return unicodedata.normalize('NFC', val.strip())
    return val

def to_time(val):
    if not val: return None
    if isinstance(val, time): return val
    if hasattr(val, 'total_seconds'): 
        seconds = int(val.total_seconds())
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return time(min(hours, 23), min(minutes, 59))
    return None

def normalize_phase_id(raw_id, valid_phases):
    if raw_id in valid_phases: return raw_id
    if raw_id and raw_id[-1].isdigit():
        alt_id = f"{raw_id[:-1]}_{raw_id[-1]}"
        if alt_id in valid_phases:
            return alt_id
    return None

def run():
    print("--- Migration Part 2: The Details (Split Strategy) ---")
    session = get_target_session()
    conn = get_legacy_connection()
    cursor = conn.cursor(dictionary=True)
    
    print("Clearing details...")
    session.query(LogProjectHour).delete()
    session.query(LogTimeframe).delete()
    session.commit()

    print("Caching valid IDs...")
    valid_projects = {p.id for p in session.query(Project.id).all()}
    valid_phases = {p.id: p.project_id for p in session.query(ProjectPhase).all()}
    valid_flags = {str(f.id) for f in session.query(ProjectFlag.id).all()}

    print("Loading Daily Summaries...")
    summaries = session.query(LogDailySummary.id, LogDailySummary.employee_id, LogDailySummary.date).all()
    summary_map = {(s.employee_id, s.date): s.id for s in summaries}
    
    # 1. FETCH LEGACY DATA
    print("Fetching 'uhrzeiten'...")
    try:
        cursor.execute("SELECT mitarbeiter, datum, start, stop, pause FROM uhrzeiten")
        times_map = defaultdict(list)
        for row in cursor.fetchall():
            d_obj = parse_legacy_date(row['datum'])
            if d_obj:
                times_map[(row['mitarbeiter'], d_obj)].append(row)
    except:
        print("⚠️ 'uhrzeiten' missing.")
        times_map = {}

    print("Fetching 'arbeitszeit' (Totals)...")
    cursor.execute("SELECT mitarbeiter, datum, projekt, arbeitszeit, notiz FROM arbeitszeit")
    work_totals_map = defaultdict(list)
    for row in cursor.fetchall():
        d_obj = parse_legacy_date(row['datum'])
        if d_obj:
            work_totals_map[(row['mitarbeiter'], d_obj)].append(row)

    print("Fetching 'stundeneigenschaften' (Flags)...")
    cursor.execute("SELECT mitarbeiter, datum, projekt, zeit, notiz, tag FROM stundeneigenschaften")
    work_flags_map = defaultdict(list)
    for row in cursor.fetchall():
        d_obj = parse_legacy_date(row['datum'])
        if d_obj:
            work_flags_map[(row['mitarbeiter'], d_obj)].append(row)

    # 2. PROCESS
    print("Processing Logs...")
    batch = []
    
    for (emp_id, date_obj), daily_id in tqdm(summary_map.items()):
        
        # A. Timeframes
        day_times = times_map.get((emp_id, date_obj), [])
        for t in day_times:
            if not t['start'] or not t['stop']: continue
            s = to_time(t['start'])
            e = to_time(t['stop'])
            batch.append( LogTimeframe( daily_entry_id=daily_id, start=s, stop=e, is_break=(t['pause'] == 1) ) )

        # B. Project Logic (The Merge)
        totals = work_totals_map.get((emp_id, date_obj), [])
        flags = work_flags_map.get((emp_id, date_obj), [])
        
        # Bucket by Phase ID (e.g. "DEC_1")
        # Structure: { "DEC_1": { total: 8.0, flags: [row, row], note: "..." } }
        phase_buckets = defaultdict(lambda: {'total': 0.0, 'flags': [], 'notes': set()})
        
        for t in totals:
            pid = t['projekt'] # "DEC_1"
            phase_buckets[pid]['total'] += float(t['arbeitszeit'] or 0)
            if t['notiz']: phase_buckets[pid]['notes'].add(t['notiz'])
            
        for f in flags:
            pid = f['projekt'] # "DEC_1"
            phase_buckets[pid]['flags'].append(f)

        # Generate Rows
        for legacy_pid, data in phase_buckets.items():
            legacy_pid = clean_str(legacy_pid)
            # Resolve Hierarchy (Project / Phase)
            p_id, ph_id = None, None
            
            if legacy_pid in valid_projects:
                p_id = legacy_pid
            elif legacy_pid in valid_phases:
                ph_id = legacy_pid
                p_id = valid_phases[legacy_pid]
            else:
                print(f"⚠️ orphan log, unknown phase: '{legacy_pid}'")
                continue

            # 1. Insert Flagged Hours
            sum_flagged = 0.0
            for f_row in data['flags']:
                h = float(f_row['zeit'] or 0)
                sum_flagged += h
                
                # Flag ID Resolution
                f_id = None
                if f_row['tag']:
                    s_flag = str(f_row['tag'])
                    if s_flag in valid_flags:
                        f_id = s_flag
                
                batch.append(LogProjectHour(
                    daily_entry_id=daily_id,
                    time=h,
                    note=f_row['notiz'],
                    project_id=p_id,
                    phase_id=ph_id,
                    flag_id=f_id
                ))

            # 2. Insert Remainder (Unflagged Phase Hours)
            remainder = data['total'] - sum_flagged
            if remainder > 0.01:
                note_str = "; ".join(data['notes']) if data['notes'] else None
                batch.append(LogProjectHour(
                    daily_entry_id=daily_id,
                    time=remainder,
                    note=note_str,
                    project_id=p_id,
                    phase_id=ph_id,
                    flag_id=None # Pure Phase time
                ))

        if len(batch) >= 5000:
            session.add_all(batch)
            session.commit()
            batch = []

    if batch:
        session.add_all(batch)
        session.commit()

    print("✅ Details Migrated.")

if __name__ == "__main__":
    run()