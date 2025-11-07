from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import job_router, agent_router

app = FastAPI(title="Open Job Matcher API")

# Allow frontend to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(job_router.router, prefix="/api")
app.include_router(agent_router.router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Open Job Matcher API"}