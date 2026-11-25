"""Dedicated Weather Service API endpoints.

Provides real-time ambient weather metrics (temperature, humidity, wind, precipitation)
powered by Open-Meteo, with intelligent station coordinate resolution, in-memory caching,
and graceful fallback to calibrated demonstration baselines.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from backend.app.core.utils import resolve_query_param

from backend.app.models.response import ApiResponse
from backend.app.models.weather import WeatherDetail
from backend.app.services.aqi_service import AqiService
from backend.app.services.weather_service import weather_service

router = APIRouter()


@router.get("/current", response_model=ApiResponse[WeatherDetail])
def get_current_weather(
    station_id: Optional[str] = Query(None, description="Monitoring station identifier to resolve coordinates"),
    latitude: Optional[float] = Query(None, description="Geographic latitude coordinate (-90 to 90)"),
    longitude: Optional[float] = Query(None, description="Geographic longitude coordinate (-180 to 180)"),
):
    """
    Retrieve real-time ambient weather telemetry.
    Resolves coordinates from explicit (latitude, longitude) query or from the specified station_id.
    """
    # Resolve FastAPI Query defaults when invoked directly as a Python function
    latitude = resolve_query_param(latitude, None)
    longitude = resolve_query_param(longitude, None)
    station_id = resolve_query_param(station_id, None)

    target_lat: float
    target_lon: float
    target_station_name: Optional[str] = None
    target_sid: Optional[str] = station_id

    if latitude is not None and longitude is not None:
        if not (-90.0 <= latitude <= 90.0 and -180.0 <= longitude <= 180.0):
            raise HTTPException(status_code=400, detail="Invalid coordinates: latitude must be [-90, 90] and longitude [-180, 180]")
        target_lat = latitude
        target_lon = longitude
    else:
        resolved_station = AqiService.get_station_by_id_or_city(station_id or "delhi-anand-vihar")
        if resolved_station:
            target_lat = resolved_station.latitude
            target_lon = resolved_station.longitude
            target_station_name = resolved_station.name
            target_sid = resolved_station.id
        else:
            # Default to primary Delhi monitoring station if unspecified
            default_station = AqiService.get_stations()[0]
            target_lat = default_station.latitude
            target_lon = default_station.longitude
            target_station_name = default_station.name
            target_sid = default_station.id

    weather_detail = weather_service.get_weather_sync(
        latitude=target_lat,
        longitude=target_lon,
        station_id=target_sid,
        station_name=target_station_name,
    )

    return ApiResponse(
        success=True,
        message="Current weather telemetry retrieved successfully",
        data=weather_detail,
        is_demo_data=weather_detail.is_demo_data,
    )
