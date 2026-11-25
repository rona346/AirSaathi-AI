from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "AirSaathi AI Backend"
    API_V1_STR: str = "/api/v1"
    VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"

    # CORS origins
    BACKEND_CORS_ORIGINS: List[str] = [
        "https://air-saathi-ai.vercel.app",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                import json
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            return [str(i).strip() for i in v if str(i).strip()]
        return v

    # Secrets and keys strictly on the backend (Never exposed to frontend or Git)
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL_ID: str = "gemini-3.8-flash"
    # Firebase Service Account & Project Configuration (Strictly backend-only)
    FIREBASE_PROJECT_ID: str = ""
    FIREBASE_SERVICE_ACCOUNT_PATH: str = ""
    FIREBASE_SERVICE_ACCOUNT_JSON: str = ""
    FIREBASE_STORAGE_BUCKET: str = ""

    # Live AQI Provider API Keys (Strictly backend-only)
    DATAGOVIN_API_KEY: str = ""
    OPENAQ_API_KEY: str = ""

    # Cache duration for ambient measurements (in seconds, default 15 minutes)
    AQI_CACHE_TTL_SECONDS: int = 900

    # Weather Service settings (Open-Meteo)
    WEATHER_CACHE_TTL_SECONDS: int = 900
    WEATHER_REQUEST_TIMEOUT_SECONDS: float = 6.0

    # Demonstration mode flag (Set to False to enable live provider when credentials exist)
    MOCK_MODE: bool = False

    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=("backend/.env", ".env"),
        extra="ignore",
    )


settings = Settings()
