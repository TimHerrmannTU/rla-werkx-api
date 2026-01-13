from sqlalchemy import Float, Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from database import Base

class Project(Base):
    __tablename__ = "projektgruppen"

    # Python Attribute = Column("DB_COLUMN_NAME", Type)
    id        = Column("kuerzel", String(50), primary_key=True) 
    desc      = Column("voller_name", String(255))
    parent_id = Column("parent", String(50))
    # phases    = relationship("Flag", back_populates="project") # replace with phase
    flags = relationship(
        "Flag", 
        back_populates="project",
        primaryjoin="foreign(Flag.parent_id) == remote(Project.id)",
        lazy="select" 
    )