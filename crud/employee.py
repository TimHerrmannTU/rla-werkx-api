from typing import Optional
from sqlalchemy.orm import Session

from models.employee import Employee
from schemas.employee import EmployeeCreate, EmployeeUpdate
from .base import CRUDBase

class CRUDEmployee(CRUDBase[Employee, EmployeeCreate, EmployeeUpdate]):
    def get_all(self, db: Session, active: Optional[bool] = None):
        query = db.query(self.model)
        if active is not None:
            query = query.filter(self.model.active == active)
        return query.order_by(self.model.name).all()

employee_crud = CRUDEmployee(Employee)