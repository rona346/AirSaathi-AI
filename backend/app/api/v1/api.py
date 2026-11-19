from fastapi import APIRouter
from backend.app.api.v1.endpoints import aqi, chat, health, impact, indoor, mobility, routine, user, weather

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(user.router, prefix="/user", tags=["User Profile & Persistence"])
api_router.include_router(aqi.router, prefix="/aqi", tags=["Air Quality"])
api_router.include_router(weather.router, prefix="/weather", tags=["Weather"])
api_router.include_router(routine.router, prefix="/routine", tags=["Routine Planner"])
api_router.include_router(indoor.router, prefix="/indoor", tags=["Indoor Air Quality"])
api_router.include_router(chat.router, prefix="/chat", tags=["Environmental Chatbot"])
api_router.include_router(mobility.router, prefix="/mobility", tags=["Sustainable Mobility"])
api_router.include_router(impact.router, prefix="/impact", tags=["Environmental Impact Tracker"])
