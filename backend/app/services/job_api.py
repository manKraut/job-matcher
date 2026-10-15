"""
Job search backed by the free Arbeitnow job board API.

API docs: https://documenter.getpostman.com/view/18545278/UVJbJdKh
  GET https://www.arbeitnow.com/api/job-board-api   (no auth, no filter parameters)
  Paginate with ?page=N, newest jobs first, refreshed hourly.

The API has no server-side filtering, so we download a few pages, cache them
for a while and filter by location / keywords / remote ourselves.
"""
import asyncio
import html
import re
import time
import unicodedata
from typing import Dict, List, Optional

import httpx

from app.models.job import JobResult

ARBEITNOW_API = "https://www.arbeitnow.com/api/job-board-api"

MAX_PAGES = 5               # pages downloaded per refresh (the API returns ~100-300 jobs per page)
CACHE_TTL_SECONDS = 600     # be kind to the free API: refresh at most every 10 minutes
REQUEST_TIMEOUT = 30.0

_cache: Dict = {"jobs": None, "fetched_at": 0.0}
_cache_lock = asyncio.Lock()


# --------------------------------------------------------------------------- #
# Text helpers
# --------------------------------------------------------------------------- #
_CHAR_FIXES = str.maketrans({"ł": "l", "ß": "ss", "ø": "o", "æ": "ae", "đ": "d", "œ": "oe"})


def _normalize(text: Optional[str]) -> str:
    """Lowercase, strip accents and punctuation: 'Zürich, CH' -> 'zurich ch'."""
    text = unicodedata.normalize("NFKD", (text or "").lower().translate(_CHAR_FIXES))
    text = "".join(c for c in text if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


def _has_word(haystack: str, needle: str) -> bool:
    """Whole-word match on normalized text (multi-word needles supported)."""
    return f" {needle} " in f" {haystack} "


def _has_word_prefix(haystack: str, needle: str) -> bool:
    """Match that must start on a word boundary: 'develop' matches 'developers'."""
    return f" {needle}" in f" {haystack}"


def _strip_html(raw: Optional[str]) -> str:
    return html.unescape(re.sub(r"<[^>]+>", " ", raw or ""))


# --------------------------------------------------------------------------- #
# Location knowledge (best effort: locations are free text in many languages)
# --------------------------------------------------------------------------- #
_COUNTRY_ALIASES = {
    "germany": ["germany", "deutschland", "allemagne"],
    "switzerland": ["switzerland", "schweiz", "suisse", "svizzera"],
    "netherlands": ["netherlands", "the netherlands", "nederland", "holland"],
    "united kingdom": ["united kingdom", "uk", "england", "scotland", "wales", "great britain", "britain"],
    "france": ["france"],
    "austria": ["austria", "osterreich"],
    "italy": ["italy", "italia"],
    "spain": ["spain", "espana"],
    "portugal": ["portugal"],
    "poland": ["poland", "polska"],
    "belgium": ["belgium", "belgique", "belgie"],
    "luxembourg": ["luxembourg"],
    "ireland": ["ireland"],
    "sweden": ["sweden", "sverige"],
    "denmark": ["denmark", "danmark"],
    "norway": ["norway", "norge"],
    "finland": ["finland", "suomi"],
}

_COUNTRY_CITIES = {
    "germany": [
        "berlin", "munich", "munchen", "hamburg", "frankfurt", "cologne", "koln", "dusseldorf",
        "stuttgart", "leipzig", "dresden", "nuremberg", "nurnberg", "hannover", "hanover",
        "bremen", "essen", "dortmund", "bonn", "mannheim", "karlsruhe", "heidelberg", "freiburg",
        "mainz", "potsdam", "aachen", "augsburg", "bochum", "bielefeld",
    ],
    "switzerland": [
        "zurich", "geneva", "geneve", "basel", "bern", "lausanne", "lugano", "nyon", "zug",
        "lucerne", "luzern", "winterthur", "st gallen", "neuchatel", "fribourg",
    ],
    "netherlands": [
        "amsterdam", "rotterdam", "utrecht", "the hague", "den haag", "eindhoven", "groningen",
        "delft", "leiden", "tilburg",
    ],
    "united kingdom": [
        "london", "manchester", "birmingham", "leeds", "edinburgh", "glasgow", "bristol",
        "cambridge", "oxford", "liverpool", "leicester", "sheffield", "cardiff", "belfast",
    ],
    "france": [
        "paris", "lyon", "marseille", "toulouse", "lille", "nantes", "bordeaux", "nice",
        "strasbourg", "montpellier", "rennes",
    ],
    "austria": ["vienna", "wien", "graz", "salzburg", "linz", "innsbruck"],
    "italy": ["milan", "milano", "rome", "roma", "turin", "torino", "bologna", "florence", "naples"],
    "spain": ["madrid", "barcelona", "valencia", "seville", "malaga", "bilbao"],
    "portugal": ["lisbon", "lisboa", "porto"],
    "poland": ["warsaw", "warszawa", "krakow", "poznan", "wroclaw", "gdansk", "lodz"],
    "belgium": ["brussels", "bruxelles", "antwerp", "antwerpen", "ghent", "gent", "leuven"],
    "luxembourg": ["luxembourg city"],
    "ireland": ["dublin", "cork", "galway"],
    "sweden": ["stockholm", "gothenburg", "goteborg", "malmo"],
    "denmark": ["copenhagen", "kobenhavn", "aarhus"],
    "norway": ["oslo", "bergen"],
    "finland": ["helsinki", "espoo", "tampere"],
}

_ALIAS_TO_COUNTRY = {
    _normalize(alias): country for country, aliases in _COUNTRY_ALIASES.items() for alias in aliases
}
_CITY_TO_COUNTRY = {
    _normalize(city): country for country, cities in _COUNTRY_CITIES.items() for city in cities
}

_REMOTE_TERMS = {"remote", "anywhere", "worldwide", "home office", "homeoffice"}


def _countries_for(location_norm: str) -> set:
    """Countries a free-text location refers to (explicitly or via a known city)."""
    found = {c for alias, c in _ALIAS_TO_COUNTRY.items() if _has_word(location_norm, alias)}
    found |= {c for city, c in _CITY_TO_COUNTRY.items() if _has_word(location_norm, city)}
    return found


def _parse_location_terms(location: Optional[str]) -> List[str]:
    """'Germany, Netherlands or Remote' -> ['germany', 'netherlands', 'remote']."""
    if not location:
        return []
    parts = re.split(r"\s*(?:,|;|/|\||\bor\b|\band\b)\s*", location, flags=re.IGNORECASE)
    return [t for t in (_normalize(p) for p in parts) if t]


def _parse_keywords(keywords: Optional[List[str]]) -> List[str]:
    """Accept repeated or comma separated keywords; return normalized, unique terms."""
    terms: List[str] = []
    for item in keywords or []:
        for piece in item.split(","):
            norm = _normalize(piece)
            if norm and norm not in terms:
                terms.append(norm)
    return terms


# --------------------------------------------------------------------------- #
# Matching
# --------------------------------------------------------------------------- #
def _location_term_matches(job: Dict, term: str) -> bool:
    if term in _REMOTE_TERMS:
        return job["remote"] or _has_word(job["loc_norm"], "remote")
    if term == "europe":
        return bool(job["countries"])
    country = _ALIAS_TO_COUNTRY.get(term)
    if country and country in job["countries"]:
        return True
    return _has_word(job["loc_norm"], term)


def _matches(job: Dict, location_terms: List[str], keyword_terms: List[str], remote: Optional[bool]) -> bool:
    if remote and not (job["remote"] or _has_word(job["loc_norm"], "remote")):
        return False
    if location_terms and not any(_location_term_matches(job, t) for t in location_terms):
        return False
    # Every keyword must appear in the title, tags, company or description.
    return all(_has_word_prefix(job["text_norm"], kw) for kw in keyword_terms)


# --------------------------------------------------------------------------- #
# Fetching and caching
# --------------------------------------------------------------------------- #
def _prepare(raw: Dict) -> Optional[Dict]:
    title = (raw.get("title") or "").strip()
    if not title:
        return None
    location = (raw.get("location") or "").strip()
    company = (raw.get("company_name") or "").strip()
    tags = " ".join(raw.get("tags") or [])
    loc_norm = _normalize(location)
    return {
        "slug": raw.get("slug"),
        "title": title,
        "company": company or None,
        "location": location or None,
        "url": raw.get("url") or None,
        "remote": bool(raw.get("remote")),
        "loc_norm": loc_norm,
        "countries": _countries_for(loc_norm),
        "text_norm": _normalize(f"{title} {tags} {company} {_strip_html(raw.get('description'))}"),
    }


async def _fetch_page(client: httpx.AsyncClient, page: int) -> Dict:
    response = await client.get(ARBEITNOW_API, params={"page": page})
    response.raise_for_status()
    return response.json()


async def _download_jobs() -> List[Dict]:
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
        first = await _fetch_page(client, 1)
        pages = [first]
        if first.get("data") and (first.get("links") or {}).get("next"):
            rest = await asyncio.gather(
                *[_fetch_page(client, p) for p in range(2, MAX_PAGES + 1)],
                return_exceptions=True,
            )
            for page_no, result in enumerate(rest, start=2):
                if isinstance(result, dict):
                    pages.append(result)
                else:
                    print(f"⚠️  Arbeitnow page {page_no} failed: {result!r}")

    jobs, seen = [], set()
    for page in pages:
        for raw in page.get("data") or []:
            job = _prepare(raw)
            if job and job["slug"] not in seen:
                seen.add(job["slug"])
                jobs.append(job)
    return jobs


async def _load_jobs() -> List[Dict]:
    """Return cached jobs, refreshing them when older than CACHE_TTL_SECONDS."""
    async with _cache_lock:
        fresh = _cache["jobs"] is not None and time.monotonic() - _cache["fetched_at"] < CACHE_TTL_SECONDS
        if fresh:
            return _cache["jobs"]
        try:
            jobs = await _download_jobs()
        except Exception as e:
            print(f"❌ Network Error: {e!r}")
            if _cache["jobs"] is not None:
                print("ℹ️  Serving stale cached jobs")
                return _cache["jobs"]
            raise
        _cache["jobs"] = jobs
        _cache["fetched_at"] = time.monotonic()
        print(f"✅ Loaded {len(jobs)} jobs from Arbeitnow")
        return jobs


async def fetch_jobs(
    location: Optional[str] = None,
    keywords: Optional[List[str]] = None,
    remote: Optional[bool] = None,
    page: int = 1,
    limit: int = 20,
) -> List[JobResult]:
    """
    Search jobs on Arbeitnow.

    Args:
        location: Free text; several places may be separated by commas ("Germany, Netherlands").
                  Country names, city names and "Remote" are understood. Empty = anywhere.
        keywords: Terms that must ALL appear in the job's title, tags, company or description.
        remote:   True = only remote jobs. False/None = no preference.
        page:     Page of the *filtered* results (1-based).
        limit:    Jobs per page.

    Returns:
        Matching jobs, newest first. An empty list means "no available jobs with those specs".
    """
    jobs = await _load_jobs()

    location_terms = _parse_location_terms(location)
    keyword_terms = _parse_keywords(keywords)
    matched = [j for j in jobs if _matches(j, location_terms, keyword_terms, remote)]

    start = (page - 1) * limit
    return [
        JobResult(title=j["title"], location=j["location"], company=j["company"], url=j["url"])
        for j in matched[start:start + limit]
    ]
