from sqlalchemy import Column, Integer, String, Text, Date, Float, Boolean, ForeignKey, JSON, Time, UniqueConstraint
from sqlalchemy.orm import relationship

from database import Base

# LOGGING STUFF
class LogDailySummary(Base):
    __tablename__ = "log_daily_summary"
    
    id = Column(Integer, primary_key=True)
    employee_id = Column(String(5), ForeignKey("employees.id"))
    date = Column(Date, ForeignKey("calendar_days.date"))
    
    status = Column(String(5), default="A")
    status_target_factor = Column(Float, default=1.0)
    status_note = Column(String(255))
    general_note = Column(Text)
    
    target_hours = Column(Float)
    project_hours = relationship("LogProjectHour", back_populates="daily_entry")
    timeframes = relationship("LogTimeframe", back_populates="daily_entry")
    
    __table_args__ = (UniqueConstraint('date', 'employee_id', name='uix_log_daily_emp_date'),)

class LogTimeframe(Base):
    __tablename__ = "log_timeframes"
    id = Column(Integer, primary_key=True)
    daily_entry_id = Column(Integer, ForeignKey("log_daily_summary.id"))
    start = Column(Time)
    stop = Column(Time)
    is_break = Column(Boolean)
    
    daily_entry = relationship("LogDailySummary", back_populates="timeframes")

class LogProjectHour(Base):
    __tablename__ = "log_project_hours"
    id = Column(Integer, primary_key=True)
    daily_entry_id = Column(Integer, ForeignKey("log_daily_summary.id"))
    time = Column(Float)
    note = Column(Text)
    
    project_id = Column(String(50), ForeignKey("projects.id"), nullable=False)
    phase_id = Column(String(50), ForeignKey("project_phases.id"), nullable=True)
    flag_id = Column(String(50), ForeignKey("project_flags.id"), nullable=True)
    
    daily_entry = relationship("LogDailySummary", back_populates="project_hours")