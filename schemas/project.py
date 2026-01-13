from pydantic import BaseModel
from typing import Optional, List
from schemas.flag import FlagSchema
from schemas.phase import PhaseSchema

class ProjectBase(BaseModel):
    id: str
    parent_id: Optional[str] = None
    desc:  Optional[str] = None 
    color: Optional[str] = None 

    class Config:
        from_attributes = True
        populate_by_name = True

class ProjectSummary(ProjectBase):
    pass

class ProjectDetail(ProjectBase):
    phases: List[PhaseSchema] = []
    flags: List[FlagSchema] = []