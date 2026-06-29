import sys
import os
from sqlalchemy import text, inspect

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.db_target import engine

def run():
    print("☢️ DB NUKE STARTED...")
    
    with engine.connect() as conn:
        # 1. Disable FK Checks globally for this connection
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
        
        # 2. Find ALL tables existing in the DB (not just models)
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        if not existing_tables:
            print("   Database is already empty.")
        else:
            print(f"   Found {len(existing_tables)} tables to destroy.")
            
            for table_name in existing_tables:
                print(f"   💥 Dropping {table_name}...")
                conn.execute(text(f"DROP TABLE IF EXISTS `{table_name}`"))
        
        # 3. Re-enable FK Checks
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
        conn.commit()

    print("✅ Database is completely clean.")

if __name__ == "__main__":
    run()