from typing import List
from fastapi import APIRouter, HTTPException, Query
from backend.app.models.aqi import CurrentAqiResponse, ForecastResponse, StationInfo
from backend.app.models.response import ApiResponse
from backend.app.services.aqi_service import AqiService

router = APIRouter()


@router.get("/stations", response_model=ApiResponse[List[StationInfo]])
def list_stations():
    stations = AqiService.get_stations()
    return ApiResponse(
        success=True,
        message=f"Retrieved {len(stations)} air quality monitoring stations",
        data=stations,
        is_demo_data=True,
    )


@router.get("/current", response_model=ApiResponse[CurrentAqiResponse])
def get_current_aqi(
    station_id: str = Query("delhi-anand-vihar", description="Identifier of the monitoring station")
):
    data = AqiService.get_current_aqi(station_id)
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
    forecast = AqiService.get_forecast(station_id)
    return ApiResponse(
        success=True,
        message="24-hour AQI diurnal projection retrieved",
        data=forecast,
        is_demo_data=forecast.is_demo_data,
    )
