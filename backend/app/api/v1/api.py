from fastapi import APIRouter
from backend.app.api.v1.endpoints import aqi, health, routine

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(aqi.router, prefix="/aqi", tags=["Air Quality"])
api_router.include_router(routine.router, prefix="/routine", tags=["Routine Planner"])
