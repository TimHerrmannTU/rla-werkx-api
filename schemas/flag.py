from pydantic import BaseModel
from typing import Optional

class FlagSchema(BaseModel):
    id: int
    desc: str
    phase: Optional[str] = None
    partial: Optional[str] = None
    color: Optional[str] = None
    time_budget: Optional[float] = None
    linked_partial: Optional[str] = None
    linked_service: Optional[str] = None

    class Config:
        from_attributes = True