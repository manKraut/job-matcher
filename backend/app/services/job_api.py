import httpx
from typing import List, Optional
from app.models.job import JobResult

RISE_JOBS_API = "https://api.joinrise.io/api/v1/jobs/public"

async def fetch_jobs(location: Optional[str] = None, page: int = 1, limit: int = 10) -> List[JobResult]:
    params = {
        "page": page,
        "limit": limit
    }
    if location:
        params["jobLoc"] = location

    async with httpx.AsyncClient() as client:
        response = await client.get(RISE_JOBS_API, params=params)
        response.raise_for_status()
        data = response.json()

    raw_jobs = data.get("result", {}).get("jobs", [])

    # Transform to JobResult list
    return [
        JobResult(
            title=job.get("title"),
            location=job.get("locationAddress"),
            company=job.get("owner", {}).get("name"),
            url=None  # Will enhance this later if job URL is available
        )
        for job in raw_jobs
    ]