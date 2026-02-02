# alembic/env.py
import os
import sys
from logging.config import fileConfig
from dotenv import load_dotenv

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

# 1. Add project root to python path to resolve 'database' and 'models'
sys.path.append(os.getcwd())

# 2. Load environment variables
load_dotenv()

# Alembic Config object
config = context.config

# Setup logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 3. Import Base and Models
from database import Base
import models
target_metadata = Base.metadata

# 4. Construct Database URL
db_user = os.getenv("DB_USER")
db_pass = os.getenv("DB_PASS")
db_host = os.getenv("DB_HOST")
db_name = os.getenv("DB_NAME")

if not all([db_user, db_pass, db_host, db_name]):
    raise ValueError("Missing required DB env vars: DB_USER, DB_PASS, DB_HOST, DB_NAME")

url = f"mysql+mysqlconnector://{db_user}:{db_pass}@{db_host}/{db_name}"

# 5. Inject URL into config
# We must define 'section' before using it
section = config.config_ini_section
config.set_section_option(section, "sqlalchemy.url", url)

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()