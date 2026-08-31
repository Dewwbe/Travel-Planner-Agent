from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.user_memory import UserMemory

def load_user_memory(db: Session, user_id: int) -> dict:
    rows = db.scalars(select(UserMemory).where(UserMemory.user_id == user_id)).all()
    return {row.key: row.value for row in rows}

def remember(db: Session, user_id: int, key: str, value: dict):
    row = db.scalar(select(UserMemory).where(UserMemory.user_id == user_id, UserMemory.key == key))
    if not row:
        row = UserMemory(user_id=user_id, key=key, value=value)
        db.add(row)
    else:
        row.value = value

def save_plan_preferences(db: Session, user_id: int, plan):
    remember(db, user_id, "travel_preferences", {
        "last_destination": plan.destination, "currency": plan.currency,
        "hotel_rating": plan.hotel_rating, "travelers": plan.travelers,
    })
