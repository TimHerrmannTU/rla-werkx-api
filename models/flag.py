from sqlalchemy import Column, Integer, String, Float, ForeignKey, select, func
from sqlalchemy.orm import relationship, column_property
from database import Base

class TimeProperty(Base):
    """
    Mapping for 'stundeneigenschaften' to calculate sums.
    We don't need a full model if we only aggregate, but it helps SQLAlchemy know the table exists.
    """
    __tablename__ = "stundeneigenschaften"
    id = Column("id", Integer, primary_key=True)
    flag_id = Column("tag", Integer, ForeignKey("stundentags.id"))
    time = Column("zeit", Float)

class Flag(Base):
    __tablename__ = "stundentags"

    id = Column("id", Integer, primary_key=True)
    project_id = Column("projekt", String(50), ForeignKey("projekte.kuerzel"))
    name = Column("name", String(255))
    phase = Column("phase", String(50))
    color = Column("farbe", String(50))
    time_budget = Column("budget", Float)
    
    linked_partial = Column("kopplung_to", String(255))
    linked_service = Column("kopplung_weitere_leistung", String(255))

    # Calculated Field: (SELECT SUM(zeit) FROM stundeneigenschaften WHERE tag = id)
    time_total = column_property(
        select(func.sum(TimeProperty.time))
        .where(TimeProperty.flag_id == id)
        .correlate_except(TimeProperty)
        .scalar_subquery()
    )

    project = relationship("Project", back_populates="flags")