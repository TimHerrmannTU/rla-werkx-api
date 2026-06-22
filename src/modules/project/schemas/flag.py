# schemas/flag.py
from pydantic import BaseModel
from typing import Optional, Dict

################
# CRUD SCHEMAS #
################

class FlagRead(BaseModel):
    id: str
    name: str
    color: Optional[str] = None
    
    class Config: from_attributes = True

class FlagCreate(BaseModel):
    id: str
    name: str
    color: Optional[str] = None

class FlagUpdate(BaseModel):
    name: Optional[str] = None
    color: Optional[str] = None

################
# VIEW SCHEMAS #
################

class FlagDetailedView(FlagRead):
    time_budget: Optional[float] = None
    total_hours: float = 0.0
    hours_per_emp: Dict[str, float] = {}

    class Config: from_attributes = True