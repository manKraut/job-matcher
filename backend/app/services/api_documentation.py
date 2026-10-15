"""
API Documentation content for the Arbeitnow Job Board API (as used by this app).
This documentation is stored in ChromaDB for RAG retrieval.

Source: https://documenter.getpostman.com/view/18545278/UVJbJdKh
Keep the order of the chunks in sync with `doc_types` in scripts/init_rag_db.py.
"""

# Arbeitnow Job Board API Documentation
ARBEITNOW_API_DOCS = [
    """
    Arbeitnow Job Board API - Endpoint Information

    Base URL: https://www.arbeitnow.com/api/job-board-api
    Method: GET
    Description: Free public job board API listing jobs mainly in Germany, Switzerland,
    the Netherlands, the UK, France and other European countries.

    The API is public and does not require authentication. It does NOT offer any
    server-side filtering: there are no location, keyword or remote parameters.
    This application downloads a few pages, caches them for about 10 minutes and then
    filters the jobs itself (by location, keywords and remote) before returning them.
    Jobs are returned newest first and are refreshed hourly.
    """,

    """
    Arbeitnow Job Board API - Query Parameters

    The upstream API itself only supports pagination:

    1. page (integer, optional, default: 1)
       - Page of results to retrieve (each page holds around 100-300 jobs)
       - Example: ?page=2

    Everything else is handled by THIS application's endpoint GET /api/jobs, which accepts:

    1. location (string, optional)
       - Country name, city name or "Remote"
       - Several places can be separated by commas: "Germany, Netherlands"
       - Matching is case-insensitive and ignores accents (Zurich = Zürich, Munich = München)
       - If omitted, jobs from all locations are searched

    2. keywords (list of strings, optional)
       - Job title and skill terms, for example: keywords=react&keywords=developer
       - ALL keywords must appear in the job title, tags, company or description
       - Prefer a few short, specific English terms (job title and main skills)

    3. remote (boolean, optional)
       - true = only remote jobs; false or omitted = no preference

    4. page (integer, default 1) and limit (integer, default 20, max 100)
       - Pagination over the already filtered results
    """,

    """
    Arbeitnow Job Board API - Request Examples

    Upstream API:
    GET https://www.arbeitnow.com/api/job-board-api
    GET https://www.arbeitnow.com/api/job-board-api?page=2

    This application's endpoint:
    GET /api/jobs?location=Germany
    GET /api/jobs?location=Zurich&keywords=data&keywords=engineer
    GET /api/jobs?location=Germany,Netherlands&keywords=react&remote=true
    GET /api/jobs?keywords=python            (any location)
    GET /api/jobs?location=Remote&keywords=designer
    """,

    """
    Arbeitnow Job Board API - Response Structure

    The upstream API returns a JSON object:

    {
        "data": [
            {
                "slug": "senior-software-engineer-munich-42343",
                "company_name": "Company Name",
                "title": "Job Title",
                "description": "<p>HTML description</p>",
                "remote": false,
                "url": "https://www.arbeitnow.com/jobs/companies/...",
                "tags": ["Engineering"],
                "job_types": ["Unbefristeter arbeitsvertrag"],
                "location": "Munich",
                "created_at": 1792065313
            }
        ],
        "links": {"first": "...", "last": null, "prev": null, "next": "...?page=2"},
        "meta": {"current_page": 1, "per_page": 100, "terms": "...", "info": "..."}
    }

    Important fields:
    - data: array of jobs (can be empty)
    - title, company_name, location (free text), url (link to the job), remote (boolean)
    - description is HTML and can be empty
    - created_at is a Unix timestamp in seconds
    - links.next is null on the last page
    """,

    """
    Arbeitnow Job Board API - Best Practices for Location Filtering

    Locations in the data are free text, in different languages and formats, for example
    "Berlin", "Zurich, Zürich, Switzerland", "Amsterdam, Noord-Holland, Netherlands",
    "Paris office", "Remote". Some jobs have an empty location.

    When choosing the location preference:
    1. Use English country names ("Germany", "Switzerland", "Netherlands", "United Kingdom")
       for broad searches. Major cities of known countries are matched to their country.
    2. Use city names for specific cities ("Berlin", "Zurich", "London").
    3. Use several comma separated places when the user names several ("Germany, Netherlands").
    4. For remote work use "Remote" (and set remote to true).
    5. For a whole region, "Europe" matches jobs in any known European country.
    6. A location that matches nothing returns no jobs. This is expected: the application then
       tells the user "No available jobs with those specs". Do not invent locations.
    7. Country coverage depends on what employers currently post, so some countries may
       have few or no jobs.
    """,

    """
    Arbeitnow Job Board API - Error Handling

    The upstream API uses standard HTTP status codes:

    - 200: Success
    - 4xx / 5xx: Client or server errors, or rate limiting if the API is abused

    In this application:
    1. No job matches the given location/keywords/remote values: GET /api/jobs returns 200 with
       an empty list, and the interface shows "No available jobs with those specs".
    2. The upstream API is unreachable or returns an error: GET /api/jobs returns 502 with a
       message that the job source is temporarily unavailable. If cached jobs exist they are
       served instead, even when slightly outdated.
    3. Network requests use a 30 second timeout.
    """,

    """
    Arbeitnow Job Board API - Data Transformation Guidelines

    How upstream jobs are mapped to the application's JobResult model:

    - title        <- job["title"]
    - company      <- job["company_name"]
    - location     <- job["location"] (None when empty)
    - url          <- job["url"] (link to the job on Arbeitnow)

    Notes:
    1. Jobs without a title are skipped.
    2. Duplicate jobs (same slug) are returned once.
    3. The HTML description is not returned to the frontend; it is only used for keyword matching.
    4. Use safe access with .get() because fields can be missing or empty.
    """,

    """
    Arbeitnow Job Board API - Pagination Strategy

    The upstream API paginates with ?page=N and returns jobs newest first.
    There is no total page count: links.last is null, and links.next is null on the last page.

    The application downloads up to 5 pages (about 1,000-1,500 jobs) per refresh, in parallel,
    and caches them for about 10 minutes. Filtering is done on this cached set, so a very rare
    search may miss matches that are only on later pages.

    For the application's own /api/jobs endpoint, page and limit paginate the filtered results
    (default limit 20, maximum 100).
    """,

    """
    Arbeitnow Job Board API - Integration Notes

    1. Terms of use: this is a free public API, "please do not abuse". Cache results (done: 10 minutes),
       avoid unnecessary requests, and link back to Arbeitnow (done: footer link in the interface).
    2. Jobs are in many languages. Job titles are often in German, French or English, so keywords
       work best as short, widely used terms (for example "developer", "python", "marketing").
    3. All keywords must match, so avoid long lists of generic words; they reduce the number of results.
    4. Use an async HTTP client (httpx.AsyncClient) with a timeout, and handle network errors gracefully.

    Current implementation uses:
    - httpx for async HTTP requests to https://www.arbeitnow.com/api/job-board-api
    - An in-memory cache of the downloaded jobs
    - JobResult Pydantic model for the response
    - Location, keywords and remote filtering done in the application
    """
]
