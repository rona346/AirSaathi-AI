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


class GrapStage(str, Enum):
    NONE = "None"
    STAGE_1 = "Stage I"
    STAGE_2 = "Stage II"
    STAGE_3 = "Stage III"
    STAGE_4 = "Stage IV"


class GrapStatus(BaseModel):
    applicable: bool = Field(
        ...,
        description="Whether CAQM GRAP framework applies to this region (Delhi-NCR only)",
    )
    stage: GrapStage = Field(
        ...,
        description="Indicative GRAP stage based on AQI or None",
    )
    stage_name: str = Field(
        ...,
        description="Full descriptive title of the stage according to the CAQM schedule",
    )
    aqi_threshold: str = Field(
        ...,
        description="Official AQI bracket under CAQM schedule (e.g. '201-300', '> 450')",
    )
    status_type: str = Field(
        "indicative_aqi_based",
        description="Type of status: indicative_aqi_based or official_order",
    )
    is_official_order: bool = Field(
        False,
        description="Whether this stage is verified by an active statutory CAQM executive order",
    )
    curbs_summary: List[str] = Field(
        default_factory=list,
        description="Key mitigation measures and citizen/municipal curbs active under this stage",
    )
    notice: str = Field(
        ...,
        description="Statutory context and legal/advisory notice",
    )


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
    grap_status: Optional[GrapStatus] = None


class ForecastResponse(BaseModel):
    station_id: str
    station_name: str
    forecast_24h: List[HourlyAqiPoint]
    peak_aqi_window: str
    safest_outdoor_window: str
    is_demo_data: bool = True
