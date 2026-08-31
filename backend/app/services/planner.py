from fastapi import HTTPException
from openai import OpenAI
from app.core.config import settings
from app.schemas.planner import TripPlan

SYSTEM_PROMPT = """You are a careful travel planning agent. Convert the user's request into a realistic,
structured trip plan. Use exact future dates. If dates, currency, travelers, or budget allocation are missing,
make conservative assumptions and list them. Keep the budget within total_budget. Use the correct IATA city
code. Keep the itinerary geographically sensible. Do not claim hotel prices are live; that is checked separately."""

def create_trip_plan(prompt: str) -> TripPlan:
    if not settings.openai_api_key:
        raise HTTPException(status_code=503, detail="OPENAI_API_KEY is not configured")
    try:
        client = OpenAI(api_key=settings.openai_api_key)
        response = client.responses.parse(
            model=settings.openai_model,
            input=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": prompt}],
            text_format=TripPlan,
        )
        if not response.output_parsed:
            raise ValueError("The model did not return a structured plan")
        return response.output_parsed
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"AI planner failed: {exc}") from exc
