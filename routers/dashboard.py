from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db

from services.dashboard import DashboardService
from services.project import ProjectService

from schemas.project import ProjectDashboardSchema

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

@router.get("/")
def get_general(db: Session = Depends(get_db)):
    start_date = date(2025, 1, 1)
    end_date = date(2026, 1, 1)
    service = DashboardService(db)
    return service.get_general(start_date=start_date, end_date=end_date)

@router.get("/project/{project_id}", response_model=ProjectDashboardSchema)
def get_project_statistic(project_id: str, db: Session = Depends(get_db)):
    service = ProjectService(db)
    pro = service.get_project_statistics(project_id)
    if not pro:
        raise HTTPException(404, "Project not found")
    return pro