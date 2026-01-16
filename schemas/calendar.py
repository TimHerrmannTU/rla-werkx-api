from pydantic import BaseModel
from datetime import date
from typing import Optional

class HolidaySchema(BaseModel):
    id: int
    date: date
    name: str
    region: str
    target_factor: float
    is_company_holiday: bool
    
    class Config: from_attributes = True

class CalendarDaySchema(BaseModel):
    date: date
    year: int
    month: int
    day: int
    weekday: int
    is_weekend: bool
    holiday: Optional[HolidaySchema] = None
    
    class Config: from_attributes = True