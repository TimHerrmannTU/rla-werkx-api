# routers/teams.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from schemas.team import TeamCreate, TeamRead, TeamUpdate
from services import team_service

router = APIRouter(prefix="/teams", tags=["teams"])

@router.post("/", response_model=TeamRead, status_code=status.HTTP_201_CREATED)
def create_new_team(team_in: TeamCreate, db: Session = Depends(get_db)):
    return team_service.create_team(db, team_in)

@router.patch("/{team_id}", response_model=TeamRead)
def update_existing_team(team_id: int, team_in: TeamUpdate, db: Session = Depends(get_db)):
    team = team_service.update_team(db, team_id, team_in)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team