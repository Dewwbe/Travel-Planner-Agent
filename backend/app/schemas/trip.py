from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field, model_validator

class TripCreate(BaseModel):
    destination: str = Field(min_length=2, max_length=120)
    start_date: date
    end_date: date
    budget: Decimal = Field(gt=0)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    request_text: str | None = Field(default=None, max_length=2000)

    @model_validator(mode="after")
    def dates_are_valid(self):
        if self.end_date < self.start_date:
            raise ValueError("End date must be on or after start date")
        return self

class TripResponse(TripCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    status: str
    itinerary: dict | None
    created_at: datetime

