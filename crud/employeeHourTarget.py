from models.employee import EmployeeHourTarget
from schemas.employeeHourTarget import EmployeeHourTargetCreate, EmployeeHourTargetUpdate
from .base import CRUDBase

class CRUDEmployeeHourTarget(CRUDBase[EmployeeHourTarget, EmployeeHourTargetCreate, EmployeeHourTargetUpdate]):
    pass # Add custom methods here

target_crud = CRUDEmployeeHourTarget(EmployeeHourTarget)