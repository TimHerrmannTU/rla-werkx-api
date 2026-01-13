from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.project import Project
from schemas.project import ProjectSchema

# Prefix sets the URL structure to /api/project
router = APIRouter(prefix="/api/project", tags=["Project"])

@router.get("/{kuerzel}", response_model=ProjectSchema)
def get_single_project(kuerzel: str, db: Session = Depends(get_db)):
    
    project = db.query(Project).filter(Project.id == kuerzel).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    return project

@router.get("/", response_model=list[ProjectSchema])
def get_all_projects(db: Session = Depends(get_db)):
    # Fetch all projects, ordered by ID
    projects = db.query(Project).order_by(Project.id).all()
    return projects