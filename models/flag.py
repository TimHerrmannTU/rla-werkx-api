from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship
from database import Base

class Flag(Base):
    __tablename__ = "stundentags"

    id        = Column("id", Integer, primary_key=True)
    parent_id = Column("projekt", String(50))
    desc      = Column("name", String(255))
    phase     = Column("phase", String(50))
    partial   = Column("teilobjekt", String(100))
    color     = Column("farbe", String(50))
    time_budget = Column("budget", Float)
    linked_partial = Column("kopplung_to", String(100))
    linked_service = Column("kopplung_weitere_leistung", String(100))

    project = relationship(
        "Project",
        back_populates="flags",
        primaryjoin="Flag.parent_id == Project.id",
        foreign_keys="[Flag.parent_id]" # Mark this column as the foreign key
    )