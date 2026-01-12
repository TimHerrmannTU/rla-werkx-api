from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.project import Project
from schemas.project import ProjectResponse

router = APIRouter(prefix="/projects", tags=["Projects"])

@router.get("/", response_model=list[ProjectResponse])
def get_all_projects(db: Session = Depends(get_db)):
    # Basic query - we will move this to 'services' later as logic grows
    projects = db.query(Project).all()
    return projects