import sys
import os
import subprocess

# Define the sequence (Order matters!)
SCRIPTS = [
    "reset_db.py",
    "seed_locations.py",
    "seed_calendar.py",
    "migrate_holidays.py",
    "migrate_employees.py",
    "migrate_contracts.py",
    "migrate_projects.py",
    "migrate_logs_general.py",
    "migrate_logs_projects.py",
    "calc_targets.py"
]

def run():
    base_path = os.path.dirname(os.path.abspath(__file__))
    
    print("🚀 Starting Full Migration Sequence...")
    
    for script_name in SCRIPTS:
        script_path = os.path.join(base_path, script_name)
        print(f"\n▶️ Running: {script_name}")
        
        # Execute script as a separate process
        result = subprocess.run([sys.executable, script_path])
        
        if result.returncode != 0:
            print(f"❌ Failed at {script_name}. Aborting.")
            sys.exit(result.returncode)
            
    print("\n✅ All migrations completed successfully.")

if __name__ == "__main__":
    run()