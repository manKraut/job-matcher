from typing import Dict
from openai import OpenAI
import os
import json

def get_openai_client():
    """Lazy initialization of OpenAI client to avoid errors at import time."""
    api_key = os.getenv("OPEN_API_KEY")
    if not api_key:
        raise ValueError("OPEN_API_KEY environment variable is not set")
    return OpenAI(api_key=api_key)

BASE_PREFERENCE_PROMPT = """
You are a helpful assistant for job seekers. Your goal is to extract structured job search preferences from a user's input.

The preferences you extract will be used to query a job search API. Make sure your extracted preferences align with the API's requirements.

Input: "I'm looking for a remote React developer job in Germany or the Netherlands"
Output: {
  "keywords": ["React", "developer"],
  "location": "Germany, Netherlands",
  "remote": true
}

Important: Extract location in a format that works with the job search API (city names, country names, or "Remote").
"""

def extract_preferences(user_input: str) -> Dict:
    """
    Extract job search preferences from user input using RAG-guided agent.
    
    Uses RAG to retrieve relevant API documentation so the agent can extract
    preferences that align with API requirements.
    """
    # Retrieve relevant API documentation using RAG
    from app.services.rag_utils import get_api_documentation_for_agent
    
    # Query RAG for location filtering, parameter requirements, and best practices
    rag_query = f"Arbeitnow job API location filtering keywords parameters user input: {user_input}"
    api_docs = get_api_documentation_for_agent(rag_query, n_results=3)
    
    # Build enhanced system prompt with API documentation
    system_prompt = BASE_PREFERENCE_PROMPT
    if api_docs:
        system_prompt += api_docs
        system_prompt += "\n\nUse the API documentation above to ensure your extracted preferences (especially location format) align with what the API expects."
    
    client = get_openai_client()
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ],
        temperature=0.3
    )
    content = response.choices[0].message.content
    print("🔍 Raw GPT output:", content)
    try:
        return json.loads(content)  # Convert string dict to actual dict
    except json.JSONDecodeError as e:
        return {"error": f"JSON parse failed: {str(e)}", "raw": content}