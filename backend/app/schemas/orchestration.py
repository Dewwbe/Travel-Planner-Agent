from typing import Any, Literal
from pydantic import BaseModel, Field
from app.schemas.hotel import HotelOffer
from app.schemas.planner import TripPlan

class AgentRunRequest(BaseModel):
    prompt: str = Field(min_length=10, max_length=3000)
    thread_id: str | None = Field(default=None, max_length=100)
    timezone: str = Field(default="UTC", max_length=80)

class ReviewResult(BaseModel):
    valid: bool
    budget_valid: bool
    calendar_conflict: bool
    hotel_results: int
    issues: list[str]

class AgentRunResponse(BaseModel):
    thread_id: str
    trip_id: int
    plan: TripPlan
    hotels: list[HotelOffer]
    calendar: dict[str, Any]
    review: ReviewResult
    pending_action_id: str | None
    requires_approval: bool

class ActionResponse(BaseModel):
    action_id: str
    status: Literal["approved", "rejected"]
    result: dict[str, Any] | None = None
