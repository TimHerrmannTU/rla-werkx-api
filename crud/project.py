from typing import Union, List, Optional
from sqlalchemy.orm import Session, joinedload
from models.project import Project
from schemas.project import ProjectCreate, ProjectUpdate

def get_all(db: Session):
    return db.query(Project).order_by(Project.id).all()

def get(db: Session, project_id: str):
    return db.query(Project).filter(Project.id == project_id).first()

def get_detailed(db: Session, project_id: Optional[str] = None) -> Union[Project, List[Project], None]:
    query = db.query(Project).options(
        joinedload(Project.phases),
        joinedload(Project.flags)
    )
    
    if project_id:
        return query.filter(Project.id == project_id).first()
    
    return query.order_by(Project.id).all()

def create(db: Session, schema: ProjectCreate):
    db_obj = Project(**schema.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update(db: Session, db_obj: Project, schema: ProjectUpdate):
    data = schema.model_dump(exclude_unset=True)
    for field in data:
        setattr(db_obj, field, data[field])
    db.commit()
    db.refresh(db_obj)
    return db_obj

def delete(db: Session, project_id: str):
    db_obj = db.query(Project).filter(Project.id == project_id).first()
    if db_obj:
        db.delete(db_obj)
        db.commit()
    return db_obj