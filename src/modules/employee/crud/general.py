from typing import Optional, Sequence
from sqlalchemy.orm import Session, joinedload

from ....core.base_crud import CRUDBase
from src.modules.employee.model import Employee
from src.modules.employee.schemas.general import EmployeeRead, EmployeeCreate, EmployeeUpdate

class CRUDEmployee(CRUDBase[Employee, EmployeeCreate, EmployeeUpdate]):
    def get_all(self, db: Session, active: Optional[bool] = None) -> Sequence[EmployeeRead]:
        query = db.query(self.model)
        if active is not None:
            query = query.filter(self.model.active == active)
        return query.order_by(self.model.name).all()
    
    def get_with_details(self, db: Session, emp_id: str):
        return (
            db.query(Employee)
            .options(
                joinedload(Employee.hour_targets),
                joinedload(Employee.vacation_claims)
            )
            .filter(Employee.id == emp_id)
            .first()
        )

employee_crud = CRUDEmployee(Employee)