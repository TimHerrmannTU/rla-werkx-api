from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.database import get_db

from src.crud.projectFlag import flag_crud
from src.schemas.projectFlag import FlagRead, FlagCreate, FlagUpdate

# Nested prefix
router = APIRouter(prefix="/projects/{project_id}/flags", tags=["Flags"])

@router.get("/", response_model=list[FlagRead])
def get_project_flags(project_id: str, db: Session = Depends(get_db)):
    # Note: CRUD should filter by project_id to ensure isolation
    return flag_crud.get_by_project(db, project_id)

@router.post("/", response_model=FlagRead, status_code=status.HTTP_201_CREATED)
def create_project_flag(project_id: str, flag_in: FlagCreate, db: Session = Depends(get_db)):
    return flag_crud.create_with_project(db, flag_in, project_id)

@router.patch("/{flag_id}", response_model=FlagRead)
def update_project_flag(project_id: str, flag_id: str, flag_in: FlagUpdate, db: Session = Depends(get_db)):
    db_flag = flag_crud.get(db, flag_id)
    if not db_flag or db_flag.project_id != project_id:
        raise HTTPException(404, "Flag not found in this project")
    return flag_crud.update(db, db_flag, flag_in)

@router.delete("/{flag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project_flag(project_id: str, flag_id: str, db: Session = Depends(get_db)):
    db_flag = flag_crud.get(db, flag_id)
    if not db_flag or db_flag.project_id != project_id:
        raise HTTPException(404, "Flag not found in this project")
    flag_crud.delete(db, flag_id)
    return None