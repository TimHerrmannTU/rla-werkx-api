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

class DailyLogSchema(BaseModel):
    date: date
    meta: CalendarDaySchema

    status: str
    status_target_factor: float
    general_note: Optional[str] = None
    
    total_hours: Optional[float] = 0.0
    project_hours: List[ProjectLogSchema] = []
    timeframes_work: List[TimeframeSchema] = []
    timeframes_break: List[TimeframeSchema] = []

    class Config: from_attributes = True