"""
routes.py
---------
All FastAPI route handlers for FitBuddy:

    GET  /                 -> index.html (input form)
    POST /generate-workout -> generates plan + tip, saves them, shows result.html
    POST /submit-feedback  -> revises the plan using feedback, shows result.html
    GET  /view-all-users   -> admin dashboard (all_users.html)
    POST /delete-user/{id} -> admin: remove a user + their plan
"""

import os
from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from .schemas import UserInput, FeedbackRequest
from .gemini_generator import generate_workout_gemini
from .gemini_flash_generator import generate_nutrition_tip_with_flash
from .updated_plan import update_workout_plan
from . import database as db_layer

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "..", "templates")
templates = Jinja2Templates(directory=TEMPLATE_DIR)


# ---------------------------------------------------------------------------
# Home - input form
# ---------------------------------------------------------------------------
@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={})


# ---------------------------------------------------------------------------
# Scenario 1: Generate workout plan + nutrition tip
# ---------------------------------------------------------------------------
@router.post("/generate-workout", response_class=HTMLResponse)
def generate_workout(
    request: Request,
    username: str = Form(...),
    user_id: str = Form(...),
    age: int = Form(...),
    weight: int = Form(...),
    goal: str = Form(...),
    intensity: str = Form(...),
):
    user_input = UserInput(
        username=username, user_id=user_id, age=age,
        weight=weight, goal=goal, intensity=intensity,
    )

    db = db_layer.get_db()
    try:
        workout_plan = generate_workout_gemini(
            goal=user_input.goal, intensity=user_input.intensity,
            age=user_input.age, weight=user_input.weight,
        )
        nutrition_tip = generate_nutrition_tip_with_flash(user_input.goal)

        db_layer.save_user(
            db, user_input.user_id, user_input.username, user_input.age,
            user_input.weight, user_input.goal, user_input.intensity,
        )
        db_layer.save_plan(db, user_input.user_id, workout_plan, nutrition_tip)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    finally:
        db.close()

    return templates.TemplateResponse(request=request, name="result.html", context={
        "username": user_input.username,
        "user_id": user_input.user_id,
        "age": user_input.age,
        "weight": user_input.weight,
        "goal": user_input.goal,
        "intensity": user_input.intensity,
        "workout_plan": workout_plan,
        "nutrition_tip": nutrition_tip,
        "updated": False,
    })


# ---------------------------------------------------------------------------
# Scenario 2: Submit feedback -> revise the plan
# ---------------------------------------------------------------------------
@router.post("/submit-feedback", response_class=HTMLResponse)
def submit_feedback(
    request: Request,
    user_id: str = Form(...),
    feedback: str = Form(...),
):
    feedback_input = FeedbackRequest(user_id=user_id, feedback=feedback)

    db = db_layer.get_db()
    try:
        user = db_layer.get_user(db, feedback_input.user_id)
        original_plan = db_layer.get_original_plan(db, feedback_input.user_id)
        if not user or not original_plan:
            raise HTTPException(status_code=404, detail="User or plan not found. Generate a plan first.")

        revised_plan = update_workout_plan(original_plan, feedback_input.feedback)
        nutrition_tip = generate_nutrition_tip_with_flash(user.goal)

        db_layer.update_plan(db, feedback_input.user_id, revised_plan, feedback_input.feedback)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    finally:
        db.close()

    return templates.TemplateResponse(request=request, name="result.html", context={
        "username": user.username,
        "user_id": user.user_id,
        "age": user.age,
        "weight": user.weight,
        "goal": user.goal,
        "intensity": user.intensity,
        "workout_plan": revised_plan,
        "nutrition_tip": nutrition_tip,
        "updated": True,
    })


# ---------------------------------------------------------------------------
# Admin: view all users + their plans
# ---------------------------------------------------------------------------
@router.get("/view-all-users", response_class=HTMLResponse)
def view_all_users(request: Request):
    db = db_layer.get_db()
    try:
        users = db_layer.get_all_users(db)
        plans = {p.user_id: p for p in db_layer.get_all_plans(db)}
    finally:
        db.close()

    rows = []
    for u in users:
        p = plans.get(u.user_id)
        rows.append({
            "user_id": u.user_id, "username": u.username, "age": u.age,
            "weight": u.weight, "goal": u.goal, "intensity": u.intensity,
            "original_plan": p.original_plan if p else "",
            "updated_plan": p.updated_plan if p else "",
            "nutrition_tip": p.nutrition_tip if p else "",
        })

    return templates.TemplateResponse(request=request, name="all_users.html", context={"users": rows})


# ---------------------------------------------------------------------------
# Admin: delete a user + their plan
# ---------------------------------------------------------------------------
@router.post("/delete-user/{user_id}")
def delete_user(user_id: str):
    db = db_layer.get_db()
    try:
        db_layer.delete_user(db, user_id)
    finally:
        db.close()
    return RedirectResponse(url="/view-all-users", status_code=303)
