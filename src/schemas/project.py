# schemas/project.py
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import date
from .projectPhase import PhaseRead, PhaseDetailedView
from .projectFlag import FlagRead, FlagDetailedView

################
# CRUD SCHEMAS #
################

class ProjectRead(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    color: Optional[str] = None
    active: bool
    creation_date: Optional[date] = None
    team_id: Optional[int] = None
    
    class Config: from_attributes = True

class ProjectCreate(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    color: Optional[str] = None
    active: bool = True
    creation_date: Optional[date] = None
    team_id: Optional[int] = None

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None
    active: Optional[bool] = None
    creation_date: Optional[date] = None
    team_id: Optional[int] = None

################
# VIEW SCHEMAS #
################

class ProjectDetailedView(ProjectRead):
    phases: List[PhaseRead] = []
    flags: List[FlagRead] = []
    
    class Config: from_attributes = True

class ProjectDashboardView(ProjectRead):
    phases: List[PhaseDetailedView] = []
    flags: List[FlagDetailedView] = []
    total_hours: float = 0.0
    timeline: Dict[date, float] = {}
    hours_per_emp: Dict[str, float] = {}
    emp_map: Dict[str, str] = {}
    
    class Config: from_attributes = True