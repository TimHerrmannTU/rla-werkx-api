from pydantic import BaseModel, Field
from typing import Optional

class ProjectResponse(BaseModel):
    # JSON field name : Python type
    id:          str
    name_short:  str
    name_long:   Optional[str] = None
    parent_id:   Optional[str] = None
    hour_limit:  Optional[int] = None
    phase:       Optional[int] = None

    class Config:
        from_attributes = True  