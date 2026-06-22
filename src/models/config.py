from sqlalchemy import Column, Integer, Float
from src.database import Base

class VacationRule(Base):
    __tablename__ = "config_vacation_rules"
    
    id = Column(Integer, primary_key=True)
    min_years = Column(Integer)    # 0
    max_years = Column(Integer)    # 4
    days = Column(Float)           # 24.0