from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db

from models.employee import Employee
import crud.employee as employee_crud
import services.employee as employee_service
from schemas.employee import EmployeeRead, EmployeeDetailedView

router = APIRouter(prefix="/employees", tags=["Employees"])

@router.get("/", response_model=list[EmployeeRead])
def get_employee_list(db: Session = Depends(get_db)):
    return employee_crud.get_all(db)

@router.get("/{emp_id}", response_model=EmployeeRead)
def get_employee_short(emp_id: str, db: Session = Depends(get_db)):
    emp = employee_crud.get(db, emp_id)
    if not emp: raise HTTPException(404, "Employee not found")
    return emp

@router.get("/detailed/{emp_id}", response_model=EmployeeDetailedView)
def get_employee_short(emp_id: str, db: Session = Depends(get_db)):
    emp = employee_service.get_employee_detailed(db, emp_id)
    if not emp: raise HTTPException(404, "Employee not found")
    return emp