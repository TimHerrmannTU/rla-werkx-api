import json 

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from database import get_db

from models.employee import Employee

from services.employee import EmployeeService

from schemas.employee import EmployeeSchema, EmployeeDetailedSchema
from schemas.log import DailyLogSchema

router = APIRouter(prefix="/api/employees", tags=["Employees"])

@router.get("/", response_model=list[EmployeeSchema])
def get_employees(db: Session = Depends(get_db)):
    return db.query(Employee).all()

@router.get("/id_map")
def get_employee_id_name_map(db: Session = Depends(get_db)):
    service = EmployeeService(db)
    return service.get_id_map()

@router.get("/{emp_id}", response_model=EmployeeDetailedSchema)
def get_employee_short(emp_id: str, db: Session = Depends(get_db)):
    """Default: Single project essential data."""
    service = EmployeeService(db)
    emp = service.get_detailed(emp_id)
    if not emp: raise HTTPException(404, "Not found")
    return emp

@router.get("/{emp_id}/{year}/{month}")
def get_employee_month(emp_id: str, year: int, month: int, db: Session = Depends(get_db)):
    service = EmployeeService(db)
    return service.get_month_view(emp_id, year, month)