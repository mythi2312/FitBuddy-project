"""
gemini_flash_generator.py
--------------------------
Uses the lighter, faster Gemini Flash (preview) model to generate
quick, practical nutrition or recovery tips - a task that doesn't need
Gemini Pro's heavier reasoning, so Flash keeps this call fast and
efficient. Uses the current `google-genai` SDK.
"""

import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")
_client = genai.Client(api_key=API_KEY) if API_KEY else None
MODEL_NAME = "gemini-flash-latest"



def generate_nutrition_tip_with_flash(goal: str) -> str:
    """
    Returns one short, practical nutrition or recovery tip tailored to the
    user's fitness goal (e.g. hydration advice, protein suggestions,
    general recovery best practices).
    """
    if _client is None:
        raise RuntimeError(
            "GOOGLE_API_KEY is not set. Add it to your .env file "
            "(see .env.example) before requesting a tip."
        )

    prompt = f"""
Give ONE short, practical nutrition or recovery tip (1-2 sentences) for
someone whose fitness goal is "{goal}". Be specific and actionable
(e.g. a food source, a hydration habit, or a recovery practice).
Do not add any preamble - return only the tip itself, plain text.
"""
    response = _client.models.generate_content(model=MODEL_NAME, contents=prompt)
    return response.text.strip()
