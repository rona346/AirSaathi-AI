from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class RoomType(str, Enum):
    BEDROOM = "bedroom"
    KITCHEN = "kitchen"
    LIVING_ROOM = "living_room"
    CHILDRENS_ROOM = "childrens_room"
    STUDY_ROOM = "study_room"


class CookingFuel(str, Enum):
    LPG = "lpg"
    INDUCTION = "induction"
    PNG = "png"
    TRADITIONAL_BIOMASS = "traditional_biomass"


class CleaningMethod(str, Enum):
    WET_MOPPING = "wet_mopping"
    DRY_BROOM = "dry_broom"
    VACUUM_CLEANER = "vacuum_cleaner"


class VentilationStatus(str, Enum):
    MOSTLY_CLOSED = "mostly_closed"
    REGULAR_CROSS_VENT = "regular_cross_vent"
    CONTINUOUS_OPEN = "continuous_open"


class QualitativeRiskLevel(str, Enum):
    LOW = "Low"
    MODERATE = "Moderate"
    HIGH = "High"
    SEVERE = "Severe"


class HouseholdInput(BaseModel):
    room_type: RoomType = Field(RoomType.LIVING_ROOM, description="Selected room type")
    room_area_sqft: float = Field(150.0, ge=30.0, le=2000.0, description="Estimated room area in square feet")
    ceiling_height_ft: float = Field(10.0, ge=7.0, le=20.0, description="Ceiling height in feet")
    cooking_fuel: CookingFuel = Field(CookingFuel.LPG, description="Primary cooking fuel used in household")
    heavy_frying_or_tadka: bool = Field(True, description="Frequent Indian tempering (tadka), deep frying or spice roasting")
    has_kitchen_chimney: bool = Field(True, description="Presence of ducted electric chimney")
    has_kitchen_exhaust: bool = Field(True, description="Presence of exhaust fan in kitchen")
    ventilation_status: VentilationStatus = Field(VentilationStatus.MOSTLY_CLOSED, description="Typical window aeration status")
    cleaning_method: CleaningMethod = Field(CleaningMethod.WET_MOPPING, description="Dusting and sweeping approach")
    burns_agarbatti_or_dhoop: bool = Field(True, description="Daily burning of incense sticks, dhoop, or mosquito coils indoors")
    has_pets: bool = Field(False, description="Presence of shedding cats or dogs")
    indoor_smoking: bool = Field(False, description="Presence of indoor cigarette or bidi smoking")
    has_air_purifier: bool = Field(False, description="Presence of an air purifier in this room")
    purifier_has_hepa: bool = Field(True, description="Whether purifier contains true HEPA H13/H14 filter")


class VentilationAdvice(BaseModel):
    action: str = Field(..., description="Open, Restrict, or Seal windows")
    optimal_window: str = Field(..., description="Recommended hours for aeration, e.g. 01:00 PM - 03:00 PM")
    duration_minutes: int = Field(..., description="Recommended duration in minutes")
    rationale: str = Field(..., description="Atmospheric and diurnal inversion justification")
    precautions: List[str] = Field(default_factory=list)


class CadrRecommendation(BaseModel):
    room_area_sqft: float
    recommended_min_cadr_m3h: int = Field(..., description="Recommended CADR in m³/h (Clean Air Delivery Rate)")
    recommended_min_cadr_cfm: int = Field(..., description="Recommended CADR in CFM (Cubic Feet per Minute)")
    target_ach: float = Field(4.5, description="Target Air Changes per Hour for smog conditions")
    filter_type_guidance: str = Field(..., description="True HEPA (H13) vs ionizers/plasma warning")
    placement_tips: List[str] = Field(default_factory=list)
    maintenance_schedule: str = Field(..., description="Cleaning and replacement frequency")


class KitchenGuidance(BaseModel):
    risk_summary: str = Field(..., description="Indoor PM2.5 and gas emissions from Indian cooking")
    chimney_exhaust_guidance: str = Field(..., description="Protocol for pre-running and post-running exhaust")
    cooking_habits_advice: List[str] = Field(default_factory=list)
    combustion_safety: str = Field(..., description="LPG blue flame, CO ventilation and pan lids")


class RoomSpecificRecommendation(BaseModel):
    room_name: str
    primary_threats: List[str]
    immediate_actions: List[str]
    night_protocol: Optional[str] = None
    lifestyle_adjustments: List[str]


class IndoorAssessmentRequest(BaseModel):
    station_id: str = Field("delhi-anand-vihar", description="Outdoor CPCB station ID for ambient context")
    language: str = Field("en", description="'en' for English or 'hi' for Hindi")
    household: HouseholdInput = Field(default_factory=HouseholdInput)


class IndoorAssessmentResponse(BaseModel):
    # Context & Data Provenance
    station_id: str
    station_name: str
    city: str
    outdoor_aqi: int
    outdoor_category: str
    outdoor_is_demo: bool
    outdoor_data_source: str
    outdoor_observed_at: datetime
    language: str
    ai_provider: str = Field(..., description="'google-gemini' or 'expert-rules-fallback'")
    ai_generated: bool
    
    # Qualitative Indoor Assessment (Strictly no fabricated indoor AQI numbers)
    has_connected_indoor_sensor: bool = False
    qualitative_risk: QualitativeRiskLevel
    risk_score_numeric: int = Field(..., ge=0, le=100, description="Qualitative composite risk index (0-100)")
    risk_summary: str = Field(..., description="Plain-language explanation of primary indoor threats")
    sensor_notice: str = Field(..., description="Clear disclosure that actual indoor AQI is not fabricated")
    
    # Feature Modules
    ventilation: VentilationAdvice
    purifier_guidance: CadrRecommendation
    kitchen_guidance: KitchenGuidance
    room_recommendations: Dict[str, RoomSpecificRecommendation]
    actionable_checklist: List[str]
    plant_myth_clarification: str = Field(..., description="Scientific fact check regarding indoor plants vs HEPA")
    
    # Safety Disclaimer
    disclaimer: str
    generated_at: datetime
