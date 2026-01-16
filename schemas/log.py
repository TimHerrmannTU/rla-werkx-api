from pydantic import BaseModel
from typing import List, Optional
from datetime import date, time

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
    status: str
    status_target_factor: float
    general_note: Optional[str] = None
    
    project_hours: List[ProjectLogSchema] = []
    timeframes_work: List[TimeframeSchema] = []
    timeframes_break: List[TimeframeSchema] = []

    class Config: from_attributes = True