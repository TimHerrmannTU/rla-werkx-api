from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Team(Base):
    __tablename__ = "teams"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(20))
    lead_id = Column(String(5), ForeignKey("employees.id"))

    projects = relationship("Project", back_populates="team")
    members = relationship("Employee", back_populates="team", foreign_keys="[Employee.team_id]")
    lead = relationship("Employee", back_populates="team_led", foreign_keys=[lead_id])