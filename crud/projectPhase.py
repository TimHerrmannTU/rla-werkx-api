# crud/phase.py
from sqlalchemy.orm import Session
from models.project import ProjectPhase
from schemas.projectPhase import PhaseCreate, PhaseUpdate

def get_all(db: Session):
    return db.query(ProjectPhase).order_by(ProjectPhase.id).all()

def get(db: Session, phase_id: str):
    return db.query(ProjectPhase).filter(ProjectPhase.id == phase_id).first()

def create(db: Session, schema: PhaseCreate):
    db_obj = ProjectPhase(**schema.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update(db: Session, db_obj: ProjectPhase, schema: PhaseUpdate):
    data = schema.model_dump(exclude_unset=True)
    for field in data:
        setattr(db_obj, field, data[field])
    db.commit()
    db.refresh(db_obj)
    return db_obj

def delete(db: Session, phase_id: str):
    db_obj = db.query(ProjectPhase).filter(ProjectPhase.id == phase_id).first()
    if db_obj:
        db.delete(db_obj)
        db.commit()
    return db_obj


# LINKED WITH PROJECT

def get_by_project(db: Session, project_id: str):
    return db.query(ProjectPhase).filter(ProjectPhase.project_id == project_id).all()

def create_with_project(db: Session, schema: PhaseCreate, project_id: str):
    data = schema.model_dump()
    data["project_id"] = project_id # Force project association
    db_obj = ProjectPhase(**data)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj