"""
database.py
------------
SQLite persistence layer (via SQLAlchemy ORM) for FitBuddy.

Exposes the helper functions named in the project workflow:
    save_user(), save_plan(), update_plan(),
    get_original_plan(), get_user(),
    get_all_users(), get_all_plans()
"""

import os
from sqlalchemy import create_engine, Column, String, Integer, Text, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship

DATABASE_URL = "sqlite:///./fitbuddy.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------
class User(Base):
    """One row per user, keyed by the user_id they enter on the form."""
    __tablename__ = "users"

    user_id = Column(String(50), primary_key=True, index=True)
    username = Column(String(100), nullable=False)
    age = Column(Integer, nullable=False)
    weight = Column(Integer, nullable=False)  # kg
    goal = Column(String(50), nullable=False)
    intensity = Column(String(20), nullable=False)

    plan = relationship("Plan", back_populates="user", uselist=False)


class Plan(Base):
    """The AI-generated plan tied to a single user (1-to-1)."""
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(50), ForeignKey("users.user_id"), nullable=False, unique=True)

    original_plan = Column(Text, nullable=True)
    updated_plan = Column(Text, nullable=True)
    nutrition_tip = Column(Text, nullable=True)
    feedback = Column(Text, nullable=True)

    user = relationship("User", back_populates="plan")


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    """Returns a new session. Routes are responsible for closing it (db.close())."""
    return SessionLocal()


# ---------------------------------------------------------------------------
# Helper functions used by routes.py
# ---------------------------------------------------------------------------
def save_user(db, user_id, username, age, weight, goal, intensity):
    """Insert a new user, or update their profile if the user_id already exists."""
    user = db.query(User).filter(User.user_id == user_id).first()
    if user:
        user.username, user.age, user.weight = username, age, weight
        user.goal, user.intensity = goal, intensity
    else:
        user = User(
            user_id=user_id, username=username, age=age,
            weight=weight, goal=goal, intensity=intensity,
        )
        db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user(db, user_id):
    return db.query(User).filter(User.user_id == user_id).first()


def save_plan(db, user_id, workout_plan, nutrition_tip):
    """Create (or overwrite) the original plan + nutrition tip for a user."""
    plan = db.query(Plan).filter(Plan.user_id == user_id).first()
    if plan:
        plan.original_plan = workout_plan
        plan.nutrition_tip = nutrition_tip
        plan.updated_plan = None
        plan.feedback = None
    else:
        plan = Plan(user_id=user_id, original_plan=workout_plan, nutrition_tip=nutrition_tip)
        db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


def get_original_plan(db, user_id):
    plan = db.query(Plan).filter(Plan.user_id == user_id).first()
    return plan.original_plan if plan else None


def update_plan(db, user_id, updated_plan_text, feedback):
    """Store the feedback-refined plan, keeping the original plan intact."""
    plan = db.query(Plan).filter(Plan.user_id == user_id).first()
    if not plan:
        return None
    plan.updated_plan = updated_plan_text
    plan.feedback = feedback
    db.commit()
    db.refresh(plan)
    return plan


def get_all_users(db):
    return db.query(User).all()


def get_all_plans(db):
    return db.query(Plan).all()


def delete_user(db, user_id):
    """Used by the admin 'view all users' page to remove a user + their plan."""
    plan = db.query(Plan).filter(Plan.user_id == user_id).first()
    if plan:
        db.delete(plan)
    user = db.query(User).filter(User.user_id == user_id).first()
    if user:
        db.delete(user)
    db.commit()
