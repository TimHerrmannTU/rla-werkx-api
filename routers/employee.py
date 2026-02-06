from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db

from crud.employee import employee_crud
import services.employee as employee_service
from schemas.employee import EmployeeRead, EmployeeCreate, EmployeeUpdate, EmployeeDetailedView

router = APIRouter(prefix="/employees", tags=["Employees"])

##################
# CRUD ENDPOINTS #
##################

@router.get("/", response_model=list[EmployeeRead])
def get_employee_list(active: Optional[bool] = None, db: Session = Depends(get_db)):
    return employee_crud.get_all(db, active=active)

@router.get("/{emp_id}", response_model=EmployeeRead)
def get_employee_single_short(emp_id: str, db: Session = Depends(get_db)):
    emp = employee_crud.get(db, emp_id)
    if not emp: raise HTTPException(404, "Employee not found")
    return emp

@router.post("/", response_model=EmployeeRead, status_code=status.HTTP_201_CREATED)
def create_new_employee(employee_in: EmployeeCreate, db: Session = Depends(get_db)):
    return employee_crud.create(db, employee_in)

@router.patch("/{emp_id}", response_model=EmployeeRead)
def update_existing_employee(emp_id: str, employee_in: EmployeeUpdate, db: Session = Depends(get_db)):
    db_emp = employee_crud.get(db, emp_id)
    if not db_emp:
        raise HTTPException(404, "Employee not found")
    return employee_crud.update(db, db_emp, employee_in)

@router.delete("/{emp_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_employee(emp_id: str, db: Session = Depends(get_db)):
    success = employee_crud.delete(db, emp_id)
    if not success:
        raise HTTPException(404, "Employee not found")
    return None

##################
# VIEW ENDPOINTS #
##################

@router.get("/detailed/{emp_id}", response_model=EmployeeDetailedView)
def get_employee_single_long(emp_id: str, db: Session = Depends(get_db)):
    emp = employee_service.get_employee_detailed(db, emp_id)
    if not emp: raise HTTPException(404, "Employee not found")
    return emp