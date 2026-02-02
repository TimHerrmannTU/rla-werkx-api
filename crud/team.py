from sqlalchemy.orm import Session
from models.team import Team
from schemas.team import TeamCreate, TeamUpdate

def get(db: Session, team_id: int):
    return db.query(Team).filter(Team.id == team_id).first()

def create(db: Session, schema: TeamCreate):
    db_obj = Team(**schema.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update(db: Session, db_obj: Team, schema: TeamUpdate):
    data = schema.model_dump(exclude_unset=True)
    for field in data:
        setattr(db_obj, field, data[field])
    db.commit()
    db.refresh(db_obj)
    return db_obj

def delete_team(db: Session, team_id: int):
    db_obj = db.query(Team).filter(Team.id == team_id).first()
    if db_obj:
        db.delete(db_obj)
        db.commit()
    return db_obj