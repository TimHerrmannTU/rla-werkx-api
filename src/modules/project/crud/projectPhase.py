from sqlalchemy.orm import Session
from src.modules.project.model import ProjectPhase
from src.modules.project.schemas.phase import PhaseCreate, PhaseUpdate
from ....core.base_crud import CRUDBase

class CRUDProjectPhase(CRUDBase[ProjectPhase, PhaseCreate, PhaseUpdate]):
    def get_by_project(self, db: Session, project_id: str):
        return db.query(self.model).filter(self.model.project_id == project_id).all()

    def create_with_project(self, db: Session, schema: PhaseCreate, project_id: str):
        data = schema.model_dump()
        data["project_id"] = project_id
        db_obj = self.model(**data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

phase_crud = CRUDProjectPhase(ProjectPhase)