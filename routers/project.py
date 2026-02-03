# routers/projects.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db

from crud.project import project_crud
import services.project as project_service
from schemas.project import ProjectRead, ProjectCreate, ProjectUpdate, ProjectDetailedView

router = APIRouter(prefix="/projects", tags=["Projects"])

##################
# CRUD ENDPOINTS #
##################

@router.get("/", response_model=list[ProjectRead])
def get_project_list(db: Session = Depends(get_db)):
    pros =  project_crud.get_all(db)
    if not pros: 
        raise HTTPException(404, "Project not found")
    return pros

@router.get("/{project_id}", response_model=ProjectRead)
def get_project_single(project_id: str, db: Session = Depends(get_db)):
    pro = project_crud.get(db, project_id)
    if not pro: 
        raise HTTPException(404, "Project not found")
    return pro

@router.post("/", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def create_new_project(project_in: ProjectCreate, db: Session = Depends(get_db)):
    return project_crud.create(db, project_in)

@router.patch("/{project_id}", response_model=ProjectRead)
def update_existing_project(project_id: str, project_in: ProjectUpdate, db: Session = Depends(get_db)):
    db_project = project_crud.get(db, project_id)
    if not db_project:
        raise HTTPException(404, "Project not found")
    return project_crud.update(db, db_project, project_in)

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: str, db: Session = Depends(get_db)):
    success = project_crud.delete(db, project_id)
    if not success:
        raise HTTPException(404, "Project not found")
    return None


##################
# VIEW ENDPOINTS #
##################

@router.get("/detailed/{project_id}/", response_model=ProjectDetailedView)
def get_project_single_long(project_id: str, db: Session = Depends(get_db)):
    pro = project_crud.get_detailed(db, project_id)
    if not pro: 
        raise HTTPException(404, "Project not found")
    return pro

@router.get("/detailed", response_model=list[ProjectDetailedView])
def get_project_list_long(db: Session = Depends(get_db)):
    pros = project_crud.get(db)
    if not pros:
        raise HTTPException(404, "Project not found")
    return pros