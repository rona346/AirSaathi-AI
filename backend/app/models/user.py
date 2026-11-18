"""User Profile and Cloud Firestore Persistence Data Models for AirSaathi AI.

Defines schemas for:
- Authenticated user identity (Firebase Auth token extraction)
- User Profile document (/users/{userId})
- Family preferences and vulnerability profiles
- Routine preferences and schedules
- Subcollections: routines, chat_sessions, saved_routes, indoor_devices, impact_logs
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from backend.app.models.routine import FamilyVulnerabilityInput, RoutinePreferencesInput
from backend.app.models.indoor import HouseholdInput
from backend.app.models.mobility import MobilityRequest


def default_mobility_request() -> MobilityRequest:
    return MobilityRequest(distance_km=12.0)


class AuthenticatedUser(BaseModel):
    uid: str = Field(..., description="Firebase User ID")
    email: Optional[str] = Field(None, description="User email address")
    display_name: Optional[str] = Field(None, description="User display name")
    email_verified: bool = Field(False, description="Whether email has been verified")
    claims: Dict[str, Any] = Field(default_factory=dict, description="Custom Firebase JWT claims")


class FamilyMemberProfile(BaseModel):
    name: str = Field(..., description="Family member name or identifier")
    age_group: str = Field("adult", description="Age group: infant, child, teen, adult, senior")
    vulnerabilities: List[str] = Field(default_factory=list, description="Specific conditions e.g. asthma, bronchitis, allergy")
    notes: Optional[str] = Field(None, description="Special instructions or precautions")


class FamilyPreferencesData(BaseModel):
    vulnerability: FamilyVulnerabilityInput = Field(default_factory=FamilyVulnerabilityInput)
    members: List[FamilyMemberProfile] = Field(default_factory=list, description="Detailed individual family member profiles")
    configured_precautions: List[str] = Field(default_factory=list, description="User-configured family precautions")


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
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class UserProfileUpdate(BaseModel):
    display_name: Optional[str] = None
    preferred_language: Optional[str] = None
    location: Optional[LocationPreferences] = None
    family: Optional[FamilyPreferencesData] = None
    routine: Optional[RoutinePreferencesData] = None
    household: Optional[HouseholdInput] = None
    mobility: Optional[MobilityRequest] = None


class PersistedRoutineRecord(BaseModel):
    routine_id: str = Field(..., description="Unique identifier of saved routine")
    station_id: str = Field(..., description="Station ID used when routine was generated")
    date_str: str = Field(..., description="Date of the routine (YYYY-MM-DD)")
    plan: Dict[str, Any] = Field(..., description="Complete RoutinePlan data")
    saved_at: datetime = Field(default_factory=datetime.utcnow)


class PersistedChatSession(BaseModel):
    session_id: str = Field(..., description="Unique session ID")
    title: str = Field("Environmental Consultation", description="Session title")
    messages: List[Dict[str, Any]] = Field(default_factory=list, description="Chat message history")
    station_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class PersistedSavedRoute(BaseModel):
    route_id: str = Field(..., description="Saved route ID")
    title: str = Field("Daily Commute", description="User label for route")
    origin: Optional[str] = None
    destination: Optional[str] = None
    distance_km: float
    current_mode: str
    recommended_option: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class PersistedIndoorDevice(BaseModel):
    device_id: str = Field(..., description="Device ID")
    device_name: str = Field(..., description="Device name e.g. Living Room Purifier")
    device_type: str = Field("air_purifier", description="air_purifier, monitor, exhaust")
    room: str = Field("living_room")
    filter_type: Optional[str] = Field("HEPA H13")
    filter_installed_date: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class PersistedImpactLog(BaseModel):
    log_id: str = Field(..., description="Impact log ID")
    activity_type: str = Field(..., description="clean_commute, purifier_optimized, ventilation_timed")
    emission_saved_kg_co2: float = 0.0
    exposure_avoided_score: float = 0.0
    notes: Optional[str] = None
    recorded_at: datetime = Field(default_factory=datetime.utcnow)
