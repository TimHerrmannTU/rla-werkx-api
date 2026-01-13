from sqlalchemy.orm import Session
from models.project import Project
from sqlalchemy import func

class ProjectService:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, pro_id: str):
        return self.db.query(Project).filter(Project.id == pro_id).first()
    
    def get_flags(self, pro_id: bool = True):
        return ""