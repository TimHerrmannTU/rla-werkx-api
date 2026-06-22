from typing import Union, List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from src.modules.project.model import Project
from src.modules.log.model import LogProjectHour, LogDailySummary
from src.modules.project.schemas.general import ProjectCreate, ProjectUpdate
from src.core.base_crud import CRUDBase

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
    
    def get_colors(self, db: Session, project_ids: list[int]):
        return (
            db.query(
                Project.id,
                Project.name,
                Project.color
            ).filter(
                Project.id.in_(project_ids)
            ).all()
        )
        
    def get_stats(self, db: Session, project_id: str):
        ''' Aggregates Hours of Project by Phase, Flag, Date, and Employee '''
        return (
            db.query(
                LogProjectHour.phase_id,
                LogProjectHour.flag_id,
                LogDailySummary.date,
                LogDailySummary.employee_id,
                func.sum(LogProjectHour.time)
            ).join(
                LogDailySummary, 
                LogProjectHour.daily_entry_id == LogDailySummary.id
            ).filter(
                LogProjectHour.project_id == project_id
            ).group_by(
                LogProjectHour.phase_id, 
                LogProjectHour.flag_id,
                LogDailySummary.date,
                LogDailySummary.employee_id,
            ).all()
        )
    
project_crud = CRUDProject(Project)