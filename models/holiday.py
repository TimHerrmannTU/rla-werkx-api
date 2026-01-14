from sqlalchemy import Column, String, Float
from database import Base

class Holiday(Base):
    __tablename__ = "feiertage"

    date_str = Column("datum", String(9), primary_key=True)
    name     = Column("name", String(100))
    region   = Column("region", String(1))
    target_factor = Column("sollfaktor", Float)