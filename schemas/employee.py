from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import date

class ContractSchema(BaseModel):
    id: int
    weekly_target: float
    target_spread: List[float] # [1.0, 1.0...]
    valid_start: date
    valid_stop: Optional[date]

    class Config: from_attributes = True

class EmployeeSchema(BaseModel):
    id: str
    name: str
    birthday: Optional[date]
    entry_date: Optional[date]
    active: bool
    contracts: List[ContractSchema] = [] # If needed
    
    class Config: from_attributes = True