from fastapi import APIRouter, Query
from typing import Optional
from app.services.job_api import fetch_jobs
from app.models.job import JobResult

router = APIRouter()

@router.get("/jobs", response_model=list[JobResult])
async def get_jobs(
    location: Optional[str] = Query(None, description="City or country"),
    page: int = 1,
    limit: int = 10
):
    jobs = await fetch_jobs(location=location, page=page, limit=limit)
    return jobs