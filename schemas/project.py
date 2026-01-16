from pydantic import BaseModel
from typing import Optional, List, Dict

class FlagSchema(BaseModel):
    id: str
    name: str
    color: Optional[str] = None
    time_budget: Optional[float] = None

    total_hours: float = 0.0
    hours_per_emp: Dict[str, float] = {}
    
    class Config: from_attributes = True

class PhaseSchema(BaseModel):
    id: str
    name: str
    phase: Optional[str] = None
    
    total_hours: float = 0.0
    hours_per_emp: Dict[str, float] = {}

    class Config: from_attributes = True

class ProjectSchema(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    active: bool
    
    class Config:from_attributes = True

class ProjectDetailedSchema(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    active: bool

    total_hours: float = 0.0
    hours_per_emp: Dict[str, float] = {}
    
    # Nested Lists (for detailed view)
    phases: List[PhaseSchema] = []
    flags: List[FlagSchema] = []
    
    class Config:from_attributes = True