from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field, model_validator


class HotelSearchRequest(BaseModel):
    city_code: str = Field(
        min_length=3,
        max_length=3,
    )

    check_in: date
    check_out: date

    adults: int = Field(
        default=1,
        ge=1,
        le=9,
    )

    max_price: Decimal | None = Field(
        default=None,
        gt=0,
    )

    currency: str = Field(
        default="USD",
        min_length=3,
        max_length=3,
    )

    rating: int | None = Field(
        default=None,
        ge=1,
        le=5,
    )

    limit: int = Field(
        default=8,
        ge=1,
        le=20,
    )

    @model_validator(mode="after")
    def validate_dates(self):
        if self.check_out <= self.check_in:
            raise ValueError(
                "check_out must be after check_in"
            )

        return self


class HotelOffer(BaseModel):
    hotel_id: str
    name: str
    rating: int | None = None
    city_code: str
    latitude: float | None = None
    longitude: float | None = None
    room_description: str | None = None
    price_total: Decimal
    currency: str
    check_in: date
    check_out: date


class HotelSearchResponse(BaseModel):
    hotels: list[HotelOffer]
    source: str = "LiteAPI Hotel Search via MCP"