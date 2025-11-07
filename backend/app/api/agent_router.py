from fastapi import APIRouter, Body
from app.agents.preference_agent import extract_preferences
from app.agents.match_advisor_agent import explain_job_matches
router = APIRouter()

@router.post("/agents/preferences")
async def clarify_preferences(input: str = Body(..., embed=True)):
    result = extract_preferences(input)
    return result

@router.post("/agents/match-advice")
async def get_match_advice(
    payload: dict = Body(...)
):
    preferences = payload.get("preferences")
    jobs = payload.get("jobs", [])
    message = explain_job_matches(preferences, jobs)
    return {"advice": message}