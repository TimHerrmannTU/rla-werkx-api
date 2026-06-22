from sqlalchemy import Column, Integer, String, Text, Date, Float, Boolean, ForeignKey, JSON, Time, UniqueConstraint
from sqlalchemy.orm import relationship

from src.core.database import Base

# PROJECT STUFF #
class Project(Base):
    __tablename__ = "projects"
    
    id = Column(String(50), primary_key=True)
    creation_date = Column(Date, nullable=True)
    
    name = Column(String(255))
    color = Column(String(50))
    active = Column(Boolean)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)
    
    team = relationship("Team", back_populates="projects")
    phases = relationship("ProjectPhase", back_populates="project")
    flags = relationship("ProjectFlag", back_populates="project")
    partials = relationship("ProjectPartial", back_populates="project")
    services = relationship("ProjectService", back_populates="project")

class ProjectPhase(Base):
    __tablename__ = "project_phases"
    
    id = Column(String(50), primary_key=True)
    name = Column(String(255))
    phase = Column(String(50))
    project_id = Column(String(50), ForeignKey("projects.id"))

    project = relationship("Project", back_populates="phases")

class ProjectPartial(Base):
    __tablename__ = "project_partials"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    project_id = Column(String(50), ForeignKey("projects.id"))
    # a bunch of columns are excluded for now

    project = relationship("Project", back_populates="partials")

class ProjectService(Base): # how is this significantly different from TOs?
    __tablename__ = "project_services"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    project_id = Column(String(50), ForeignKey("projects.id"))

    project = relationship("Project", back_populates="services")

class ProjectFlag(Base):
    __tablename__ = "project_flags"
    
    id = Column(String(50), primary_key=True) # e.g. "ZWH_F1" or legacy ID cast to string?
    name = Column(String(255))
    color = Column(String(50))
    project_id = Column(String(50), ForeignKey("projects.id"))
    phase = Column(String(50), nullable=True) # "1", "2" or NULL
    time_budget = Column(Float)
    
    # Links
    linked_partial_id = Column(Integer, ForeignKey("project_partials.id"), nullable=True)
    linked_service_id = Column(Integer, ForeignKey("project_services.id"), nullable=True)

    project = relationship("Project", back_populates="flags")
