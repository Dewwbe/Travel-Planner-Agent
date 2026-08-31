from datetime import date
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, Field, model_validator

class PlanRequest(BaseModel):
    prompt: str = Field(min_length=10, max_length=3000)
    trip_id: int | None = None

class Activity(BaseModel):
    time: str
    title: str
    description: str
    estimated_cost: Decimal = Field(ge=0)

class DayPlan(BaseModel):
    day: int = Field(ge=1)
    date: date
    theme: str
    activities: list[Activity]

class BudgetBreakdown(BaseModel):
    accommodation: Decimal = Field(ge=0)
    food: Decimal = Field(ge=0)
    transport: Decimal = Field(ge=0)
    activities: Decimal = Field(ge=0)
    contingency: Decimal = Field(ge=0)
    total: Decimal = Field(ge=0)

class TripPlan(BaseModel):
    destination: str
    city_code: str = Field(min_length=3, max_length=3, description="IATA city code")
    start_date: date
    end_date: date
    travelers: int = Field(default=1, ge=1, le=9)
    currency: str = Field(min_length=3, max_length=3)
    total_budget: Decimal = Field(gt=0)
    max_hotel_total_price: Decimal = Field(gt=0)
    hotel_rating: int | None = Field(default=None, ge=1, le=5)
    summary: str
    days: list[DayPlan]
    budget: BudgetBreakdown
    assumptions: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_dates(self):
        if self.end_date <= self.start_date:
            raise ValueError("end_date must be after start_date")
        return self

class PlanResponse(BaseModel):
    trip_id: int
    plan: TripPlan
    status: Literal["planned"] = "planned"
