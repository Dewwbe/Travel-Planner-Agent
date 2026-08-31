from datetime import datetime
from pydantic import BaseModel, Field, model_validator

class OAuthStartResponse(BaseModel):
    authorization_url: str

class CalendarStatusResponse(BaseModel):
    connected: bool

class FreeBusyRequest(BaseModel):
    time_min: datetime
    time_max: datetime
    timezone: str = "UTC"
    @model_validator(mode="after")
    def dates_valid(self):
        if self.time_max <= self.time_min:
            raise ValueError("time_max must be after time_min")
        return self

class CalendarEventPayload(BaseModel):
    summary: str = Field(min_length=2, max_length=200)
    description: str = Field(default="", max_length=4000)
    start: datetime
    end: datetime
    timezone: str = "UTC"
    location: str | None = None
