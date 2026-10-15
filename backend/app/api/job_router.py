from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import httpx
from app.services.job_api import fetch_jobs
from app.models.job import JobResult

router = APIRouter()

@router.get("/jobs", response_model=list[JobResult])
async def get_jobs(
    location: Optional[str] = Query(
        None, description="Country, city or 'Remote'. Separate several places with commas."
    ),
    keywords: Optional[List[str]] = Query(
        None, description="Job title / skill terms; all of them must match. Repeat the parameter or use commas."
    ),
    remote: Optional[bool] = Query(None, description="true = only remote jobs"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
):
    """Returns matching jobs, or an empty list when nothing matches the given specs."""
    try:
        return await fetch_jobs(
            location=location, keywords=keywords, remote=remote, page=page, limit=limit
        )
    except httpx.HTTPError:
        raise HTTPException(
            status_code=502,
            detail="The job source is temporarily unavailable. Please try again in a moment.",
        )
