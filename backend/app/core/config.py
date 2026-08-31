from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "TripPilot API"
    api_v1_prefix: str = "/api/v1"

    # Database
    database_url: str = (
        "postgresql+psycopg://travel:"
        "travel_dev_password@db:5432/travel_agent"
    )

    # Authentication
    jwt_secret: str = "development-only-secret-change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440

    # Frontend
    backend_cors_origins: str = "http://localhost:3000"

    # OpenAI
    openai_api_key: str = ""
    openai_model: str = "gpt-5-mini"

    # LiteAPI / Hotel MCP
    liteapi_api_key: str = ""
    liteapi_base_url: str = "https://api.liteapi.travel/v3.0"
    liteapi_guest_nationality: str = "LK"
    hotel_mcp_url: str = "http://hotel-mcp:8001/mcp"

    # Google Calendar
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = (
        "http://localhost:8000/api/v1/calendar/oauth/callback"
    )
    google_oauth_success_url: str = (
        "http://localhost:3000/dashboard?calendar=connected"
    )
    calendar_mcp_url: str = "http://calendar-mcp:8002/mcp"
    token_encryption_key: str = ""

    model_config = SettingsConfigDict(
        env_file="../.env",
        extra="ignore",
        case_sensitive=False,
    )

    @property
    def cors_origins(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.backend_cors_origins.split(",")
            if origin.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()