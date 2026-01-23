from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import date

from schemas.location import LocationSchema

class ContractSchema(BaseModel):
    weekly_target: float
    target_spread: List[float] # [1.0, 1.0...]
    valid_start: Optional[date]
    valid_stop: Optional[date]
    starting_balance: Optional[float]

    class Config: from_attributes = True

class HolidayClaimSchema(BaseModel):
    year: Optional[int]
    days: float
    
    class Config: from_attributes = True

class EmployeeSchema(BaseModel):
    id: str
    name: str
    birthday: Optional[date]
    entry_date: Optional[date]
    location: LocationSchema
    color: str
    active: bool
    
    class Config: from_attributes = True

class EmployeeDetailedSchema(BaseModel):
    id: str
    name: str
    birthday: Optional[date]
    entry_date: Optional[date]
    location: LocationSchema
    color: str
    active: bool
    hour_targets: List[ContractSchema] = [] # If needed
    vacation_claims: List[HolidayClaimSchema] = []
    
    class Config: from_attributes = True