from typing import Union, List, Optional
from sqlalchemy.orm import Session, joinedload

from models.project import Project
from schemas.project import ProjectCreate, ProjectUpdate
from .base import CRUDBase

class CRUDProject(CRUDBase[Project, ProjectCreate, ProjectUpdate]):

    def get_all(self, db: Session, active: Optional[bool] = None):
        query = db.query(self.model)
        if active is not None:
            query = query.filter(self.model.active == active)
        return query.order_by(self.model.id).all()

    def get_detailed(self, db: Session, project_id: Optional[str] = None, active: Optional[bool] = None) -> Union[Project, List[Project], None]:
        query = db.query(self.model).options(
            joinedload(self.model.phases),
            joinedload(self.model.flags)
        )
        
        if project_id:
            return query.filter(self.model.id == project_id).first()
        elif active is not None:
            query = query.filter(self.model.active == active)
        
        return query.order_by(self.model.id).all()
    
project_crud = CRUDProject(Project)