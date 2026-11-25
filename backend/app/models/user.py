"""User Profile and Cloud Firestore Persistence Data Models for AirSaathi AI.

Defines schemas for:
- Authenticated user identity (Firebase Auth token extraction)
- User Profile document (/users/{userId})
- Family preferences, demographics, and vulnerability profiles
- Household clean-air assets and environmental alert thresholds
- Routine preferences and schedules
- Subcollections: routines, chat_sessions, saved_routes, indoor_devices, impact_logs
- Personalized advisory responses
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from backend.app.core.utils import get_utc_now

from backend.app.models.routine import FamilyVulnerabilityInput, RoutinePreferencesInput
from backend.app.models.indoor import HouseholdInput
from backend.app.models.mobility import MobilityRequest


def default_mobility_request() -> MobilityRequest:
    return MobilityRequest(distance_km=12.0)


class AlertThresholdPreference(str, Enum):
    """AQI sensitivity threshold preference for personalized warnings."""
    SENSITIVE = "sensitive"          # Trigger cautionary guidance at AQI > 100 (Moderate)
    STANDARD = "standard"            # Trigger cautionary guidance at AQI > 200 (Poor)
    HIGH_TOLERANCE = "high_tolerance"  # Trigger cautionary guidance at AQI > 300 (Very Poor)


class HouseholdDemographics(BaseModel):
    """Broad household age-group demographics without personal data or medical records."""
    has_infants: bool = Field(False, description="Presence of infants (0-2 yrs)")
    has_children: bool = Field(False, description="Presence of children (3-11 yrs)")
    has_teens: bool = Field(False, description="Presence of adolescents (12-17 yrs)")
    has_adults: bool = Field(True, description="Presence of adults (18-59 yrs)")
    has_seniors: bool = Field(False, description="Presence of elderly family members (60+ yrs)")


class HouseholdCleanAirPreferences(BaseModel):
    """Household environmental, clean-air infrastructure, and daily activity window preferences."""
    alert_threshold: AlertThresholdPreference = Field(
        default=AlertThresholdPreference.STANDARD,
        description="AQI sensitivity threshold for personalized warnings"
    )
    preferred_transit_mode: str = Field(
        default="public_transit",
        description="Preferred sustainable commute mode: public_transit, metro, electric_bus, carpool, walking, cycling"
    )
    has_hepa_purifier: bool = Field(
        default=False,
        description="Presence of mechanical True HEPA air purifier in home"
    )
    has_kitchen_exhaust: bool = Field(
        default=True,
        description="Kitchen equipped with ducted chimney or exhaust fan"
    )
    has_indoor_monitor: bool = Field(
        default=False,
        description="Presence of indoor air quality monitor"
    )
    morning_outdoor_window: bool = Field(
        default=True,
        description="Household participates in morning outdoor activities/commute"
    )
    school_commute_active: bool = Field(
        default=False,
        description="Household has members actively commuting to school"
    )
    office_commute_active: bool = Field(
        default=True,
        description="Household has members actively commuting to work"
    )
    evening_outdoor_window: bool = Field(
        default=True,
        description="Household participates in evening outdoor recreation"
    )


class AuthenticatedUser(BaseModel):
    uid: str = Field(..., description="Firebase User ID")
    email: Optional[str] = Field(None, description="User email address")
    display_name: Optional[str] = Field(None, description="User display name")
    email_verified: bool = Field(False, description="Whether email has been verified")
    claims: Dict[str, Any] = Field(default_factory=dict, description="Custom Firebase JWT claims")


class FamilyMemberProfile(BaseModel):
    """Legacy individual family member profile preserved for full backward compatibility."""
    name: str = Field(..., description="Family member name or identifier")
    age_group: str = Field("adult", description="Age group: infant, child, teen, adult, senior")
    vulnerabilities: List[str] = Field(default_factory=list, description="Specific conditions e.g. asthma, bronchitis, allergy")
    notes: Optional[str] = Field(None, description="Special instructions or precautions")


class FamilyPreferencesData(BaseModel):
    """Consolidated family preferences maintaining 100% backward compatibility."""
    # Legacy fields
    vulnerability: FamilyVulnerabilityInput = Field(default_factory=FamilyVulnerabilityInput)
    members: List[FamilyMemberProfile] = Field(default_factory=list, description="Detailed individual family member profiles")
    configured_precautions: List[str] = Field(default_factory=list, description="User-configured family precautions")

    # Module 7 Household-level fields
    household_size: int = Field(default=2, ge=1, le=20, description="Total number of household members")
    demographics: HouseholdDemographics = Field(default_factory=HouseholdDemographics)
    preferences: HouseholdCleanAirPreferences = Field(default_factory=HouseholdCleanAirPreferences)


class FamilyPreferencesUpdate(BaseModel):
    """Partial update schema for family preferences using explicit optional fields."""
    vulnerability: Optional[FamilyVulnerabilityInput] = None
    members: Optional[List[FamilyMemberProfile]] = None
    configured_precautions: Optional[List[str]] = None
    household_size: Optional[int] = Field(None, ge=1, le=20)
    demographics: Optional[HouseholdDemographics] = None
    preferences: Optional[HouseholdCleanAirPreferences] = None


class RoutinePreferencesData(BaseModel):
    preferences: RoutinePreferencesInput = Field(default_factory=RoutinePreferencesInput)
    work_start_time: Optional[str] = Field("09:00", description="Typical office or commute start time")
    work_end_time: Optional[str] = Field("18:00", description="Typical office departure time")
    school_start_time: Optional[str] = Field("08:00", description="School arrival time")
    school_end_time: Optional[str] = Field("14:30", description="School dismissal time")
    indoor_alternatives_enabled: bool = Field(True, description="Preference for substituting outdoor activities on high smog days")


class LocationPreferences(BaseModel):
    default_station_id: str = Field("delhi-anand-vihar", description="Preferred monitoring station ID")
    default_city: str = Field("Delhi", description="Preferred city name")
    latitude: Optional[float] = Field(None, description="Home latitude coordinate")
    longitude: Optional[float] = Field(None, description="Home longitude coordinate")


class UserProfile(BaseModel):
    uid: str = Field(..., description="Unique Firebase User ID")
    email: Optional[str] = Field(None, description="User email address")
    display_name: Optional[str] = Field(None, description="User display name")
    preferred_language: str = Field("en", description="Preferred interface language ('en' or 'hi')")
    location: LocationPreferences = Field(default_factory=LocationPreferences)
    family: FamilyPreferencesData = Field(default_factory=FamilyPreferencesData)
    routine: RoutinePreferencesData = Field(default_factory=RoutinePreferencesData)
    household: Optional[HouseholdInput] = Field(default_factory=HouseholdInput)
    mobility: Optional[MobilityRequest] = Field(default_factory=default_mobility_request)
    created_at: datetime = Field(default_factory=get_utc_now)
    updated_at: datetime = Field(default_factory=get_utc_now)


class UserProfileUpdate(BaseModel):
    display_name: Optional[str] = None
    preferred_language: Optional[str] = None
    location: Optional[LocationPreferences] = None
    family: Optional[Union[FamilyPreferencesUpdate, FamilyPreferencesData]] = None
    routine: Optional[RoutinePreferencesData] = None
    household: Optional[HouseholdInput] = None
    mobility: Optional[MobilityRequest] = None


class PersistedRoutineRecord(BaseModel):
    routine_id: str = Field(..., description="Unique identifier of saved routine")
    station_id: str = Field(..., description="Station ID used when routine was generated")
    date_str: str = Field(..., description="Date of the routine (YYYY-MM-DD)")
    plan: Dict[str, Any] = Field(..., description="Complete RoutinePlan data")
    saved_at: datetime = Field(default_factory=get_utc_now)


class PersistedChatSession(BaseModel):
    session_id: str = Field(..., description="Unique session ID")
    title: str = Field("Environmental Consultation", description="Session title")
    messages: List[Dict[str, Any]] = Field(default_factory=list, description="Chat message history")
    station_id: Optional[str] = None
    created_at: datetime = Field(default_factory=get_utc_now)
    updated_at: datetime = Field(default_factory=get_utc_now)


class PersistedSavedRoute(BaseModel):
    route_id: str = Field(..., description="Saved route ID")
    title: str = Field("Daily Commute", description="User label for route")
    origin: Optional[str] = None
    destination: Optional[str] = None
    distance_km: float
    current_mode: str
    recommended_option: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=get_utc_now)


class PersistedIndoorDevice(BaseModel):
    device_id: str = Field(..., description="Device ID")
    device_name: str = Field(..., description="Device name e.g. Living Room Purifier")
    device_type: str = Field("air_purifier", description="air_purifier, monitor, exhaust")
    room: str = Field("living_room")
    filter_type: Optional[str] = Field("HEPA H13")
    filter_installed_date: Optional[str] = None
    created_at: datetime = Field(default_factory=get_utc_now)


class PersistedImpactLog(BaseModel):
    log_id: str = Field(..., description="Impact log ID")
    activity_type: str = Field(..., description="clean_commute, purifier_optimized, ventilation_timed")
    emission_saved_kg_co2: float = 0.0
    exposure_avoided_score: float = 0.0
    notes: Optional[str] = None
    recorded_at: datetime = Field(default_factory=get_utc_now)


class PersonalizedActionItem(BaseModel):
    category: str = Field(..., description="demographic, indoor_asset, commute, general")
    priority: str = Field(..., description="urgent, caution, advisory, good")
    title: str = Field(..., description="Short summary of recommended action")
    description: str = Field(..., description="Detailed actionable instruction")
    target_group: Optional[str] = Field(None, description="e.g. infants, children, seniors, all")
    rationale: str = Field(..., description="Scientific or exposure-reduction reason")


class PersonalizedAdvisoryResponse(BaseModel):
    status: str = Field("active", description="'active' if AQI telemetry is available, 'unavailable' if station data cannot be resolved")
    station_id: Optional[str] = None
    station_name: Optional[str] = None
    city: Optional[str] = None
    aqi: Optional[int] = None
    category: Optional[str] = None
    prominent_pollutant: Optional[str] = None
    data_source: str = "Unknown"
    is_demo_data: bool = False
    observed_at: Optional[datetime] = None
    threshold_applied: AlertThresholdPreference = AlertThresholdPreference.STANDARD
    household_size: int = 2
    actions: List[PersonalizedActionItem] = Field(default_factory=list)
    active_safeguards: List[str] = Field(default_factory=list)
    equipment_status: Dict[str, Any] = Field(default_factory=dict)
    disclaimer: str = Field(
        "AirSaathi provides atmospheric exposure-mitigation guidance based on ambient air quality. "
        "This is not medical diagnosis, clinical treatment, or a health guarantee."
    )
