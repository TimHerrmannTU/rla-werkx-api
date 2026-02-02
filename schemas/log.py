from pydantic import BaseModel
from typing import List, Optional
from datetime import date, time

################
# CRUD SCHEMAS #
################

class TimeframeRead(BaseModel):
    id: int
    start: Optional[time]
    stop: Optional[time]
    is_break: bool

    class Config: from_attributes = True

class ProjectLogRead(BaseModel):
    id: int
    time: float
    project_id: str
    phase_id: Optional[str] = None
    flag_id: Optional[str] = None
    note: Optional[str] = None
    
    class Config: from_attributes = True

class DailyLogRead(BaseModel):
    id: int
    date: date
    employee_id: str
    status: str
    status_target_factor: float
    status_note: Optional[str] = None
    general_note: Optional[str] = None
    target_hours: float
    
    project_hours: List[ProjectLogRead] = []
    timeframes: List[TimeframeRead] = []

    class Config: from_attributes = True

################
# SYNC SCHEMAS #
################

class TimeframeSync(BaseModel):
    id: Optional[int] = None # If null: CREATE, else: UPDATE
    start: time
    stop: time
    is_break: bool = False

class ProjectHourSync(BaseModel):
    id: Optional[int] = None # If null: CREATE, else: UPDATE
    time: float
    project_id: str
    phase_id: Optional[str] = None
    flag_id: Optional[str] = None
    note: Optional[str] = None

class DailyLogSync(BaseModel):
    id: Optional[int] = None
    date: date
    employee_id: str
    
    status: str = "A"
    status_target_factor: float = 1.0
    status_note: Optional[str] = None
    general_note: Optional[str] = None
    target_hours: float
    
    project_hours: List[ProjectHourSync] = []
    timeframes: List[TimeframeSync] = []

    class Config: from_attributes = True

class DailyLogBatchSync(BaseModel):
    logs: List[DailyLogSync]

################
# VIEW SCHEMAS #
################

class MonthView(BaseModel):
    meta: dict # Or specific MonthStats schema
    days: List[DailyLogRead]