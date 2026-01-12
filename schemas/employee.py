from pydantic import BaseModel
from typing import Optional
from datetime import date

class EmployeeSchema(BaseModel):
    id: str
    name: str
    target_hours: Optional[float] = None
    total_hours: Optional[float] = None
    entry_date: Optional[date] = None
    exit_date: Optional[date] = None
    is_active: bool

    class Config:
        from_attributes = True