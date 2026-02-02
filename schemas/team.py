from pydantic import BaseModel
from typing import Optional

class TeamRead(BaseModel):
    id: Optional[int] = None
    name: str
    lead_id: str
    
    class Config: from_attributes = True

class TeamCreate(BaseModel):
    name: str
    lead_id: str

class TeamUpdate(BaseModel):
    name: Optional[str] = None
    lead_id: Optional[str] = None