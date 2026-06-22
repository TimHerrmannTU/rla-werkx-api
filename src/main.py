from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.modules.employee.routers.general import router as employee_general_router
from src.modules.employee.routers.hourTarget import router as employee_hour_target_router
from src.modules.employee.routers.vacationClaim import router as employee_vacation_claim_router

from src.modules.project.routers.general import router as project_general_router
from src.modules.project.routers.flag import router as project_flag_router
from src.modules.project.routers.phase import router as project_phase_router

from src.modules.team import Team
from src.modules.location import Location

# Initialize the App
app = FastAPI(title="WerkX API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev only. In prod, set to specific domain.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(project_general_router) 
app.include_router(project_flag_router) 
app.include_router(project_phase_router) 

app.include_router(employee_general_router)
app.include_router(employee_hour_target_router)
app.include_router(employee_vacation_claim_router)