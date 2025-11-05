import httpx
from typing import List, Optional

RISE_JOBS_API = "https://api.joinrise.io/api/v1/jobs/public"

async def fetch_jobs(location: Optional[str] = None, page: int = 1, limit: int = 10):
    params = {
        "page": page,
        "limit": limit
    }
    if location:
        params["jobLoc"] = location

    async with httpx.AsyncClient() as client:
        response = await client.get(RISE_JOBS_API, params=params)
        response.raise_for_status()
        return response.json()