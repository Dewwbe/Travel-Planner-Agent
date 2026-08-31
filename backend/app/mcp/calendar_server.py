import json
from mcp.server.fastmcp import FastMCP
from app.db.session import SessionLocal
from app.services.google_calendar import calendar_service

mcp = FastMCP("TripPilot Google Calendar", host="0.0.0.0", port=8002)

@mcp.tool()
def check_availability(user_id: int, time_min: str, time_max: str, timezone: str = "UTC") -> str:
    """Read a user's primary Google Calendar and return busy periods."""
    with SessionLocal() as db:
        service = calendar_service(db, user_id)
        result = service.freebusy().query(body={
            "timeMin": time_min, "timeMax": time_max, "timeZone": timezone,
            "items": [{"id": "primary"}],
        }).execute()
    busy = result.get("calendars", {}).get("primary", {}).get("busy", [])
    return json.dumps({"connected": True, "busy": busy, "has_conflicts": bool(busy)})

@mcp.tool()
def create_trip_event(user_id: int, summary: str, description: str, start: str,
                      end: str, timezone: str = "UTC", location: str | None = None) -> str:
    """Create a Google Calendar event after application-level human approval."""
    body = {"summary": summary, "description": description,
            "start": {"dateTime": start, "timeZone": timezone},
            "end": {"dateTime": end, "timeZone": timezone}}
    if location:
        body["location"] = location
    with SessionLocal() as db:
        event = calendar_service(db, user_id).events().insert(calendarId="primary", body=body).execute()
    return json.dumps({"event_id": event.get("id"), "html_link": event.get("htmlLink"),
                       "status": event.get("status")})

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
