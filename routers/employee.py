from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db

from schemas.employee import EmployeeSchema
from services.employee import EmployeeService

router = APIRouter(prefix="/employees", tags=["Employees"])

@router.get("/", response_model=list[EmployeeSchema])
def get_employees(active: bool = True, db: Session = Depends(get_db)):
    service = EmployeeService(db)
    return service.get_all(active_only=active)

@router.get("/{emp_id}/leave-balance")
def get_leave_balance(emp_id: str, year: int, db: Session = Depends(get_db)):
    service = EmployeeService(db)
    return service.calculate_leave_balance(emp_id, year)