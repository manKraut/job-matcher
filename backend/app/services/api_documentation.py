"""
API Documentation content for the Rise Jobs API.
This documentation will be stored in ChromaDB for RAG retrieval.
"""

# Rise Jobs API Documentation
RISE_JOBS_API_DOCS = [
    """
    Rise Jobs API - Endpoint Information
    
    Base URL: https://api.joinrise.io/api/v1/jobs/public
    Method: GET
    Description: Retrieves public job listings from the Rise Jobs platform.
    
    This endpoint returns job postings that can be filtered by location and paginated.
    The API is public and does not require authentication.
    """,
    
    """
    Rise Jobs API - Query Parameters
    
    The API accepts the following query parameters:
    
    1. page (integer, optional, default: 1)
       - Specifies which page of results to retrieve
       - Use for pagination when there are many results
       - Must be a positive integer
       - Example: page=1, page=2, page=3
    
    2. limit (integer, optional, default: 10)
       - Specifies the maximum number of jobs to return per page
       - Controls pagination size
       - Recommended range: 10-50
       - Example: limit=10, limit=20, limit=50
    
    3. jobLoc (string, optional)
       - Filters jobs by location (city or country name)
       - Case-insensitive matching
       - Can be a city name (e.g., "Berlin", "New York")
       - Can be a country name (e.g., "Germany", "United States")
       - If omitted, returns jobs from all locations
       - Example: jobLoc=Berlin, jobLoc=Germany, jobLoc=Remote
    """,
    
    """
    Rise Jobs API - Request Examples
    
    Example 1: Get first page with default limit (10 jobs)
    GET https://api.joinrise.io/api/v1/jobs/public?page=1&limit=10
    
    Example 2: Get jobs in a specific location
    GET https://api.joinrise.io/api/v1/jobs/public?page=1&limit=10&jobLoc=Berlin
    
    Example 3: Get more jobs per page
    GET https://api.joinrise.io/api/v1/jobs/public?page=1&limit=50&jobLoc=Germany
    
    Example 4: Get jobs without location filter (all locations)
    GET https://api.joinrise.io/api/v1/jobs/public?page=1&limit=10
    
    Example 5: Get second page of results
    GET https://api.joinrise.io/api/v1/jobs/public?page=2&limit=10&jobLoc=London
    """,
    
    """
    Rise Jobs API - Response Structure
    
    The API returns a JSON object with the following structure:
    
    {
        "result": {
            "jobs": [
                {
                    "title": "Job Title",
                    "locationAddress": "City, Country",
                    "owner": {
                        "name": "Company Name"
                    },
                    ...other fields...
                }
            ]
        }
    }
    
    Important fields:
    - result: Top-level object containing the response
    - result.jobs: Array of job objects
    - Each job has: title (string), locationAddress (string), owner.name (string)
    - Always check if result exists and jobs array is not empty
    - The jobs array can be empty if no matches are found
    """,
    
    """
    Rise Jobs API - Best Practices for Location Filtering
    
    When filtering by location (jobLoc parameter):
    
    1. Use city names for specific cities: "Berlin", "London", "New York"
    2. Use country names for broader searches: "Germany", "United Kingdom", "USA"
    3. For remote jobs, try: "Remote", "Anywhere", or omit the jobLoc parameter
    4. Location matching is case-insensitive
    5. If location is not found, API may return empty results or all jobs
    6. Always handle cases where location parameter is None or empty (return all jobs)
    7. Location doesn't match any jobs (empty results array)
    8. Location is ambiguous (multiple matches possible)
    
    Best practice: Always provide a fallback when location filtering returns no results.
    """,
    
    """
    Rise Jobs API - Error Handling
    
    The API uses standard HTTP status codes:
    
    - 200: Success - Jobs retrieved successfully
    - 400: Bad Request - Invalid parameters (e.g., negative page number)
    - 404: Not Found - Endpoint not found
    - 500: Server Error - API server issue
    
    Always:
    1. Check response status code before processing
    2. Use response.raise_for_status() to handle HTTP errors
    3. Validate response structure before accessing nested fields
    4. Handle empty results gracefully (result.jobs might be empty array)
    5. Check if result key exists before accessing result.jobs
    6. Handle network errors (connection timeout, DNS errors, etc.)
    """,
    
    """
    Rise Jobs API - Data Transformation Guidelines
    
    When processing API responses:
    
    1. Extract jobs from: data.get("result", {}).get("jobs", [])
       - Always use .get() with defaults to avoid KeyError
       - Default to empty list if structure is missing
    
    2. Map API fields to application model:
       - title -> job.get("title")
       - locationAddress -> job.get("locationAddress")
       - owner.name -> job.get("owner", {}).get("name")
       - url -> None (not available in current API version)
    
    3. Handle missing or null fields:
       - Use Optional types in models
       - Provide default values (e.g., "Unknown Company" for missing company)
       - Filter out jobs with missing required fields if needed
       - Use safe navigation: job.get("owner", {}).get("name") to avoid errors
    """,
    
    """
    Rise Jobs API - Pagination Strategy
    
    When implementing pagination:
    
    1. Start with page=1 for first page
    2. Use limit to control page size (recommended: 10-50)
    3. Continue fetching pages until empty results
    4. For user-facing applications, limit total pages fetched (e.g., max 10 pages)
    5. Consider caching results to reduce API calls
    6. Handle rate limiting if API has rate limits
    
    Example pagination loop:
    - Fetch page 1 with limit 10
    - If results < limit, no more pages
    - Otherwise, increment page and fetch next page
    
    Note: Always validate page and limit parameters are positive integers.
    """,
    
    """
    Rise Jobs API - Integration Notes
    
    When integrating this API:
    
    1. Use async HTTP client (httpx.AsyncClient) for non-blocking requests
    2. Set appropriate timeout values
    3. Use environment variables for API URLs (if they change)
    4. Implement retry logic for transient failures
    5. Log API calls for debugging
    6. Transform API response to match your application's data model
    7. Handle network errors gracefully (connection timeout, DNS errors, etc.)
    8. Use type hints and Pydantic models for response validation
    
    Current implementation uses:
    - httpx for async HTTP requests
    - JobResult Pydantic model for type safety
    - Optional location parameter for flexible filtering
    - Safe dictionary access with .get() methods
    """
]
