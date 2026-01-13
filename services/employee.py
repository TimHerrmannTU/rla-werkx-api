from sqlalchemy.orm import Session
from models.employee import Employee
from sqlalchemy import func

class EmployeeService:
    def __init__(self, db: Session):
        self.db = db

    def get_id_map(self, active_only: bool = True):
        employees = self.get_all(active_only)
        return {emp.name: emp.id for emp in employees}