from datetime import datetime
from fastapi import APIRouter
from backend.app.core.config import settings
from backend.app.models.response import ApiResponse

router = APIRouter()


@router.get("", response_model=ApiResponse[dict])
def check_health():
    return ApiResponse(
        success=True,
        message="AirSaathi AI API is healthy",
        data={
            "service": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "environment": settings.ENVIRONMENT,
            "mock_mode": settings.MOCK_MODE,
            "status": "online",
            "server_time": datetime.utcnow().isoformat(),
        },
        is_demo_data=False,
    )
