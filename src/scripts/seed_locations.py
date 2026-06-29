import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.db_target import get_target_session, engine
from src.models import Base, Location

LOCATIONS = ["Dresden", "Berlin", "Prag"]

def run():
    print("--- Seeding Locations ---")
    session = get_target_session()
    Base.metadata.create_all(bind=engine) # Ensure table exists
    session.query(Location).delete()
    
    for location in LOCATIONS:
        session.add(Location(name=location))
    
    session.commit()
    print("✅ Locations seeded.")

if __name__ == "__main__":
    run()