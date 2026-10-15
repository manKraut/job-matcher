import httpx
from typing import List, Optional
from app.models.job import JobResult

RISE_JOBS_API = "https://api.joinrise.io/api/v1/jobs/public"

async def fetch_jobs(location: Optional[str] = None, page: int = 1, limit: int = 10) -> List[JobResult]:
    """
    Fetch jobs from Rise Jobs API.
    
    Args:
        location: Optional location filter (city or country name)
        page: Page number for pagination (default: 1)
        limit: Number of jobs per page (default: 10)
        
    Returns:
        List of JobResult objects
    """
    # Build query parameters
    params = {
        "page": page,
        "limit": limit
    }
    
    # Add location parameter if provided
    if location:
        params["jobLoc"] = location
    
    # Make API call
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(RISE_JOBS_API, params=params)
            response.raise_for_status()
            data = response.json()
        except httpx.HTTPStatusError as e:
            print(f"❌ API Error {e.response.status_code}: {e.response.text}")
            raise
        except Exception as e:
            print(f"❌ Network Error: {e}")
            raise
    
    # Extract jobs from response
    raw_jobs = data.get("result", {}).get("jobs", [])
    
    if not raw_jobs:
        print("ℹ️  No jobs found for the given parameters")
    
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