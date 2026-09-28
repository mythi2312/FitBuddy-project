"""
gemini_generator.py
--------------------
Uses Gemini 3 flash (preview) to generate the structured 7-day workout plan,
via the current `google-genai` SDK (the older `google-generativeai` package
is deprecated and no longer receives model updates).
"""

import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")
_client = genai.Client(api_key=API_KEY) if API_KEY else None
MODEL_NAME = "gemini-3-flash-preview"


def generate_workout_gemini(goal: str, intensity: str, age: int = None, weight: int = None) -> str:
    """
    Builds a prompt from the user's goal/intensity (and optional age/weight
    for extra context) and asks Gemini for a structured 7-day plan
    containing, for every day: a warm-up, the main workout, and a
    cooldown/recovery note.
    """
    if _client is None:
        raise RuntimeError(
            "GOOGLE_API_KEY is not set. Add it to your .env file "
            "(see .env.example) before generating a plan."
        )

    extra_context = ""
    if age:
        extra_context += f"Age: {age}. "
    if weight:
        extra_context += f"Weight: {weight} kg. "

    prompt = f"""
You are a certified personal trainer. Create a personalized 7-day workout plan.

Fitness goal: {goal}
Preferred workout intensity: {intensity}
{extra_context}

For each of the 7 days, structure the response exactly like this:

Day X - <focus area, e.g. Full Body / Upper Body / Cardio / Core / Flexibility / Rest>
Warm-up (5-10 mins): <short warm-up description>
Main Workout:
- <exercise 1 with sets/reps or duration>
- <exercise 2 with sets/reps or duration>
- <exercise 3 with sets/reps or duration>
Cooldown / Recovery: <short cooldown or recovery note>

Keep the exercises appropriate for the requested intensity ({intensity}) and
aligned with the goal ({goal}). Use plain text only, no markdown tables or
asterisks.
"""
    response = _client.models.generate_content(model=MODEL_NAME, contents=prompt)
    return response.text.strip()
