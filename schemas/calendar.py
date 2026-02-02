from pydantic import BaseModel
from datetime import date
from typing import Optional

from schemas.location import LocationRead

class HolidayRead(BaseModel):
    id: int
    date: date
    name: str
    location: str
    target_factor: float
    is_company_holiday: bool
    location: LocationRead
    
    class Config: from_attributes = True

class CalendarDayRead(BaseModel):
    date: date
    year: int
    month: int
    day: int
    weekday: int
    is_weekend: bool
    holiday: Optional[HolidayRead] = None
    
    class Config: from_attributes = True