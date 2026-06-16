from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db

import services.dashboard as dashboard_service
from services.project import GetProjectDashboard
from services.employee import GetEmployeeDashboard 

from schemas.project import ProjectDashboardView

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/")
def get_general(db: Session = Depends(get_db)):
    start_date = date(2025, 1, 1)
    end_date = date(2026, 1, 1)
    return dashboard_service.get_general(db, start_date=start_date, end_date=end_date)

@router.get("/project/{project_id}", response_model=ProjectDashboardView)
def get_project(project_id: str, db: Session = Depends(get_db)):
    action = GetProjectDashboard(db)
    pro = action.execute(project_id)
    if not pro:
        raise HTTPException(404, "Project not found")
    return pro

@router.get("/employee/{emp_id}")
def get_project(emp_id: str, db: Session = Depends(get_db)):
    action = GetEmployeeDashboard(db)
    return action.execute(emp_id)