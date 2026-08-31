from typing import Any, TypedDict

class TravelState(TypedDict, total=False):
    user_id: int
    thread_id: str
    prompt: str
    memory: dict[str, Any]
    timezone: str
    plan: dict[str, Any]
    hotels: list[dict[str, Any]]
    hotel_error: str | None
    calendar: dict[str, Any]
    review: dict[str, Any]
