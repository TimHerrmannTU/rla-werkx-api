from src.core.base_crud import CRUDBase
from src.modules.employee.model import EmployeeVacationClaim
from src.modules.employee.schemas.vacationClaim import EmployeeVacationClaimCreate, EmployeeVacationClaimUpdate

class CRUDEmployeeVacationClaim(CRUDBase[EmployeeVacationClaim, EmployeeVacationClaimCreate, EmployeeVacationClaimUpdate]):
    pass # Add custom methods here

vacation_contract_crud = CRUDEmployeeVacationClaim(EmployeeVacationClaim)