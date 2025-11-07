from fastapi import APIRouter, Body
from app.agents.preference_agent import extract_preferences

router = APIRouter()

@router.post("/agents/preferences")
async def clarify_preferences(input: str = Body(..., embed=True)):
    result = extract_preferences(input)
    return result