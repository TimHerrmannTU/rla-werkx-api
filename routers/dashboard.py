from datetime import date, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db

import services.dashboard as dashboard_service
from services.project import GetProjectDashboard
from services.employee import GetEmployeeDashboard 

from schemas.project import ProjectDashboardView

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

def _parse_dates(start_date: Optional[date], end_date: Optional[date]) -> tuple[date, date]:
    today = date.today()
    parsed_end = end_date if (end_date is not None) else today
    parsed_start = start_date if (start_date is not None) else parsed_end - timedelta(days=365)
    return parsed_start, parsed_end

@router.get("/")
def get_general(
    db: Session = Depends(get_db),
    start_date: Optional[date] = Query(None, description="Start date of the timeframe (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date of the timeframe (YYYY-MM-DD)")
):
    parsed_start, parsed_end = _parse_dates(start_date, end_date)
    return dashboard_service.get_general(db, start_date=parsed_start, end_date=parsed_end)


@router.get("/team")
def get_team_stats(
    db: Session = Depends(get_db),
    emp_ids: list[str] = Query(..., description="List of employee IDs for the team statistics"),
    start_date: Optional[date] = Query(None, description="Start date of the timeframe (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date of the timeframe (YYYY-MM-DD)")
):
    parsed_start, parsed_end = _parse_dates(start_date, end_date)
    return dashboard_service.get_team_stats(
        db, 
        emp_ids=emp_ids, 
        start_date=parsed_start, 
        end_date=parsed_end
    )


@router.get("/project/{project_id}", response_model=ProjectDashboardView)
def get_project(project_id: str, db: Session = Depends(get_db)):
    action = GetProjectDashboard(db)
    pro = action.execute(project_id)
    if not pro:
        raise HTTPException(404, "Project not found")
    return pro


@router.get("/employee/{emp_id}")
def get_employee(emp_id: str, db: Session = Depends(get_db)):
    action = GetEmployeeDashboard(db)
    return action.execute(emp_id)