from sqlalchemy.orm import Session
from src.modules.project.model import ProjectFlag
from src.modules.project.schemas.flag import FlagCreate, FlagUpdate
from src.core.base_crud import CRUDBase

class CRUDProjectFlag(CRUDBase[ProjectFlag, FlagCreate, FlagUpdate]):

    def get_by_project(self, db: Session, project_id: str):
        return db.query(self.model).filter(self.model.project_id == project_id).all()

    def create_with_project(self, db: Session, schema: FlagCreate, project_id: str):
        data = schema.model_dump()
        data["project_id"] = project_id
        db_obj = self.model(**data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

flag_crud = CRUDProjectFlag(ProjectFlag)