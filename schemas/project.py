from pydantic import BaseModel, BeforeValidator
from typing import Optional, Annotated

def clean_int(v):
    if v is None: return None # gate
    try: 
        return int(v)
    except (ValueError, TypeError):
        return None

SafeInt = Annotated[Optional[int], BeforeValidator(clean_int)]

class ProjectSchema(BaseModel):
    # JSON field name : Python type = fallback
    id:          str
    name_short:  str
    name_long:   Optional[str] = None
    parent_id:   Optional[str] = None
    hour_limit:  Optional[float] = None
    phase:       SafeInt = None

    class Config:
        from_attributes = True  