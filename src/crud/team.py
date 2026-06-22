# crud/team.py
from src.models.team import Team
from src.schemas.team import TeamCreate, TeamUpdate
from .base import CRUDBase

class CRUDTeam(CRUDBase[Team, TeamCreate, TeamUpdate]):
    pass

team_crud = CRUDTeam(Team)