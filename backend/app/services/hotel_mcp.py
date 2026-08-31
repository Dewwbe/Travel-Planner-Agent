import json
from fastapi import HTTPException
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
from app.core.config import settings
from app.schemas.hotel import HotelOffer, HotelSearchRequest

async def search_hotels_via_mcp(query: HotelSearchRequest) -> list[HotelOffer]:
    arguments = {
        "city_code": query.city_code.upper(), "check_in": query.check_in.isoformat(),
        "check_out": query.check_out.isoformat(), "adults": query.adults,
        "max_price": float(query.max_price) if query.max_price else None,
        "currency": query.currency.upper(), "rating": query.rating, "limit": query.limit,
    }
    try:
        async with streamable_http_client(settings.hotel_mcp_url) as (read, write, _):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool("search_hotels", arguments)
        if result.isError:
            raise RuntimeError(result.content[0].text if result.content else "Hotel MCP tool failed")
        content = next((item.text for item in result.content if hasattr(item, "text")), "[]")
        return [HotelOffer.model_validate(item) for item in json.loads(content)]
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Hotel search unavailable: {exc}") from exc
