from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

from backend.app.models.routine import FamilyVulnerabilityInput


class TransportMode(str, Enum):
    PETROL_CAR = "petrol_car"
    DIESEL_CAR = "diesel_car"
    TWO_WHEELER = "two_wheeler"
    ELECTRIC_CAR = "electric_car"
    ELECTRIC_TWO_WHEELER = "electric_two_wheeler"
    CNG_AUTO = "cng_auto"
    PUBLIC_BUS = "public_bus"
    ELECTRIC_BUS = "electric_bus"
    METRO = "metro"
    CARPOOL = "carpool"
    WALKING = "walking"
    CYCLING = "cycling"


class CommutePurpose(str, Enum):
    OFFICE = "office"
    SCHOOL_COLLEGE = "school_college"
    ERRANDS = "errands"
    HEALTHCARE = "healthcare"
    LEISURE = "leisure"


class CommuteFrequency(str, Enum):
    DAILY_ROUND_TRIP = "daily_round_trip"
    ONE_WAY = "one_way"
    WEEKDAYS_ONLY = "weekdays_only"
    OCCASIONAL = "occasional"


class AccessibilityNeed(str, Enum):
    NONE = "none"
    WHEELCHAIR = "wheelchair"
    LOW_WALKING = "low_walking"
    SENIOR_FRIENDLY = "senior_friendly"
    CHILD_FRIENDLY = "child_friendly"


class ModeEmissionDetail(BaseModel):
    mode: TransportMode
    label: str
    direct_emissions_g: float = Field(..., description="Tailpipe exhaust emissions in grams CO2e per trip")
    grid_indirect_emissions_g: float = Field(..., description="Upstream power-grid generation emissions in grams CO2e per trip")
    total_emissions_g: float = Field(..., description="Total direct + indirect modeled emissions per trip")
    per_passenger_emissions_g: float = Field(..., description="Emissions allocated per passenger based on occupancy")
    co2e_savings_vs_baseline_g: float = Field(..., description="CO2e savings compared to solo private petrol car")
    co2e_savings_pct: float = Field(..., description="Percentage savings relative to baseline (0 to 100%)")
    suitability_score: str = Field(..., description="Optimal, Recommended, Moderate, or Restricted Today")
    aqi_safety_verdict: str = Field(..., description="AQI-aware exposure assessment (e.g. Enclosed Cabin Safe, High Respiratory Hazard)")
    exposure_level: str = Field(..., description="Low, Moderate, High, or Severe outdoor smog inhalation risk")
    precautions: List[str] = Field(default_factory=list, description="Specific precautions (e.g. AC recirculation, N95 mask)")


class CarpoolEstimate(BaseModel):
    solo_trip_emissions_g: float = Field(..., description="Emissions if driving solo")
    shared_2_person_emissions_g: float = Field(..., description="Per-person emissions with 2 occupants (50% reduction)")
    shared_3_person_emissions_g: float = Field(..., description="Per-person emissions with 3 occupants (67% reduction)")
    shared_4_person_emissions_g: float = Field(..., description="Per-person emissions with 4 occupants (75% reduction)")
    daily_savings_kg: float = Field(..., description="Daily CO2e avoided for round trip by carpooling with 3 persons")
    annual_savings_kg: float = Field(..., description="Annual CO2e avoided (based on 250 work days)")


class MobilityRequest(BaseModel):
    station_id: str = Field("delhi-anand-vihar", description="Target CPCB monitoring station ID")
    language: str = Field("en", description="'en' for English or 'hi' for Hindi")
    distance_km: float = Field(..., gt=0, le=150, description="One-way commute distance in kilometers")
    starting_area: Optional[str] = Field(None, max_length=100, description="Origin area or locality")
    destination_area: Optional[str] = Field(None, max_length=100, description="Destination area or transit node")
    current_mode: TransportMode = Field(TransportMode.PETROL_CAR, description="Current primary commute mode")
    frequency: CommuteFrequency = Field(CommuteFrequency.DAILY_ROUND_TRIP, description="Travel frequency")
    purpose: CommutePurpose = Field(CommutePurpose.OFFICE, description="Commute purpose")
    accessibility: AccessibilityNeed = Field(AccessibilityNeed.NONE, description="Accessibility constraint")
    occupancy: int = Field(default=1, ge=1, le=6, description="Average passengers in current vehicle")
    family_profile: Optional[FamilyVulnerabilityInput] = None


class MobilityPlanResponse(BaseModel):
    station_id: str
    station_name: str
    city: str
    aqi: int
    category: str
    prominent_pollutant: str
    is_demo_data: bool
    data_source: str
    observed_at: datetime
    language: str
    distance_km: float
    frequency: str
    current_mode: TransportMode
    current_trip_emissions_g: float
    current_daily_emissions_g: float
    mode_comparisons: List[ModeEmissionDetail]
    recommended_mode: TransportMode
    recommended_mode_label: str
    recommended_mode_reason: str
    active_mobility_advisory: str
    carpool_potential: CarpoolEstimate
    ai_recommendation: str
    ai_provider: str
    ai_generated: bool
    methodology_notes: List[str]
    disclaimer: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)
