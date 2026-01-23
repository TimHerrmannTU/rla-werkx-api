from pydantic import BaseModel
from typing import List, Optional
from datetime import date, time

from schemas.calendar import CalendarDaySchema

class TimeframeSchema(BaseModel):
    start: Optional[time]
    stop: Optional[time]

    class Config: from_attributes = True

class ProjectLogSchema(BaseModel):
    id: int
    time: float
    project_id: str
    phase_id: Optional[str] = None
    flag_id: Optional[str] = None
    note: Optional[str] = None
    
    class Config: from_attributes = True

class DailyViewSchema(BaseModel):
    date: date
    meta: CalendarDaySchema # Nested Calendar Data
    
    status: str
    status_target_factor: float
    note: Optional[str] = None
    
    target_hours: float
    total_hours: float
    
    project_hours: List[ProjectLogSchema] = []
    timeframes_work: List[TimeframeSchema] = []
    timeframes_break: List[TimeframeSchema] = []

    class Config: from_attributes = True

class MonthViewSchema(BaseModel):
    meta: dict # Or specific MonthStats schema
    days: List[DailyViewSchema]