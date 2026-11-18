from typing import List
from fastapi import APIRouter, Query
from backend.app.models.aqi import CurrentAqiResponse, ForecastResponse, StationInfo
from backend.app.models.response import ApiResponse
from backend.app.services.live_aqi_provider import get_active_aqi_provider

router = APIRouter()


@router.get("/stations", response_model=ApiResponse[List[StationInfo]])
def list_stations():
    provider = get_active_aqi_provider()
    stations = provider.get_stations()
    return ApiResponse(
        success=True,
        message=f"Retrieved {len(stations)} air quality monitoring stations",
        data=stations,
        is_demo_data=not provider.is_live(),
    )


@router.get("/current", response_model=ApiResponse[CurrentAqiResponse])
def get_current_aqi(
    station_id: str = Query("delhi-anand-vihar", description="Identifier of the monitoring station")
):
    provider = get_active_aqi_provider()
    data = provider.get_current_aqi(station_id)
    return ApiResponse(
        success=True,
        message="Current air quality index retrieved",
        data=data,
        is_demo_data=data.is_demo_data,
    )


@router.get("/forecast", response_model=ApiResponse[ForecastResponse])
def get_forecast(
    station_id: str = Query("delhi-anand-vihar", description="Identifier of the monitoring station")
):
    provider = get_active_aqi_provider()
    forecast = provider.get_forecast(station_id)
    return ApiResponse(
        success=True,
        message="24-hour AQI diurnal projection retrieved",
        data=forecast,
        is_demo_data=forecast.is_demo_data,
    )
