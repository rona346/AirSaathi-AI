"""Pydantic Models for Module 6: Environmental Impact Tracker.

Defines schemas for:
- Activity logging (clean commute, carpool, active travel, indoor safeguards)
- Detailed per-passenger and vehicle-level emission accounting
- Transparent baseline calculations and avoided emissions (savings)
- Daily, weekly, monthly longitudinal aggregations
- Modal split and breakdown analytics
- Verifiable calculation methodology metadata and educational disclaimers
"""

from datetime import date, datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator
from backend.app.core.utils import get_utc_now

from backend.app.models.mobility import TransportMode


class ImpactActivityType(str, Enum):
    """Categorization of environmental actions and commute records."""
    COMMUTE = "commute"
    CARPOOL = "carpool"
    ACTIVE_TRAVEL = "active_travel"
    PUBLIC_TRANSIT = "public_transit"
    EV_TRANSIT = "ev_transit"
    PURIFIER_OPTIMIZED = "purifier_optimized"
    VENTILATION_TIMED = "ventilation_timed"


class TimeframeFilter(str, Enum):
    """Time aggregation window for impact summaries."""
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    ALL_TIME = "all_time"


class ImpactLogCreate(BaseModel):
    """Request payload to record an environmental action or commute."""
    activity_type: ImpactActivityType = Field(..., description="Type of environmental activity")
    mode: Optional[TransportMode] = Field(None, description="Transport mode if activity is transit-related")
    distance_km: Optional[float] = Field(None, gt=0, le=150, description="Trip distance in kilometers (required for transit)")
    passengers: int = Field(default=1, ge=1, le=100, description="Actual passenger occupancy for vehicle allocation")
    baseline_mode: TransportMode = Field(default=TransportMode.PETROL_CAR, description="Baseline comparator mode (default solo petrol car)")
    activity_date: Optional[date] = Field(None, description="Date of activity (defaults to current UTC date)")
    notes: Optional[str] = Field(None, max_length=200, description="User note or commute description")
    exposure_avoided_score: Optional[float] = Field(0.0, ge=0.0, le=100.0, description="Qualitative particulate exposure mitigation score")

    @field_validator("distance_km")
    @classmethod
    def validate_distance_for_transit(cls, v: Optional[float], info) -> Optional[float]:
        activity_type = info.data.get("activity_type")
        transit_types = (
            ImpactActivityType.COMMUTE,
            ImpactActivityType.CARPOOL,
            ImpactActivityType.ACTIVE_TRAVEL,
            ImpactActivityType.PUBLIC_TRANSIT,
            ImpactActivityType.EV_TRANSIT,
        )
        if activity_type in transit_types and (v is None or v <= 0):
            raise ValueError("distance_km is required and must be > 0 for transit activities.")
        return v


class ImpactLogRecord(BaseModel):
    """Persisted environmental action record stored in Cloud Firestore or demonstration state."""
    log_id: str = Field(..., description="Unique record identifier")
    user_id: Optional[str] = Field(None, description="Firebase user UID if authenticated")
    activity_type: ImpactActivityType = Field(..., description="Activity category")
    mode: Optional[TransportMode] = Field(None, description="Commute mode if applicable")
    distance_km: float = Field(default=0.0, ge=0.0, description="Logged trip distance in km")
    passengers: int = Field(default=1, ge=1, le=500, description="Passenger occupancy used for allocation")
    vehicle_emissions_kg_co2e: float = Field(default=0.0, ge=0.0, description="Total vehicle-level emissions in kg CO2e")
    per_passenger_emissions_kg_co2e: float = Field(default=0.0, ge=0.0, description="Allocated individual emissions in kg CO2e")
    baseline_emissions_kg_co2e: float = Field(default=0.0, ge=0.0, description="Baseline comparator emissions for the same distance in kg CO2e")
    emission_saved_kg_co2e: float = Field(default=0.0, ge=0.0, description="Calculated CO2e avoided relative to baseline in kg CO2e")
    exposure_avoided_score: float = Field(default=0.0, ge=0.0, description="Qualitative health exposure mitigation score")
    activity_date: str = Field(..., description="Activity date string (YYYY-MM-DD)")
    notes: Optional[str] = Field(None, description="User notes")
    recorded_at: datetime = Field(default_factory=get_utc_now, description="Record creation timestamp")
    data_provenance: str = Field(default="modeled_estimate", description="Data source indicator: 'modeled_estimate' or 'simulated_demo'")
    methodology_notes: Optional[str] = Field(None, description="Transparent statement of calculation assumptions")


class DailyTrendItem(BaseModel):
    """Aggregated emissions and savings metrics for a single calendar day."""
    date_str: str = Field(..., description="Date (YYYY-MM-DD)")
    day_label: str = Field(..., description="Display label (e.g. 'Mon', 'Nov 19')")
    emissions_kg: float = Field(..., description="Total actual modeled emissions on this day in kg CO2e")
    savings_kg: float = Field(..., description="Total estimated avoided emissions on this day in kg CO2e")
    clean_distance_km: float = Field(..., description="Distance traveled via low-emission modes in km")
    activity_count: int = Field(..., description="Number of environmental actions logged on this day")


class ModeBreakdownItem(BaseModel):
    """Modal split summary showing travel distance, emissions, and share percentage."""
    mode: str = Field(..., description="TransportMode value")
    label_en: str = Field(..., description="English mode label")
    label_hi: str = Field(..., description="Hindi mode label")
    trip_count: int = Field(..., description="Total trips logged with this mode")
    distance_km: float = Field(..., description="Cumulative distance in km")
    emissions_kg: float = Field(..., description="Cumulative emissions in kg CO2e")
    savings_kg: float = Field(..., description="Cumulative avoided emissions in kg CO2e")
    distance_share_pct: float = Field(..., ge=0.0, le=100.0, description="Share of total logged distance (0 to 100%)")


class CalculationMethodologyDetail(BaseModel):
    """Transparent scientific disclosures and emission factors used in calculations."""
    grid_emission_factor_g_per_kwh: float = 716.0
    grid_factor_source: str = "Central Electricity Authority (CEA) v19 Baseline Database for Indian Power Sector (Dec 2023)"
    petrol_car_baseline_factor_g_per_km: float = 165.0
    baseline_source: str = "ARAI & BEE Automotive Standards (~14 km/L solo petrol car benchmark)"
    metro_factor_g_per_pax_km: float = 22.0
    metro_source: str = "DMRC Sustainability Report 2023-24 (30.7 Wh/passenger-km, passenger-allocated)"
    tree_monthly_absorption_kg: float = 1.75
    tree_source: str = "Educational reference based on US EPA GHG Equivalencies & urban forestry averages (~21 kg/tree/year). Indicative educational indicator; does not represent certified carbon offsets."
    indoor_action_disclaimer: str = "Purifier optimization and timed ventilation protect lung health by reducing particulate intake (PM2.5/PM10); they do not claim vehicular CO2 greenhouse gas reductions."


class SustainabilitySuggestion(BaseModel):
    """Contextual, actionable recommendation to reduce emissions or exposure."""
    id: str
    title_en: str
    title_hi: str
    description_en: str
    description_hi: str
    potential_monthly_savings_kg: float
    difficulty: str  # "easy", "moderate", "high"
    category: str    # "commute", "carpool", "indoor", "transit"


class ImpactSummaryResponse(BaseModel):
    """Comprehensive environmental impact aggregation for the selected timeframe."""
    timeframe: TimeframeFilter = Field(..., description="Aggregation timeframe")
    total_activities_logged: int = Field(..., description="Total activities in timeframe")
    total_distance_km: float = Field(..., description="Total transit distance logged in km")
    total_emissions_kg_co2e: float = Field(..., description="Total modeled actual emissions in kg CO2e")
    total_savings_kg_co2e: float = Field(..., description="Total modeled avoided emissions relative to baseline in kg CO2e")
    tree_months_equivalent: Optional[float] = Field(None, description="Optional educational equivalency: mature tree-months absorption")
    daily_trends: List[DailyTrendItem] = Field(default_factory=list, description="Chronological daily trend series")
    mode_breakdown: List[ModeBreakdownItem] = Field(default_factory=list, description="Modal split distribution")
    suggestions: List[SustainabilitySuggestion] = Field(default_factory=list, description="Personalized sustainability suggestions")
    methodology: CalculationMethodologyDetail = Field(default_factory=CalculationMethodologyDetail, description="Calculation assumptions and citations")
    is_demo_data: bool = Field(default=False, description="True if operating in demonstration/guest mode")


class PaginatedImpactLogs(BaseModel):
    """Paginated collection of environmental impact log records."""
    items: List[ImpactLogRecord] = Field(default_factory=list, description="Page of impact log records")
    total_count: int = Field(..., description="Total count of records matching filter criteria")
    limit: int = Field(..., description="Page size limit")
    offset: int = Field(..., description="Pagination offset")
    has_more: bool = Field(..., description="Whether additional records exist beyond current page")
