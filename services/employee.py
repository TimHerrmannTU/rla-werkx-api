from sqlalchemy.orm import Session
from models.employee import Employee
from sqlalchemy import func

class EmployeeService:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, active_only: bool = True):
        """
        Replaces get_mitarbeiter_k (active=True) and get_mitarbeiter_ki (active=False)
        Returns full objects instead of just lists of strings.
        """
        query = self.db.query(Employee)
        if active_only:
            query = query.filter(Employee.is_active == True)
        
        # Legacy sort was LOWER(`name`)
        return query.order_by(func.lower(Employee.name)).all()

    def get_by_id(self, emp_id: str):
        return self.db.query(Employee).filter(Employee.id == emp_id).first()
    
    def get_id_map(self, active_only: bool = True):
        """
        Useful for dropdowns. Replaces get_mitarbeiter_kv.
        Returns { "AeMe": "Max Mustermann", ... }
        """
        employees = self.get_all(active_only)
        return {emp.name: emp.id for emp in employees}