from pydantic import BaseModel
from typing import Dict, Optional

class PhaseBase(BaseModel):
    id: str
    parent_id: str
    name: str
    desc: Optional[str] = None
    time_budget: Optional[float] = None
    linked_phase: Optional[str] = None

    class Config:
        from_attributes = True

class PhaseDetail(PhaseBase):
    total_hours: float = 0.0
    hours_per_emp: Dict[str, float] = {}