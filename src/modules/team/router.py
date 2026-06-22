from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.core.database import get_db

from src.models import Team
from src.modules.team.schema import TeamRead, TeamCreate, TeamRead, TeamUpdate
from src.modules.team.crud import team_crud

router = APIRouter(prefix="/teams", tags=["Teams"])

##################
# CRUD ENDPOINTS #
##################

@router.get("/", response_model=list[TeamRead])
def get_team_list(db: Session = Depends(get_db)):
    return team_crud.get_all(db)

@router.get("/{team_id}", response_model=TeamRead)
def get_team_single(team_id: int, db: Session = Depends(get_db)):
    team = team_crud.get(db, team_id)
    if not team: raise HTTPException(404, "Project not found")
    return team

@router.post("/", response_model=TeamRead, status_code=status.HTTP_201_CREATED)
def create_new_team(team_in: TeamCreate, db: Session = Depends(get_db)):
    return team_crud.get(db, team_in)

@router.patch("/{team_id}", response_model=TeamRead)
def update_existing_team(team_id: int, team_in: TeamUpdate, db: Session = Depends(get_db)):
    team = team_crud.update(db, team_id, team_in)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team

@router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_team(team_id: int, db: Session = Depends(get_db)):
    success = team_crud.delete(db, team_id)
    if not success:
        raise HTTPException(status_code=404, detail="Team not found")
    return None

##################
# VIEW ENDPOINTS #
##################