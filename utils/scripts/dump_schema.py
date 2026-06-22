# dump_schema.py
from database import engine
from sqlalchemy import MetaData

# Create a clean MetaData container
metadata = MetaData()

print("Connecting to your database and reflecting schema...")
metadata.reflect(bind=engine)

print("\n--- LIVE DB SCHEMA OVERVIEW ---")
for table_name, table in metadata.tables.items():
  print(f"Table: {table_name}")
  for column in table.columns:
    fk_relation = ""
    if column.foreign_keys:
      fk_relation = f" -> FK to {list(column.foreign_keys)[0].target_fullname}"
    print(f"  - {column.name} ({column.type}){fk_relation}")
  print()