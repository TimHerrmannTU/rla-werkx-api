from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db

import services.employee as employee_service
from schemas.log import MonthView

router = APIRouter(prefix="/logging", tags=["Logging"])

@router.get("/{emp_id}/{year}/{month}", response_model=MonthView)
def get_employee_month(emp_id: str, year: int, month: int, db: Session = Depends(get_db)):
    return employee_service.get_employee_month_view(db, emp_id, year, month)
