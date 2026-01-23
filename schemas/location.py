from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import date

class LocationSchema(BaseModel):
    id: int
    name: str

    class Config: from_attributes = True