from sqlalchemy import Float, Column, Integer, String, Boolean
from database import Base

class Project(Base):
    __tablename__ = "projekte"

    # Python Attribute = Column("DB_COLUMN_NAME", Type)
    id          = Column("kuerzel", String(50), primary_key=True) 
    name_short  = Column("name", String(255))
    name_long   = Column("voller_name", String(255))
    parent_id   = Column("projekt", String(50)) # link to 'ProjektGruppe'
    hour_limit  = Column("stundenlimit", Float)
    phase       = Column("leistungsphase", String(100))