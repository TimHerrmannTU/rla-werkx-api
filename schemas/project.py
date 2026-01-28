from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import date, time

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

class ProjectDetailedSchema(ProjectSchema):
    phases: List[PhaseSchema] = []
    flags: List[FlagSchema] = []
    
    class Config:from_attributes = True

class ProjectDashboardSchema(ProjectDetailedSchema):
    total_hours: float = 0.0
    timeline: dict[date, float] = {}
    hours_per_emp: Dict[str, float] = {}
    emp_map: Dict[str, str] = {}
    
    class Config:from_attributes = True