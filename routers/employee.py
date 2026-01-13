from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db

from models.employee import Employee
from schemas.employee import EmployeeSchema
from services.employee import EmployeeService

router = APIRouter(prefix="/api/employees", tags=["Employees"])

@router.get("/", response_model=list[EmployeeSchema])
def get_employees(db: Session = Depends(get_db)):
    return db.query(Employee).all()

@router.get("/id_map")
def get_employee_id_name_map(db: Session = Depends(get_db)):
    service = EmployeeService(db)
    return service.get_id_map()

@router.get("/{emp_id}", response_model=EmployeeSchema)
def get_employee_short(emp_id: str, db: Session = Depends(get_db)):
    """Default: Single project essential data."""
    emp = db.query(Employee).filter(Employee.id == emp_id).first()
    if not emp: raise HTTPException(404, "Employee not found")
    return emp