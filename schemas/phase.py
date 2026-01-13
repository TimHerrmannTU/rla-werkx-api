from pydantic import BaseModel
from typing import Optional

class FlagSchema(BaseModel):
    id: str
    name: str
    desc: Optional[str] = None
    time_budget: Optional[str] = None
    linked_phase: Optional[str] = None

    class Config:
        from_attributes = True