from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db

from schemas.log import MonthView, DailyLogRead, DailyLogSync, YearView
import crud.log as log_crud
from services.employee import GetEmployeeMonthView, GetEmployeeYearView

router = APIRouter(prefix="/logs", tags=["Logs"])

@router.get("/{emp_id}/{year}/{month}", response_model=MonthView)
def get_employee_month(emp_id: str, year: int, month: int, db: Session = Depends(get_db)):
    action = GetEmployeeMonthView(db)
    return action.execute(emp_id, year, month)

@router.get("/{emp_id}/{year}", response_model=YearView)
def get_employee_year(emp_id: str, year: int, db: Session = Depends(get_db)):
    action = GetEmployeeYearView(db)
    return action.execute(emp_id, year)

@router.post("/sync", response_model=DailyLogRead)
def sync_log(payload: DailyLogSync, db: Session = Depends(get_db)):
    return log_crud.sync_daily_log(db, payload)