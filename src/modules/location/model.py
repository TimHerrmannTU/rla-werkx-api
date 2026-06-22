from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship
from src.core.database import Base

class Location(Base):
    __tablename__ = "locations"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50))

    # relationships
    employees = relationship("Employee", back_populates="location")
    holidays  = relationship("Holiday",  back_populates="location")