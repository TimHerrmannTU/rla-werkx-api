from sqlalchemy import Column, String, Integer, Float, Date, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Employee(Base):
    __tablename__ = "employees"

    id = Column(String(5), primary_key=True) 
    name = Column(String(100))
    password_hash = Column(String(255))
    
    color = Column(String)
    birthday = Column(Date)
    entry_date = Column(Date)
    exit_date = Column(Date, nullable=True)
    first_work_year = Column(Integer)
    start_tracking_date = Column(Date)
    active = Column(Boolean, default=True)

    location_id = Column(Integer, ForeignKey("locations.id"))

    # Relationships
    location = relationship("Location", back_populates="employees")
    hour_targets = relationship("EmployeeHourTarget", back_populates="employee")
    vacation_claims = relationship("EmployeeVacationClaim", back_populates="employee")

class EmployeeHourTarget(Base):
    __tablename__ = "employee_hour_targets"
    
    id = Column(Integer, primary_key=True)
    employee_id = Column(String(5), ForeignKey("employees.id"))
    weekly_target = Column(Float)
    target_spread = Column(JSON) 
    starting_balance = Column(Float)
    valid_start = Column(Date, nullable=True)
    valid_stop = Column(Date, nullable=True)

    employee = relationship("Employee", back_populates="hour_targets")

class EmployeeVacationClaim(Base):
    __tablename__ = "employee_vacation_claims"
    
    id = Column(Integer, primary_key=True)
    employee_id = Column(String(5), ForeignKey("employees.id"))
    year = Column(Integer)
    days = Column(Float)

    employee = relationship("Employee", back_populates="vacation_claims")