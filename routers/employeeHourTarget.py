from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
import crud.employeeHourTarget as target_crud
from schemas.employeeHourTarget import EmployeeHourTargetRead, EmployeeHourTargetCreate, EmployeeHourTargetUpdate

router = APIRouter(prefix="/employees/{emp_id}/hour-targets", tags=["Employee Hour Targets"])

@router.get("/", response_model=list[EmployeeHourTargetRead])
def get_targets(emp_id: str, db: Session = Depends(get_db)):
    return target_crud.get_by_employee(db, emp_id)

@router.post("/", response_model=EmployeeHourTargetRead, status_code=status.HTTP_201_CREATED)
def create_target(emp_id: str, schema_in: EmployeeHourTargetCreate, db: Session = Depends(get_db)):
    return target_crud.create_with_employee(db, schema_in, emp_id)

@router.patch("/{target_id}", response_model=EmployeeHourTargetRead)
def update_target(emp_id: str, target_id: int, schema_in: EmployeeHourTargetUpdate, db: Session = Depends(get_db)):
    db_obj = db.query(target_crud.EmployeeHourTarget).filter(
        target_crud.EmployeeHourTarget.id == target_id,
        target_crud.EmployeeHourTarget.employee_id == emp_id
    ).first()
    if not db_obj: raise HTTPException(404, "Target not found")
    return target_crud.update(db, db_obj, schema_in)

@router.delete("/{target_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_target(emp_id: str, target_id: int, db: Session = Depends(get_db)):
    db_obj = db.query(target_crud.EmployeeHourTarget).filter(
        target_crud.EmployeeHourTarget.id == target_id,
        target_crud.EmployeeHourTarget.employee_id == emp_id
    ).first()
    if not db_obj: raise HTTPException(404, "Target not found")
    target_crud.delete(db, target_id)