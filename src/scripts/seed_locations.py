import sys
import os

from src.core.database import get_target_session, engine, Base

from src.models import Location

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