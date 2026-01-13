from sqlalchemy import Column, String, Float
from sqlalchemy.orm import relationship
from database import Base

class Phase(Base):
    __tablename__ = "projekte"

    id        = Column("kuerzel", String(50), primary_key=True)
    parent_id = Column("projekt", String(50))
    name      = Column("name", String(50))
    desc      = Column("voller_name", String(255))
    time_budget = Column("stundenlimit", Float)
    linked_phase = Column("leistungsphase", String(50))

    project = relationship(
        "Project",
        back_populates="phases",
        primaryjoin="Phase.parent_id == Project.id",
        foreign_keys="[Phase.parent_id]"
    )