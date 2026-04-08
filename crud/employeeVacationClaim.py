from models.employee import EmployeeVacationClaim
from schemas.employeeVacationClaim import EmployeeVacationClaimCreate, EmployeeVacationClaimUpdate
from .base import CRUDBase

class CRUDEmployeeVacationClaim(CRUDBase[EmployeeVacationClaim, EmployeeVacationClaimCreate, EmployeeVacationClaimUpdate]):
    pass # Add custom methods here

vacation_contract_crud = CRUDEmployeeVacationClaim(EmployeeVacationClaim)