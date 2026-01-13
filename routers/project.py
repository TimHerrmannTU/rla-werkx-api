from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from database import get_db
from models.project import Project
from schemas.project import ProjectSummary, ProjectDetail

router = APIRouter(prefix="/api/projects", tags=["Projects"])

# --------------------------
# LIST ENDPOINTS
# --------------------------

@router.get("/", response_model=list[ProjectSummary])
def get_projects_short(db: Session = Depends(get_db)):
    """Default: Returns essential data only."""
    return db.query(Project).order_by(Project.id).all()

@router.get("/detailed", response_model=list[ProjectDetail])
def get_projects_long(db: Session = Depends(get_db)):
    """Detailed: Returns everything + flags."""
    return db.query(Project).options(joinedload(Project.flags)).order_by(Project.id).all()


# --------------------------
# SINGLE ENDPOINTS
# --------------------------

@router.get("/{project_id}", response_model=ProjectSummary)
def get_project_short(project_id: str, db: Session = Depends(get_db)):
    """Default: Single project essential data."""
    pro = db.query(Project).filter(Project.id == project_id).first()
    if not pro: raise HTTPException(404, "Project not found")
    return pro

@router.get("/{project_id}/detailed", response_model=ProjectDetail)
def get_project_long(project_id: str, db: Session = Depends(get_db)):
    """Default: Single project essential data."""
    pro = db.query(Project).filter(Project.id == project_id).first()
    if not pro: raise HTTPException(404, "Project not found")
    return pro