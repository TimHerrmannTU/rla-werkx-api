import sys
import os

from src.core.database import get_target_session, engine, Base

from src.models import VacationRule

RULES = [
    {"min": 0,  "max": 4,   "days": 24.0},
    {"min": 5,  "max": 9,   "days": 26.0},
    {"min": 10, "max": 14,  "days": 28.0},
    {"min": 15, "max": 200, "days": 30.0},
]

def run():
    print("--- Seeding Vacation Rules ---")
    session = get_target_session()
    Base.metadata.create_all(bind=engine)
    
    # Clean Slate
    session.query(VacationRule).delete()
    
    for r in RULES:
        rule = VacationRule(
            min_years=r["min"],
            max_years=r["max"],
            days=r["days"]
        )
        session.add(rule)
        
    session.commit()
    print("✅ Rules Seeded.")

if __name__ == "__main__":
    run()