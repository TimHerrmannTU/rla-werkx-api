# src/core/database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from src.core.config import get_settings

settings = get_settings()
Base = declarative_base()

def create_db_engine(fetch_from_legacy_table: bool = False):
    url = settings.get_database_url(fetch_from_legacy_table)
    return create_engine(url)

def get_sessionmaker(fetch_from_legacy_table: bool = False):
    engine_instance = create_db_engine(fetch_from_legacy_table)
    return sessionmaker(autocommit=False, autoflush=False, bind=engine_instance)

def get_target_session():
    return SessionLocal()

def get_legacy_connection():
    import mysql.connector 
    return mysql.connector.connect(
        host=settings.DB_HOST,
        user=settings.DB_USER,
        password=settings.DB_PASS,
        database=settings.OLD_DB_NAME
    )
    
engine = create_db_engine(fetch_from_legacy_table=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()