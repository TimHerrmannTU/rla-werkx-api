from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db

from crud.projectPhase import phase_crud
from schemas.projectPhase import PhaseRead, PhaseCreate, PhaseUpdate

router = APIRouter(prefix="/projects/{project_id}/phases", tags=["Phases"])

@router.get("/", response_model=list[PhaseRead])
def get_project_phases(project_id: str, db: Session = Depends(get_db)):
    return phase_crud.get_by_project(db, project_id)

@router.post("/", response_model=PhaseRead, status_code=status.HTTP_201_CREATED)
def create_project_phase(project_id: str, phase_in: PhaseCreate, db: Session = Depends(get_db)):
    return phase_crud.create_with_project(db, phase_in, project_id)

@router.patch("/{phase_id}", response_model=PhaseRead)
def update_project_phase(project_id: str, phase_id: str, phase_in: PhaseUpdate, db: Session = Depends(get_db)):
    db_phase = phase_crud.get(db, phase_id)
    if not db_phase or db_phase.project_id != project_id:
        raise HTTPException(404, "Phase not found in this project")
    return phase_crud.update(db, db_phase, phase_in)

@router.delete("/{phase_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project_phase(project_id: str, phase_id: str, db: Session = Depends(get_db)):
    db_phase = phase_crud.get(db, phase_id)
    if not db_phase or db_phase.project_id != project_id:
        raise HTTPException(404, "Phase not found in this project")
    phase_crud.delete(db, phase_id)
    return None