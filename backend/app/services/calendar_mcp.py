import json
from fastapi import HTTPException
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
from app.core.config import settings

async def _call(tool: str, arguments: dict) -> dict:
    try:
        async with streamable_http_client(settings.calendar_mcp_url) as (read, write, _):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(tool, arguments)
        if result.isError:
            raise RuntimeError(result.content[0].text if result.content else "Calendar MCP failed")
        text = next((item.text for item in result.content if hasattr(item, "text")), "{}")
        return json.loads(text)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Calendar MCP unavailable: {exc}") from exc

async def check_availability(user_id: int, time_min: str, time_max: str, timezone: str = "UTC"):
    return await _call("check_availability", {"user_id": user_id, "time_min": time_min,
                                               "time_max": time_max, "timezone": timezone})

async def create_event(user_id: int, payload: dict):
    return await _call("create_trip_event", {"user_id": user_id, **payload})
