from sqlalchemy.orm import Session
from models.employee import Employee
from schemas.employee import EmployeeCreate, EmployeeUpdate

def get_all(db: Session):
    return db.query(Employee).order_by(Employee.id).all()

def get(db: Session, emp_id: int):
    return db.query(Employee).filter(Employee.id == emp_id).first()

def create(db: Session, schema: EmployeeCreate):
    db_obj = Employee(**schema.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update(db: Session, db_obj: Employee, schema: EmployeeUpdate):
    data = schema.model_dump(exclude_unset=True)
    for field in data:
        setattr(db_obj, field, data[field])
    db.commit()
    db.refresh(db_obj)
    return db_obj

def delete(db: Session, emp_id: int):
    db_obj = db.query(Employee).filter(Employee.id == emp_id).first()
    if db_obj:
        db.delete(db_obj)
        db.commit()
    return db_obj