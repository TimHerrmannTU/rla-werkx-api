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
    entry_date     = Column("eintritt", Date)
    exit_date      = Column("austritt", Date, nullable=True)
    birth_date     = Column("geburtsdatum", Date)
    first_job_date = Column("erste_berufsttgkt", Date)
    
    # Status
    is_active = Column("aktiv", Boolean, default=True)