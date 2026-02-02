# services/team_service.py
from sqlalchemy.orm import Session
from models.team import Team
from schemas.team import TeamCreate, TeamUpdate

def create_team(db: Session, team_data: TeamCreate):
    db_team = Team(**team_data.model_dump())
    db.add(db_team)
    db.commit()
    db.refresh(db_team)
    return db_team

def update_team(db: Session, team_id: int, team_data: TeamUpdate):
    db_team = db.query(Team).filter(Team.id == team_id).first()
    if not db_team:
        return None
    
    update_dict = team_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(db_team, key, value)
    
    db.commit()
    db.refresh(db_team)
    return db_team