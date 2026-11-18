from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field

from backend.app.models.weather import WeatherDetail


class AqiCategory(str, Enum):
    GOOD = "Good"
    SATISFACTORY = "Satisfactory"
    MODERATE = "Moderate"
    POOR = "Poor"
    VERY_POOR = "Very Poor"
    SEVERE = "Severe"
    SEVERE_PLUS = "Severe+"


class PollutantDetail(BaseModel):
    name: str = Field(..., description="Chemical or pollutant name (e.g. PM2.5, NO2)")
    value: float = Field(..., description="Observed concentration value")
    unit: str = Field(..., description="Measurement unit (e.g. µg/m³, mg/m³)")
    sub_index: int = Field(..., description="Calculated sub-index for this pollutant")
    category: AqiCategory = Field(..., description="Air quality category for this pollutant")
    standard_limit: float = Field(..., description="CPCB 24-hr national standard threshold")
    who_limit: float = Field(..., description="WHO 24-hr guideline benchmark")


class StationInfo(BaseModel):
    id: str
    name: str
    city: str
    state: str
    latitude: float
    longitude: float
    is_hotspot: bool = False


class HealthAdvisory(BaseModel):
    general_advice: str
    children_and_seniors: str
    patients_with_respiratory_issues: str
    outdoor_activity: str
    mask_recommendation: str
    purifier_recommendation: str
    ventilation_window: str


class HourlyAqiPoint(BaseModel):
    hour: str
    time: datetime
    aqi: int
    category: AqiCategory
    pm25: float
    pm10: float


class CurrentAqiResponse(BaseModel):
    station: StationInfo
    aqi: int
    category: AqiCategory
    prominent_pollutant: str
    pollutants: Dict[str, PollutantDetail]
    health_advisory: HealthAdvisory
    weather: Union[WeatherDetail, Dict[str, Any]]
    data_source: str
    last_updated: datetime
    is_demo_data: bool = True


class ForecastResponse(BaseModel):
    station_id: str
    station_name: str
    forecast_24h: List[HourlyAqiPoint]
    peak_aqi_window: str
    safest_outdoor_window: str
    is_demo_data: bool = True
