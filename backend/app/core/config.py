from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "AirSaathi AI Backend"
    API_V1_STR: str = "/api/v1"
    VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"

    # CORS origins
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    # Secrets and keys strictly on the backend (Never exposed to frontend or Git)
    GEMINI_API_KEY: str = ""
    FIREBASE_PROJECT_ID: str = ""

    # Live AQI Provider API Keys (Strictly backend-only)
    DATAGOVIN_API_KEY: str = ""
    OPENAQ_API_KEY: str = ""

    # Cache duration for ambient measurements (in seconds, default 15 minutes)
    AQI_CACHE_TTL_SECONDS: int = 900

    # Demonstration mode flag (Set to False to enable live provider when credentials exist)
    MOCK_MODE: bool = False

    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=("backend/.env", ".env"),
        extra="ignore",
    )


settings = Settings()
