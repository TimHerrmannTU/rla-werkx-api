from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import date

from schemas.location import LocationRead
from schemas.team import TeamRead

class ContractRead(BaseModel):
    weekly_target: float
    target_spread: List[float] # [1.0, 1.0...]
    valid_start: Optional[date]
    valid_stop: Optional[date]
    starting_balance: Optional[float]

    class Config: from_attributes = True

class HolidayClaimRead(BaseModel):
    year: Optional[int]
    days: float
    
    class Config: from_attributes = True

class EmployeeRead(BaseModel):
    id: str
    name: str
    birthday: Optional[date]
    entry_date: Optional[date]
    location: LocationRead
    team_led: List[TeamRead] = []
    color: str
    active: bool
    
    class Config: from_attributes = True

class EmployeeDetailedView(BaseModel):
    id: str
    name: str
    birthday: Optional[date]
    entry_date: Optional[date]
    location: LocationRead
    color: str
    active: bool
    hour_targets: List[ContractRead] = [] # If needed
    vacation_claims: List[HolidayClaimRead] = []
    
    class Config: from_attributes = True