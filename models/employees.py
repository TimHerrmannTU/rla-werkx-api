from sqlalchemy import Column, Integer, String, Text, Date, Float, Boolean, ForeignKey, JSON, Time, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Employee(Base):
    __tablename__ = "employees"

    id = Column(String(5), primary_key=True) # 'TmHn'
    name = Column(String(100))
    password_hash = Column(String(255))
    # TOKEN should not be saved in DB

    birthday = Column(Date)
    entry_date = Column(Date)
    exit_date = Column(Date, nullable=True)
    
    first_work_year = Column(Integer)
    start_tracking_date = Column(Date)
    
    active = Column(Boolean, default=True)

class EmployeeHourTarget(Base):
    __tablename__ = "employee_hour_targets"
    
    id = Column(Integer, primary_key=True)
    employee_id = Column(String(5), ForeignKey("employees.id"))
    weekly_target = Column(Float)
    target_spread = Column(JSON) # [1, 1, 1, 1, 1, 0, 0]
    starting_balance = Column(Float)
    
    valid_start = Column(Date, nullable=True) # Unfortunatly the source data is poor
    valid_stop = Column(Date, nullable=True) # Open-ended

class EmployeeVacationClaim(Base):
    __tablename__ = "employee_vacation_claims"
    
    id = Column(Integer, primary_key=True)
    employee_id = Column(String(5), ForeignKey("employees.id"))
    year = Column(Integer)
    days = Column(Float)
    # TODO investigate why parte_time column exists