from pydantic import BaseModel
from typing import Optional, List

class FlagSchema(BaseModel):
    id: str
    name: str
    color: Optional[str] = None
    time_budget: Optional[float] = None
    
    class Config: from_attributes = True

class PhaseSchema(BaseModel):
    id: str
    name: str
    phase: Optional[str] = None

    class Config: from_attributes = True

class ProjectSchema(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    active: bool
    
    # Nested Lists (for detailed view)
    phases: List[PhaseSchema] = []
    flags: List[FlagSchema] = [] 
    
    class Config:from_attributes = True