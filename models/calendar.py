from sqlalchemy import Column, Integer, String, Text, Date, Float, Boolean, ForeignKey, JSON, Time, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# CALENDAR STUFF #
class CalendarDay(Base):
    __tablename__ = "calendar_days"
    
    date = Column(Date, primary_key=True)
    year = Column(Integer)
    month = Column(Integer)
    day = Column(Integer)
    weekday = Column(Integer) # 0=Mon
    week_number = Column(Integer)
    is_weekend = Column(Boolean)

class Holiday(Base):
    __tablename__ = "calendar_holidays"
    
    id = Column(Integer, primary_key=True) 
    date = Column(Date, ForeignKey("calendar_days.date"))
    name = Column(String(100))
    region = Column(String(5))
    target_factor = Column(Float, default=0.0)
    is_company_holiday = Column(Boolean, default=False)
