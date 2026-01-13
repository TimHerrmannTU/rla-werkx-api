from pydantic import BaseModel
from typing import Optional

class PhaseSchema(BaseModel):
    id: str
    parent_id: str
    name: str
    desc: Optional[str] = None
    time_budget: Optional[float] = None
    linked_phase: Optional[str] = None

    class Config:
        from_attributes = True