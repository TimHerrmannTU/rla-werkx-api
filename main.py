from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from models import (
    employees,
    flag ,
    phase,
    projects
)

from routers import (
    project,
    employee
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

app.include_router(projects.router) 
app.include_router(employees.router)
