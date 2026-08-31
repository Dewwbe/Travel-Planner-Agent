from datetime import datetime, time, timezone
from uuid import uuid4
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.trip import Trip
from app.models.user import User
from app.schemas.planner import PlanRequest, PlanResponse
from app.services.planner import create_trip_plan
from app.graph.travel_graph import travel_graph
from app.models.pending_action import PendingAction
from app.schemas.hotel import HotelOffer
from app.schemas.orchestration import ActionResponse, AgentRunRequest, AgentRunResponse, ReviewResult
from app.schemas.planner import TripPlan
from app.services.calendar_mcp import create_event
from app.services.memory import load_user_memory, save_plan_preferences

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

@router.post("/run", response_model=AgentRunResponse)
async def run_agent(data: AgentRunRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    supplied = data.thread_id or str(uuid4())
    thread_id = supplied if supplied.startswith(f"u{user.id}-") else f"u{user.id}-{supplied}"
    result = await travel_graph.ainvoke({"user_id": user.id, "thread_id": thread_id,
        "prompt": data.prompt, "memory": load_user_memory(db, user.id), "timezone": data.timezone},
        {"configurable": {"thread_id": thread_id}})
    plan = TripPlan.model_validate(result["plan"])
    trip = Trip(user_id=user.id, destination=plan.destination, start_date=plan.start_date,
                end_date=plan.end_date, budget=plan.total_budget, currency=plan.currency.upper(),
                request_text=data.prompt, itinerary=plan.model_dump(mode="json"), status="planned")
    db.add(trip); db.flush()
    save_plan_preferences(db, user.id, plan)
    pending_id = None
    if result.get("calendar", {}).get("connected"):
        try: zone = ZoneInfo(data.timezone)
        except ZoneInfoNotFoundError: zone = ZoneInfo("UTC")
        payload = {"summary": f"Trip to {plan.destination}", "description": plan.summary,
                   "start": datetime.combine(plan.start_date, time(9), zone).isoformat(),
                   "end": datetime.combine(plan.end_date, time(18), zone).isoformat(),
                   "timezone": str(zone), "location": plan.destination}
        pending_id = str(uuid4())
        db.add(PendingAction(id=pending_id, user_id=user.id, trip_id=trip.id, thread_id=thread_id,
                             action_type="create_calendar_event", payload=payload, status="pending"))
    db.commit()
    return AgentRunResponse(thread_id=thread_id, trip_id=trip.id, plan=plan,
        hotels=[HotelOffer.model_validate(x) for x in result.get("hotels", [])],
        calendar=result.get("calendar", {}), review=ReviewResult.model_validate(result["review"]),
        pending_action_id=pending_id, requires_approval=pending_id is not None)

@router.post("/actions/{action_id}/approve", response_model=ActionResponse)
async def approve_action(action_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    action = db.scalar(select(PendingAction).where(PendingAction.id == action_id,
                                                    PendingAction.user_id == user.id).with_for_update())
    if not action: raise HTTPException(status_code=404, detail="Pending action not found")
    if action.status != "pending": raise HTTPException(status_code=409, detail="Action is no longer pending")
    result = await create_event(user.id, action.payload)
    action.status, action.executed_at = "approved", datetime.now(timezone.utc)
    db.commit()
    return ActionResponse(action_id=action.id, status="approved", result=result)

@router.post("/actions/{action_id}/reject", response_model=ActionResponse)
def reject_action(action_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    action = db.scalar(select(PendingAction).where(PendingAction.id == action_id,
                                                    PendingAction.user_id == user.id).with_for_update())
    if not action: raise HTTPException(status_code=404, detail="Pending action not found")
    if action.status != "pending": raise HTTPException(status_code=409, detail="Action is no longer pending")
    action.status, action.executed_at = "rejected", datetime.now(timezone.utc)
    db.commit()
    return ActionResponse(action_id=action.id, status="rejected")
