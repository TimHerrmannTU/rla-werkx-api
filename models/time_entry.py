from sqlalchemy import Column, Integer, String, Float, ForeignKey
from database import Base

class TimeEntry(Base):
    __tablename__ = "stundeneigenschaften"

    id = Column(Integer, primary_key=True)
    emp_id = Column("mitarbeiter", String(5))
    phase_id = Column("projekt", String(50))
    date_str = Column("datum", String(9)) # Legacy date
    note = Column("notiz", String(500))
    hours = Column("zeit", Float)
    tag = Column("tag", Integer) # TODO figure out wtf this is