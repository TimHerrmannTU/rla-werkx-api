from models.employee import Employee
from schemas.employee import EmployeeCreate, EmployeeUpdate
from .base import CRUDBase

class CRUDEmployee(CRUDBase[Employee, EmployeeCreate, EmployeeUpdate]):
    pass # Add custom methods here

employee_crud = CRUDEmployee(Employee)