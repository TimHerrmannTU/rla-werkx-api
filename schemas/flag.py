from pydantic import BaseModel
from typing import Optional

class FlagSchema(BaseModel):
    id: int
    name: str
    phase: Optional[str] = None
    color: Optional[str] = None
    time_budget: Optional[float] = None
    linked_partial: Optional[str] = None
    linked_service: Optional[str] = None
    
    # Read-only sum
    time_total: Optional[float] = 0.0

    class Config:
        from_attributes = True