from pydantic import BaseModel
from typing import Optional, List
from schemas.flag import FlagBase
from schemas.phase import PhaseBase

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