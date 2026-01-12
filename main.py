from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

# 1. Hello World Endpoint
@app.get("/api/hello")
def read_root():
    return {"message": "Hello World from FastAPI", "status": "online"}

# 2. Example with Path Parameter (like /api/user/123)
@app.get("/api/hello/{name}")
def read_item(name: str):
    return {"message": f"Hello, {name}!"}