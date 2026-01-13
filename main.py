from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import models.project

from routers import project
from routers import employee

# Initialize the App
app = FastAPI(title="WerkX API")

# Configure CORS (Allows your PHP/Frontend to talk to this API if on different ports)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev only. In prod, set to specific domain.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(project.router) 

# TEST ENDPOINTS
@app.get("/api/hello")
def read_root():
    return {"message": "Hello World from FastAPI", "status": "online"}
@app.get("/api/hello/{name}")
def read_item(name: str):
    return {"message": f"Hello, {name}!"}