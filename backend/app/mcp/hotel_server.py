import json
from decimal import Decimal
from typing import Any

from mcp.server.fastmcp import FastMCP

from app.services.liteapi import (
    extract_currency,
    extract_price,
    liteapi_client,
)


mcp = FastMCP(
    "TripPilot Hotel Search",
    host="0.0.0.0",
    port=8001,
)


def get_hotel_data(item: dict[str, Any]) -> dict[str, Any]:
    hotel = item.get("hotel")

    if isinstance(hotel, dict):
        return hotel

    hotel_data = item.get("hotelData")

    if isinstance(hotel_data, dict):
        return hotel_data

    return item


def get_room_types(item: dict[str, Any]) -> list[dict[str, Any]]:
    room_types = item.get("roomTypes", [])

    if not isinstance(room_types, list):
        return []

    return [
        room
        for room in room_types
        if isinstance(room, dict)
    ]


def get_coordinates(
    hotel: dict[str, Any],
) -> tuple[float | None, float | None]:
    latitude = hotel.get("latitude")
    longitude = hotel.get("longitude")

    coordinates = hotel.get("coordinates")

    if isinstance(coordinates, dict):
        latitude = latitude or coordinates.get("latitude")
        longitude = longitude or coordinates.get("longitude")

    return latitude, longitude


@mcp.tool()
async def search_hotels(
    city_code: str,
    check_in: str,
    check_out: str,
    adults: int = 1,
    max_price: float | None = None,
    currency: str = "USD",
    rating: int | None = None,
    limit: int = 8,
) -> str:
    """
    Search live LiteAPI hotel rates using an IATA destination
    code, dates, guests, currency, star rating and total budget.
    """

    raw_hotels = await liteapi_client.search_hotel_rates(
        iata_code=city_code,
        check_in=check_in,
        check_out=check_out,
        adults=adults,
        currency=currency,
        rating=rating,
        limit=limit,
    )

    results: list[dict[str, Any]] = []

    for item in raw_hotels:
        if not isinstance(item, dict):
            continue

        hotel = get_hotel_data(item)
        room_types = get_room_types(item)

        if not room_types:
            continue

        room = room_types[0]
        price = extract_price(room)

        if price is None:
            continue

        if (
            max_price is not None
            and price > Decimal(str(max_price))
        ):
            continue

        hotel_id = (
            hotel.get("id")
            or hotel.get("hotelId")
            or item.get("hotelId")
            or item.get("id")
        )

        if not hotel_id:
            continue

        name = (
            hotel.get("name")
            or hotel.get("hotelName")
            or item.get("hotelName")
            or "Unknown hotel"
        )

        hotel_rating = (
            hotel.get("starRating")
            or hotel.get("rating")
            or item.get("starRating")
            or rating
        )

        try:
            normalized_rating = (
                int(float(hotel_rating))
                if hotel_rating is not None
                else None
            )
        except (TypeError, ValueError):
            normalized_rating = rating

        latitude, longitude = get_coordinates(hotel)

        room_description = (
            room.get("name")
            or room.get("roomName")
            or room.get("description")
            or room.get("boardName")
            or "Available room"
        )

        results.append(
            {
                "hotel_id": str(hotel_id),
                "name": str(name),
                "rating": normalized_rating,
                "city_code": city_code.upper(),
                "latitude": latitude,
                "longitude": longitude,
                "room_description": str(room_description),
                "price_total": str(price),
                "currency": extract_currency(
                    room,
                    currency,
                ),
                "check_in": check_in,
                "check_out": check_out,
            }
        )

    results.sort(
        key=lambda hotel: Decimal(hotel["price_total"])
    )

    return json.dumps(results[:limit])


@mcp.tool()
async def compare_hotels(hotels_json: str) -> str:
    """
    Rank normalized hotels by rating and then by total price.
    """

    hotels = json.loads(hotels_json)

    if not isinstance(hotels, list):
        raise ValueError("hotels_json must contain a list")

    ranked = sorted(
        hotels,
        key=lambda hotel: (
            -int(hotel.get("rating") or 0),
            Decimal(str(hotel.get("price_total", "0"))),
        ),
    )

    return json.dumps(ranked)


if __name__ == "__main__":
    mcp.run(transport="streamable-http")