from decimal import Decimal, InvalidOperation
from typing import Any

import httpx

from app.core.config import settings


class LiteAPIClient:
    def __init__(self) -> None:
        self.base_url = settings.liteapi_base_url.rstrip("/")

    def _headers(self) -> dict[str, str]:
        if not settings.liteapi_api_key:
            raise RuntimeError("LITEAPI_API_KEY is not configured")

        return {
            "X-API-Key": settings.liteapi_api_key,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    async def search_hotel_rates(
        self,
        iata_code: str,
        check_in: str,
        check_out: str,
        adults: int,
        currency: str,
        rating: int | None,
        limit: int,
    ) -> list[dict[str, Any]]:
        payload: dict[str, Any] = {
            "iataCode": iata_code.upper(),
            "checkin": check_in,
            "checkout": check_out,
            "currency": currency.upper(),
            "guestNationality": (
                settings.liteapi_guest_nationality.upper()
            ),
            "occupancies": [
                {
                    "adults": adults,
                }
            ],
            "limit": limit,
            "timeout": 10,
            "maxRatesPerHotel": 1,
            "includeHotelData": True,
        }

        if rating is not None:
            payload["starRating"] = [float(rating)]

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{self.base_url}/hotels/rates",
                headers=self._headers(),
                json=payload,
            )

        if response.status_code == 204:
            return []

        if response.status_code >= 400:
            try:
                error_body = response.json()
            except ValueError:
                error_body = response.text

            raise RuntimeError(
                f"LiteAPI returned {response.status_code}: "
                f"{error_body}"
            )

        body = response.json()
        data = body.get("data", [])

        if not isinstance(data, list):
            return []

        return data


def decimal_value(value: Any) -> Decimal | None:
    """
    Extract a Decimal from the different price structures that
    may appear inside a LiteAPI rate response.
    """

    if value is None:
        return None

    if isinstance(value, Decimal):
        return value

    if isinstance(value, (int, float, str)):
        try:
            return Decimal(str(value))
        except (InvalidOperation, ValueError):
            return None

    if isinstance(value, list):
        for item in value:
            amount = decimal_value(item)

            if amount is not None:
                return amount

        return None

    if isinstance(value, dict):
        preferred_keys = (
            "amount",
            "total",
            "value",
            "price",
            "gross",
            "net",
        )

        for key in preferred_keys:
            if key in value:
                amount = decimal_value(value[key])

                if amount is not None:
                    return amount

    return None


def extract_price(room: dict[str, Any]) -> Decimal | None:
    candidates = [
        room.get("total"),
        room.get("price"),
        room.get("retailRate"),
        room.get("retailPrice"),
        room.get("totalPrice"),
    ]

    rates = room.get("rates", [])

    if isinstance(rates, list) and rates:
        first_rate = rates[0]

        if isinstance(first_rate, dict):
            candidates.extend(
                [
                    first_rate.get("total"),
                    first_rate.get("price"),
                    first_rate.get("retailRate"),
                    first_rate.get("retailPrice"),
                    first_rate.get("totalPrice"),
                ]
            )

    for candidate in candidates:
        amount = decimal_value(candidate)

        if amount is not None:
            return amount

    return None


def extract_currency(
    room: dict[str, Any],
    default_currency: str,
) -> str:
    direct_currency = room.get("currency")

    if direct_currency:
        return str(direct_currency).upper()

    price_objects = [
        room.get("price"),
        room.get("retailRate"),
        room.get("retailPrice"),
    ]

    rates = room.get("rates", [])

    if isinstance(rates, list) and rates:
        first_rate = rates[0]

        if isinstance(first_rate, dict):
            price_objects.extend(
                [
                    first_rate.get("price"),
                    first_rate.get("retailRate"),
                    first_rate.get("retailPrice"),
                ]
            )

    for price_object in price_objects:
        if isinstance(price_object, dict):
            currency = price_object.get("currency")

            if currency:
                return str(currency).upper()

            total = price_object.get("total")

            if isinstance(total, list) and total:
                first_total = total[0]

                if isinstance(first_total, dict):
                    currency = first_total.get("currency")

                    if currency:
                        return str(currency).upper()

    return default_currency.upper()


liteapi_client = LiteAPIClient()