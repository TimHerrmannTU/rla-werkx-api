from pydantic import BaseModel
from typing import List, Optional
from datetime import date, time

from schemas.calendar import CalendarDayRead

class TimeframeRead(BaseModel):
    start: Optional[time]
    stop: Optional[time]

    class Config: from_attributes = True

class ProjectLogRead(BaseModel):
    id: int
    time: float
    project_id: str
    phase_id: Optional[str] = None
    flag_id: Optional[str] = None
    note: Optional[str] = None
    
    class Config: from_attributes = True

class DailyView(BaseModel):
    date: date
    meta: CalendarDayRead # Nested Calendar Data
    
    status: str
    status_target_factor: float
    note: Optional[str] = None
    
    target_hours: float
    total_hours: float
    
    project_hours: List[ProjectLogRead] = []
    timeframes_work: List[TimeframeRead] = []
    timeframes_break: List[TimeframeRead] = []

    class Config: from_attributes = True

class MonthView(BaseModel):
    meta: dict # Or specific MonthStats schema
    days: List[DailyView]