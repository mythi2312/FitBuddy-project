"""
schemas.py
----------
Pydantic models used to validate incoming form data.
"""

from pydantic import BaseModel, Field


class UserInput(BaseModel):
    username: str
    user_id: str
    age: int = Field(..., ge=10, le=100)
    weight: int = Field(..., ge=20, le=300)
    goal: str          # e.g. "weight loss", "muscle gain", "flexibility"
    intensity: str     # "low" | "medium" | "high"


class FeedbackRequest(BaseModel):
    user_id: str
    feedback: str
