from pydantic import BaseModel
from typing import Optional
from utils.validators import LegacyDate

class EmployeeBase(BaseModel):
    id: str
    name: str
    target_hours: Optional[float] = None
    total_hours: Optional[float] = None
    entry_date: LegacyDate = None
    exit_date: LegacyDate = None
    is_active: bool

    class Config:
        from_attributes = True