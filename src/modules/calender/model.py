from sqlalchemy import Column, Integer, String, Text, Date, Float, Boolean, ForeignKey, JSON, Time, UniqueConstraint
from sqlalchemy.orm import relationship

from src.core.database import Base

class CalendarDay(Base):
    __tablename__ = "calendar_days"
    
    date = Column(Date, primary_key=True)
    year = Column(Integer)
    month = Column(Integer)
    day = Column(Integer)
    weekday = Column(Integer) # 0=Mon
    week_number = Column(Integer)
    is_weekend = Column(Boolean)

    holiday = relationship("Holiday", back_populates="calendar_day", uselist=False)

class Holiday(Base):
    __tablename__ = "calendar_holidays"
    
    id = Column(Integer, primary_key=True) 
    date = Column(Date, ForeignKey("calendar_days.date"))
    name = Column(String(100))
    target_factor = Column(Float, default=0.0)
    is_company_holiday = Column(Boolean, default=False)
    location_id = Column(Integer, ForeignKey("locations.id"))

    location = relationship("Location", back_populates="holidays")
    calendar_day = relationship("CalendarDay", back_populates="holiday")