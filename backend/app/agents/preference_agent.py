from typing import Dict
from openai import OpenAI
import os
import json

client = OpenAI(api_key="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")


  # Replace with your env var later

PREFERENCE_PROMPT = """
You are a helpful assistant for job seekers. Your goal is to extract structured job search preferences from a user's input.

Input: "I'm looking for a remote React developer job in Germany or the Netherlands"
Output: {
  "keywords": ["React", "developer"],
  "location": "Germany, Netherlands",
  "remote": true
}
"""

def extract_preferences(user_input: str) -> Dict:
    prompt = PREFERENCE_PROMPT + f'\n\nInput: "{user_input}"\nOutput:'
    response = client.chat.completions.create(model="gpt-4",
    messages=[
        {"role": "system", "content": PREFERENCE_PROMPT},
        {"role": "user", "content": user_input}
    ],
    temperature=0.3)
    content = response.choices[0].message.content
    print("🔍 Raw GPT output:", content)
    try:
        return json.loads(content)  # Convert string dict to actual dict
    except json.JSONDecodeError as e:
        return {"error": f"JSON parse failed: {str(e)}", "raw": content}