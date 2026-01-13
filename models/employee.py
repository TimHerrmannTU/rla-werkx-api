from sqlalchemy import Column, String, Integer, Float, Date, Boolean
from database import Base

class Employee(Base):
    __tablename__ = "mitarbeiter"

    id =   Column("kuerzel", String(10), primary_key=True)
    name = Column("name", String(255))
    
    # Contract / HR Data
    target_hours = Column("soll", Float) # daily
    total_hours =  Column("gesamtstunden", Float)
    
    # Dates
    entry_date     = Column("eintritt", String(20))
    exit_date      = Column("austritt", String(20))
    birth_date     = Column("geburtsdatum", String(20))
    first_job_date = Column("erste_berufsttgkt", String(20))
    
    # Status
    is_active = Column("aktiv", Boolean, default=True)