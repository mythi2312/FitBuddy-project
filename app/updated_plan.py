"""
updated_plan.py
-----------------
Handles Scenario 2: revising an existing 7-day plan based on user feedback.
Reuses Gemini flash (preview) so the revised plan keeps the same
structured, day-wise format as the original. Uses the current
`google-genai` SDK.
"""

import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")
_client = genai.Client(api_key=API_KEY) if API_KEY else None
MODEL_NAME = "gemini-flash-latest"



def update_workout_plan(original_plan: str, feedback: str) -> str:
    """
    Sends the original plan + the user's feedback (e.g. "Add yoga",
    "Include more cardio") to Gemini and returns a revised 7-day plan
    that incorporates the requested changes.
    """
    if _client is None:
        raise RuntimeError(
            "GOOGLE_API_KEY is not set. Add it to your .env file "
            "(see .env.example) before updating a plan."
        )

    prompt = f"""
You are a certified personal trainer revising an existing 7-day workout
plan based on user feedback.

Original plan:
{original_plan}

User feedback: "{feedback}"

Regenerate the full 7-day plan, incorporating the feedback, using the
exact same structure as the original (Day X, Warm-up, Main Workout,
Cooldown / Recovery for each day). Plain text only, no markdown tables
or asterisks.
"""
    response = _client.models.generate_content(model=MODEL_NAME, contents=prompt)
    return response.text.strip()
