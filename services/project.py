from sqlalchemy.orm import Session
from models.project import Project

class ProjectService:
    def __init__(self, db: Session):
        self.db = db

    def get_statistics(self, pro_id: str):
        
        return None