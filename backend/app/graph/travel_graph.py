from datetime import datetime, time
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from fastapi import HTTPException
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from app.graph.state import TravelState
from app.schemas.hotel import HotelSearchRequest
from app.schemas.planner import TripPlan
from app.services.calendar_mcp import check_availability
from app.services.hotel_mcp import search_hotels_via_mcp
from app.services.planner import create_trip_plan

async def planner_node(state: TravelState):
    memory = state.get("memory", {})
    context = f"\nKnown user preferences: {memory}" if memory else ""
    plan = create_trip_plan(state["prompt"] + context)
    return {"plan": plan.model_dump(mode="json")}

async def hotel_node(state: TravelState):
    plan = TripPlan.model_validate(state["plan"])
    try:
        hotels = await search_hotels_via_mcp(HotelSearchRequest(
            city_code=plan.city_code, check_in=plan.start_date, check_out=plan.end_date,
            adults=plan.travelers, max_price=plan.max_hotel_total_price,
            currency=plan.currency, rating=plan.hotel_rating, limit=5,
        ))
        return {"hotels": [hotel.model_dump(mode="json") for hotel in hotels], "hotel_error": None}
    except HTTPException as exc:
        return {"hotels": [], "hotel_error": str(exc.detail)}

async def calendar_node(state: TravelState):
    plan = TripPlan.model_validate(state["plan"])
    timezone_name = state.get("timezone", "UTC")
    try:
        zone = ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError:
        zone, timezone_name = ZoneInfo("UTC"), "UTC"
    start = datetime.combine(plan.start_date, time.min, zone).isoformat()
    end = datetime.combine(plan.end_date, time.max, zone).isoformat()
    try:
        result = await check_availability(state["user_id"], start, end, timezone_name)
        return {"calendar": result}
    except HTTPException as exc:
        return {"calendar": {"connected": False, "busy": [], "has_conflicts": False,
                             "message": str(exc.detail)}}

async def review_node(state: TravelState):
    plan = TripPlan.model_validate(state["plan"])
    issues = []
    budget_valid = plan.budget.total <= plan.total_budget
    if not budget_valid:
        issues.append("Budget breakdown exceeds the requested total")
    calendar_conflict = bool(state.get("calendar", {}).get("has_conflicts"))
    if calendar_conflict:
        issues.append("Google Calendar contains events during the proposed trip")
    if state.get("hotel_error"):
        issues.append("Live hotel search was unavailable")
    return {"review": {"valid": budget_valid and not calendar_conflict,
                       "budget_valid": budget_valid, "calendar_conflict": calendar_conflict,
                       "hotel_results": len(state.get("hotels", [])), "issues": issues}}

builder = StateGraph(TravelState)
builder.add_node("planner", planner_node)
builder.add_node("hotels", hotel_node)
builder.add_node("calendar", calendar_node)
builder.add_node("review", review_node)
builder.add_edge(START, "planner")
builder.add_edge("planner", "hotels")
builder.add_edge("hotels", "calendar")
builder.add_edge("calendar", "review")
builder.add_edge("review", END)
travel_graph = builder.compile(checkpointer=InMemorySaver())
