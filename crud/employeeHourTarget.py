from sqlalchemy.orm import Session
from models.employee import EmployeeHourTarget
from schemas.employeeHourTarget import EmployeeHourTargetCreate, EmployeeHourTargetUpdate

def get_by_employee(db: Session, emp_id: str):
    return db.query(EmployeeHourTarget).filter(EmployeeHourTarget.employee_id == emp_id).all()

def create_with_employee(db: Session, schema: EmployeeHourTargetCreate, emp_id: str):
    data = schema.model_dump()
    data["employee_id"] = emp_id
    db_obj = EmployeeHourTarget(**data)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update(db: Session, db_obj: EmployeeHourTarget, schema: EmployeeHourTargetUpdate):
    data = schema.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(db_obj, field, value)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def delete(db: Session, target_id: int):
    db_obj = db.query(EmployeeHourTarget).filter(EmployeeHourTarget.id == target_id).first()
    if db_obj:
        db.delete(db_obj)
        db.commit()
    return db_obj