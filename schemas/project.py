from pydantic import BaseModel, Field, BeforeValidator
from typing import Optional, Annotated, Union, List
from schemas.flag import FlagSchema

def clean_int(v):
    if v is None: return None # gate
    try: 
        return int(v)
    except (ValueError, TypeError):
        return None

SafeInt = Annotated[Optional[int], BeforeValidator(clean_int)]

class ProjectBase(BaseModel):
    id: str
    parent_id: Optional[str] = None
    name_long: Optional[str] = Field(default=None, alias="full_name") 
    phase: SafeInt = None
    color: Optional[str] = None 

    class Config:
        from_attributes = True
        populate_by_name = True

class ProjectSummary(ProjectBase):
    pass

class ProjectDetail(ProjectBase):
    flags: List[FlagSchema] = []