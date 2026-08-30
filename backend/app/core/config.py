from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "TripPilot API"
    api_v1_prefix: str = "/api/v1"
    database_url: str = "postgresql+psycopg://travel:travel_dev_password@localhost:5432/travel_agent"
    jwt_secret: str = "development-only-secret-change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440
    backend_cors_origins: str = "http://localhost:3000"
    model_config = SettingsConfigDict(env_file="../.env", extra="ignore")

    @property
    def cors_origins(self):
        return [x.strip() for x in self.backend_cors_origins.split(",") if x.strip()]

@lru_cache
def get_settings():
    return Settings()

settings = get_settings()

