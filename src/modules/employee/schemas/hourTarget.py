from pydantic import BaseModel
from typing import Optional, List
from datetime import date

class EmployeeHourTargetRead(BaseModel):
    id: int
    employee_id: str
    weekly_target: float
    target_spread: List[float]
    starting_balance: float
    valid_start: Optional[date] = None
    valid_stop: Optional[date] = None

    class Config: from_attributes = True

class EmployeeHourTargetCreate(BaseModel):
    weekly_target: float
    target_spread: List[float]
    starting_balance: float = 0.0
    valid_start: Optional[date] = None
    valid_stop: Optional[date] = None

class EmployeeHourTargetUpdate(BaseModel):
    weekly_target: Optional[float] = None
    target_spread: Optional[List[float]] = None
    starting_balance: Optional[float] = None
    valid_start: Optional[date] = None
    valid_stop: Optional[date] = None