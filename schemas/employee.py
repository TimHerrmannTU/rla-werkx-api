from pydantic import BaseModel, BeforeValidator
from typing import Optional, Annotated
from datetime import date, datetime

def parse_legacy_date(v):
    if v is None: return None # gate
    if isinstance(v, date): return v
    if isinstance(v, str) and v.startswith("d") and len(v) == 9:
        try:
            return datetime.strptime(v, "d%Y%m%d").date()
        except ValueError:
            return None
    return None
LegacyDate = Annotated[Optional[date], BeforeValidator(parse_legacy_date)]

class EmployeeSchema(BaseModel):
    id: str
    name: str
    target_hours: Optional[float] = None
    total_hours: Optional[float] = None
    entry_date: LegacyDate = None
    exit_date: LegacyDate = None
    is_active: bool

    class Config:
        from_attributes = True