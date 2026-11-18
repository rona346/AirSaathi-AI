from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class WeatherDetail(BaseModel):
    temperature_c: float = Field(..., description="Ambient air temperature in degrees Celsius")
    humidity_percent: float = Field(..., description="Relative humidity percentage (0-100%)")
    wind_speed_kmh: float = Field(..., description="Wind speed in kilometers per hour (km/h)")
    wind_direction: str = Field(..., description="Cardinal wind direction (e.g. N, NE, E, SE, S, SW, W, NW)")
    wind_direction_deg: Optional[float] = Field(None, description="Wind direction in meteorological degrees (0-360)")
    precipitation_mm: float = Field(0.0, description="Precipitation or rainfall in millimeters (mm)")
    weather_condition: str = Field("Clear", description="Interpreted weather condition descriptor (e.g. Clear, Overcast, Rain)")
    visibility_km: Optional[float] = Field(None, description="Atmospheric horizontal visibility in kilometers (km)")
    mixing_layer_height_m: Optional[float] = Field(None, description="Estimated boundary / mixing layer height in meters (m)")
    observed_at: datetime = Field(..., description="Timestamp of the weather observation")
    source: str = Field("Open-Meteo", description="Name of the weather data provider or baseline source")
    is_demo_data: bool = Field(False, description="Flag indicating whether data is demonstration/fallback")
