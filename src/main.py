from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.modules.employee import (
    employee_general_router, 
    employee_hour_target_router, 
    employee_vacation_claim_router
)
from src.modules.project import (
    project_general_router,
    project_flag_router,
    project_phase_router,
)

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