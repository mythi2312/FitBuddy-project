import traceback

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from fastapi.staticfiles import StaticFiles

from app.database import init_db
from app.routes import router

app = FastAPI(
    title="FitBuddy - AI Fitness Plan Generator",
    description="Generates personalized 7-day workout plans and nutrition tips using Gemini.",
    version="1.0.0",
)

init_db()


@app.exception_handler(Exception)
async def show_error(request, exc):
    return PlainTextResponse(traceback.format_exc(), status_code=500)


app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(router)
