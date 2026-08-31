from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.trip import Trip
from app.models.user import User
from app.schemas.planner import PlanRequest, PlanResponse
from app.services.planner import create_trip_plan

router = APIRouter(prefix="/agent", tags=["AI Planner"])

@router.post("/plan", response_model=PlanResponse)
def plan_trip(data: PlanRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    plan = create_trip_plan(data.prompt)
    trip = None
    if data.trip_id:
        trip = db.scalar(select(Trip).where(Trip.id == data.trip_id, Trip.user_id == user.id))
        if not trip: raise HTTPException(status_code=404, detail="Trip not found")
    if not trip:
        trip = Trip(user_id=user.id, destination=plan.destination, start_date=plan.start_date,
                    end_date=plan.end_date, budget=plan.total_budget, currency=plan.currency.upper())
        db.add(trip)
    trip.destination, trip.start_date, trip.end_date = plan.destination, plan.start_date, plan.end_date
    trip.budget, trip.currency, trip.request_text = plan.total_budget, plan.currency.upper(), data.prompt
    trip.itinerary, trip.status = plan.model_dump(mode="json"), "planned"
    db.commit(); db.refresh(trip)
    return PlanResponse(trip_id=trip.id, plan=plan)
