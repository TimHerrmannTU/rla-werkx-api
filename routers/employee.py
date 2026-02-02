from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db

from models.employee import Employee
import services.employee as employee_service

from schemas.employee import EmployeeRead, EmployeeDetailedView
from schemas.log import MonthView

router = APIRouter(prefix="/employees", tags=["Employees"])

@router.get("/", response_model=list[EmployeeRead])
def get_employees(db: Session = Depends(get_db)):
    return db.query(Employee).all()

@router.get("/id_map")
def get_employee_id_name_map(db: Session = Depends(get_db)):
    return employee_service.get_employee_id_map(db)

@router.get("/{emp_id}", response_model=EmployeeDetailedView)
def get_employee_short(emp_id: str, db: Session = Depends(get_db)):
    emp = employee_service.get_employee_detailed(db, emp_id)
    if not emp: 
        raise HTTPException(404, "Employee not found")
    return emp

@router.get("/{emp_id}/{year}/{month}", response_model=MonthView)
def get_employee_month(emp_id: str, year: int, month: int, db: Session = Depends(get_db)):
    return employee_service.get_employee_month_view(db, emp_id, year, month)