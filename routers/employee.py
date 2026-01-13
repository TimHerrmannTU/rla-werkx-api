from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db

from models.employee import Employee
from schemas.employee import EmployeeSchema

router = APIRouter(prefix="/employees", tags=["Employees"])

@router.get("/", response_model=list[EmployeeSchema])
def get_employees(active: bool = True, db: Session = Depends(get_db)):
    return db.query(Employee).all()


@router.get("/{emp_id}", response_model=EmployeeSchema)
def get_project_summary(emp_id: str, db: Session = Depends(get_db)):
    """Default: Single project essential data."""
    emp = db.query(Employee).filter(Employee.id == emp_id).first()
    if not emp: raise HTTPException(404, "Project not found")
    return emp