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
    print("🚀 Starting Full Migration Sequence...")
    
    for script_name in SCRIPTS:
        module_name = f"src.scripts.{script_name.replace('.py', '')}"
        print(f"\n▶️ Running: {module_name}")
        
        result = subprocess.run([sys.executable, "-m", module_name])
        
        if result.returncode != 0:
            print(f"❌ Failed at {module_name}. Aborting.")
            sys.exit(result.returncode)
            
    print("\n✅ All migrations completed successfully.")

if __name__ == "__main__":
    run()