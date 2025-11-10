from openai import OpenAI
import os

def get_openai_client():
    """Lazy initialization of OpenAI client to avoid errors at import time."""
    api_key = os.getenv("OPEN_API_KEY")
    if not api_key:
        raise ValueError("OPEN_API_KEY environment variable is not set")
    return OpenAI(api_key=api_key)

ADVISOR_SYSTEM_PROMPT = """
You are a job search advisor. Based on the user’s preferences and a list of job matches, you provide a short explanation of why the results are relevant. Be friendly, clear, and concise.
"""

def explain_job_matches(preferences: dict, jobs: list) -> str:
    job_titles = [job["title"] for job in jobs[:5]]
    companies = [job["company"] for job in jobs[:5] if job.get("company")]

    job_titles_str = ", ".join(set(job_titles))
    companies_str = ", ".join(set(companies))

    user_pref_str = f"""
User Preferences:
- Keywords: {preferences.get("keywords")}
- Location: {preferences.get("location")}
- Remote: {preferences.get("remote")}
    """

    job_data_str = f"""
Top Jobs Found:
- Titles: {job_titles_str}
- Companies: {companies_str}
    """

    messages = [
        {"role": "system", "content": ADVISOR_SYSTEM_PROMPT},
        {"role": "user", "content": f"{user_pref_str}\n\n{job_data_str}"}
    ]

    client = get_openai_client()
    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        temperature=0.5
    )

    return response.choices[0].message.content
