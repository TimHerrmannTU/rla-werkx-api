from pydantic import BaseModel
from typing import Optional, List, Dict
from schemas.flag import FlagBase
from schemas.phase import PhaseBase, PhaseDetail

class ProjectBase(BaseModel):
    id: str
    parent_id: Optional[str] = None
    desc:  Optional[str] = None 
    color: Optional[str] = None 

    class Config:
        from_attributes = True
        populate_by_name = True

class ProjectDetail(ProjectBase):
    phases: List[PhaseBase] = []
    flags: List[FlagBase] = []

class ProjectHours(ProjectBase):
    total_hours: float = 0.0
    hours_per_emp: Dict[str, float] = {}
    
    phases: List[PhaseDetail] = []
    flags: List[FlagBase] = []