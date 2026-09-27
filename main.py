"""
main.py
-------
FitBuddy - AI Fitness Plan Generator (FastAPI + Gemini 1.5 Pro/Flash)

Run with:
    uvicorn main:app --reload

Then visit:
    http://127.0.0.1:8000        -> web app
    http://127.0.0.1:8000/docs   -> interactive API docs
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.database import init_db
from app.routes import router

app = FastAPI(
    title="FitBuddy - AI Fitness Plan Generator",
    description="Generates personalized 7-day workout plans and nutrition tips using Gemini 1.5 Pro & Flash.",
    version="1.0.0",
)

# Create the SQLite tables on startup if they don't exist yet.
init_db()

app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(router)
