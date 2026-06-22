from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import date

from src.modules.location.schema import LocationRead
from src.modules.team.schema import TeamRead

################
# CRUD SCHEMAS #
################

class EmployeeRead(BaseModel):
    id: str
    name: str
    email: Optional[str] = None
    birthday: Optional[date]
    entry_date: Optional[date]
    location: LocationRead
    team_id: Optional[int] = None
    team_led: List[TeamRead] = []
    color: str
    active: bool
    
    class Config: from_attributes = True

class EmployeeCreate(BaseModel):
    id: str
    name: str
    birthday: Optional[date] = None
    entry_date: Optional[date] = None
    location_id: int
    color: str = "#ffffff"
    active: bool = True

class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    birthday: Optional[date] = None
    entry_date: Optional[date] = None
    location_id: Optional[int] = None
    color: Optional[str] = None
    active: Optional[bool] = None

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

################
# VIEW SCHEMAS #
################

class EmployeeDetailedView(EmployeeRead):
    hour_targets: List[ContractRead] = [] # If needed
    vacation_claims: List[HolidayClaimRead] = []
    
    class Config: from_attributes = True
