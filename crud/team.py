# crud/team.py
from models.team import Team
from schemas.team import TeamCreate, TeamUpdate
from .base import CRUDBase

class CRUDTeam(CRUDBase[Team, TeamCreate, TeamUpdate]):
    pass

team_crud = CRUDTeam(Team)