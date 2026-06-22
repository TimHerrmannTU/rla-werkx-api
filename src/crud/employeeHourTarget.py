from sqlalchemy import extract
from sqlalchemy.orm import Session, joinedload
from typing import Sequence
from datetime import date

from src.models.employee import EmployeeHourTarget
from src.schemas.employeeHourTarget import EmployeeHourTargetCreate, EmployeeHourTargetUpdate
from .base import CRUDBase

class CRUDEmployeeHourTarget(CRUDBase[EmployeeHourTarget, EmployeeHourTargetCreate, EmployeeHourTargetUpdate]):
    def get_for_month(db: Session, emp_id: str, year: int, month: int):
        first_day = date(year, month, 1)
        return (
            db.query(
                EmployeeHourTarget
            ).filter(
                EmployeeHourTarget.employee_id == emp_id,
                (EmployeeHourTarget.valid_start <= first_day) | (EmployeeHourTarget.valid_start == None),
                (EmployeeHourTarget.valid_stop >= first_day)  | (EmployeeHourTarget.valid_stop == None)
            ).first()
        )

hour_contract_crud = CRUDEmployeeHourTarget(EmployeeHourTarget)