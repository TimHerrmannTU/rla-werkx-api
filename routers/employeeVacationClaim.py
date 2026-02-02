# routers/employee_vacation_claims.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
import crud.employeeVacationClaim as claim_crud
from schemas.employeeVacationClaim import EmployeeVacationClaimRead, EmployeeVacationClaimCreate, EmployeeVacationClaimUpdate

router = APIRouter(prefix="/employees/{emp_id}/vacation-claims", tags=["Employee Vacation Claims"])

@router.get("/", response_model=list[EmployeeVacationClaimRead])
def get_claims(emp_id: str, db: Session = Depends(get_db)):
    return claim_crud.get_by_employee(db, emp_id)

@router.post("/", response_model=EmployeeVacationClaimRead, status_code=status.HTTP_201_CREATED)
def create_claim(emp_id: str, schema_in: EmployeeVacationClaimCreate, db: Session = Depends(get_db)):
    return claim_crud.create_with_employee(db, schema_in, emp_id)

@router.patch("/{claim_id}", response_model=EmployeeVacationClaimRead)
def update_claim(emp_id: str, claim_id: int, schema_in: EmployeeVacationClaimUpdate, db: Session = Depends(get_db)):
    db_obj = db.query(claim_crud.EmployeeVacationClaim).filter(
        claim_crud.EmployeeVacationClaim.id == claim_id,
        claim_crud.EmployeeVacationClaim.employee_id == emp_id
    ).first()
    if not db_obj: raise HTTPException(404, "Claim not found")
    return claim_crud.update(db, db_obj, schema_in)

@router.delete("/{claim_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_claim(emp_id: str, claim_id: int, db: Session = Depends(get_db)):
    db_obj = db.query(claim_crud.EmployeeVacationClaim).filter(
        claim_crud.EmployeeVacationClaim.id == claim_id,
        claim_crud.EmployeeVacationClaim.employee_id == emp_id
    ).first()
    if not db_obj: raise HTTPException(404, "Claim not found")
    claim_crud.delete(db, claim_id)