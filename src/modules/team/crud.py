# crud/team.py
from src.modules.team.models import Team
from src.modules.team.schema import TeamCreate, TeamUpdate
from ...core.base_crud import CRUDBase

class CRUDTeam(CRUDBase[Team, TeamCreate, TeamUpdate]):
    pass

team_crud = CRUDTeam(Team)