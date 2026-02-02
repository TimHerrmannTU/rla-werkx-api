# crud/flag.py
from sqlalchemy.orm import Session
from models.project import ProjectFlag
from schemas.projectFlag import FlagCreate, FlagUpdate

def get_all(db: Session):
    return db.query(ProjectFlag).order_by(ProjectFlag.id).all()

def get(db: Session, flag_id: str):
    return db.query(ProjectFlag).filter(ProjectFlag.id == flag_id).first()

def create(db: Session, schema: FlagCreate):
    db_obj = ProjectFlag(**schema.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update(db: Session, db_obj: ProjectFlag, schema: FlagUpdate):
    data = schema.model_dump(exclude_unset=True)
    for field in data:
        setattr(db_obj, field, data[field])
    db.commit()
    db.refresh(db_obj)
    return db_obj

def delete(db: Session, flag_id: str):
    db_obj = db.query(ProjectFlag).filter(ProjectFlag.id == flag_id).first()
    if db_obj:
        db.delete(db_obj)
        db.commit()
    return db_obj

# LINKED WITH PROJECT

def get_by_project(db: Session, project_id: str):
    return db.query(ProjectFlag).filter(ProjectFlag.project_id == project_id).all()

def create_with_project(db: Session, schema: FlagCreate, project_id: str):
    data = schema.model_dump()
    data["project_id"] = project_id # Force project association
    db_obj = ProjectFlag(**data)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj