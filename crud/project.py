from typing import Union, List, Optional
from sqlalchemy.orm import Session, joinedload

from models.project import Project
from schemas.project import ProjectCreate, ProjectUpdate
from .base import CRUDBase

class CRUDProject(CRUDBase[Project, ProjectCreate, ProjectUpdate]):
    def get_detailed(self, db: Session, project_id: Optional[str] = None) -> Union[Project, List[Project], None]:
        query = db.query(self.model).options(
            joinedload(self.model.phases),
            joinedload(self.model.flags)
        )
        
        if project_id:
            return query.filter(self.model.id == project_id).first()
        
        return query.order_by(self.model.id).all()
    
project_crud = CRUDProject(Project)