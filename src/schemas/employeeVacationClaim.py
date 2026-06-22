from pydantic import BaseModel
from typing import Optional

class EmployeeVacationClaimRead(BaseModel):
    id: int
    employee_id: str
    year: int
    days: float

    class Config: from_attributes = True

class EmployeeVacationClaimCreate(BaseModel):
    year: int
    days: float

class EmployeeVacationClaimUpdate(BaseModel):
    year: Optional[int] = None
    days: Optional[float] = None