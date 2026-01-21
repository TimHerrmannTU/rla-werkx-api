from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db

from services.dashboard import DashboardService

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

@router.get("/")
def get_employees(db: Session = Depends(get_db)):
    start_date = date(2025, 1, 1)
    end_date = date(2026, 1, 1)
    service = DashboardService(db)
    return service.get_project_stats(start_date=start_date, end_date=end_date)
