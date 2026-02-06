# schemas/phase.py
from pydantic import BaseModel
from typing import Optional, Dict

################
# CRUD SCHEMAS #
################

class PhaseRead(BaseModel):
    id: str
    name: Optional[str] = None
    phase: Optional[str] = None
    
    class Config: from_attributes = True

class PhaseCreate(BaseModel):
    id: str
    name: str
    phase: Optional[str] = None

class PhaseUpdate(BaseModel):
    name: Optional[str] = None
    phase: Optional[str] = None

################
# VIEW SCHEMAS #
################

class PhaseDetailedView(PhaseRead):
    total_hours: float = 0.0
    hours_per_emp: Dict[str, float] = {}
    
    class Config: from_attributes = True