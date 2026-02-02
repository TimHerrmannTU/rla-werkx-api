from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from database import get_db

from models.project import Project
from schemas.project import ProjectRead, ProjectDetailedView

router = APIRouter(prefix="/projects", tags=["Projects"])

##################
# LIST ENDPOINTS #
##################

@router.get("/", response_model=list[ProjectRead])
def get_project_list_short(db: Session = Depends(get_db)):
    """Default: Returns essential data only (Base)."""
    return db.query(Project).order_by(Project.id).all()

@router.get("/detailed", response_model=list[ProjectDetailedView])
def get_project_list_long(db: Session = Depends(get_db)):
    """Detailed: Returns everything + flags/phases."""
    # Eager load both phases and flags
    return db.query(Project).options(
        joinedload(Project.phases),
        joinedload(Project.flags)
    ).order_by(Project.id).all()


####################
# SINGLE ENDPOINTS #
####################

@router.get("/{project_id}", response_model=ProjectRead)
def get_project_single_short(project_id: str, db: Session = Depends(get_db)):
    """Default: Single project essential data."""
    pro = db.query(Project).filter(Project.id == project_id).first()
    if not pro: raise HTTPException(404, "Project not found")
    return pro

@router.get("/{project_id}/detailed", response_model=ProjectDetailedView)
def get_project_single_long(project_id: str, db: Session = Depends(get_db)):
    """Detailed: Single project with children."""
    pro = db.query(Project).options(
        joinedload(Project.phases), 
        joinedload(Project.flags)
    ).filter(Project.id == project_id).first()
    
    if not pro: raise HTTPException(404, "Project not found")
    return pro
