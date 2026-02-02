# crud/employee_vacation_claim.py
from sqlalchemy.orm import Session
from models.employee import EmployeeVacationClaim
from schemas.employeeVacationClaim import EmployeeVacationClaimCreate, EmployeeVacationClaimUpdate

def get_by_employee(db: Session, emp_id: str):
    return db.query(EmployeeVacationClaim).filter(EmployeeVacationClaim.employee_id == emp_id).all()

def create_with_employee(db: Session, schema: EmployeeVacationClaimCreate, emp_id: str):
    data = schema.model_dump()
    data["employee_id"] = emp_id
    db_obj = EmployeeVacationClaim(**data)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update(db: Session, db_obj: EmployeeVacationClaim, schema: EmployeeVacationClaimUpdate):
    data = schema.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(db_obj, field, value)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def delete(db: Session, claim_id: int):
    db_obj = db.query(EmployeeVacationClaim).filter(EmployeeVacationClaim.id == claim_id).first()
    if db_obj:
        db.delete(db_obj)
        db.commit()
    return db_obj