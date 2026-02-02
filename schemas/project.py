from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import date, time

class FlagRead(BaseModel):
    id: str
    name: str
    color: Optional[str] = None
    
    class Config: from_attributes = True

class FlagDetailedView(FlagRead):
    time_budget: Optional[float] = None
    total_hours: float = 0.0
    hours_per_emp: Dict[str, float] = {}

    class Config: from_attributes = True


class PhaseRead(BaseModel):
    id: str
    name: str
    phase: Optional[str] = None
    
    class Config: from_attributes = True

class PhaseDetailedView(PhaseRead):
    total_hours: float = 0.0
    hours_per_emp: Dict[str, float] = {}
    
    class Config: from_attributes = True

class ProjectRead(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    active: bool
    
    class Config:from_attributes = True


class ProjectDetailedView(ProjectRead):
    phases: List[PhaseRead] = []
    flags: List[FlagRead] = []
    
    class Config:from_attributes = True


class ProjectDashboardView(ProjectRead):
    phases: List[PhaseDetailedView] = []
    flags: List[FlagDetailedView] = []

    total_hours: float = 0.0
    timeline: dict[date, float] = {}
    hours_per_emp: Dict[str, float] = {}
    emp_map: Dict[str, str] = {}
    
    class Config:from_attributes = True