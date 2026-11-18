from typing import Optional
from fastapi import APIRouter, Body, HTTPException, Query
from backend.app.models.mobility import (
    AccessibilityNeed,
    CommuteFrequency,
    CommutePurpose,
    MobilityPlanResponse,
    MobilityRequest,
    TransportMode,
)
from backend.app.models.response import ApiResponse
from backend.app.services.mobility_service import MobilityService

router = APIRouter()


@router.post("/plan", response_model=ApiResponse[MobilityPlanResponse])
def plan_sustainable_commute(
    request: MobilityRequest = Body(...),
):
    """Generates an AQI-aware sustainable mobility recommendation plan, comparing 12 transport modes,

    calculating per-passenger CO2e emissions and carpooling potential, and factoring in ambient smog risks.
    """
    if request.distance_km <= 0 or request.distance_km > 150:
        raise HTTPException(
            status_code=400,
            detail="Commute distance must be between 0.1 and 150 km.",
        )

    plan = MobilityService.generate_mobility_plan(request)

    return ApiResponse(
        success=True,
        message="Sustainable mobility plan generated successfully",
        data=plan,
        is_demo_data=plan.is_demo_data,
    )


@router.get("/plan", response_model=ApiResponse[MobilityPlanResponse])
def plan_sustainable_commute_get(
    distance_km: float = Query(..., gt=0, le=150, description="Commute distance in kilometers"),
    station_id: str = Query("delhi-anand-vihar", description="Target CPCB station ID"),
    language: str = Query("en", description="Output language: 'en' or 'hi'"),
    current_mode: str = Query("petrol_car", description="Current travel mode"),
    frequency: str = Query("daily_round_trip", description="Commute frequency"),
    purpose: str = Query("office", description="Commute purpose"),
    accessibility: str = Query("none", description="Accessibility requirement"),
    occupancy: int = Query(1, ge=1, le=6, description="Vehicle occupancy"),
):
    """GET endpoint for sustainable commute planning with query parameters."""
    def _resolve(val, default):
        if hasattr(val, "default"):
            return val.default
        return val if val is not None else default

    res_distance = float(_resolve(distance_km, 10.0))
    res_station_id = str(_resolve(station_id, "delhi-anand-vihar"))
    res_language = str(_resolve(language, "en"))
    res_mode = str(_resolve(current_mode, "petrol_car"))
    res_frequency = str(_resolve(frequency, "daily_round_trip"))
    res_purpose = str(_resolve(purpose, "office"))
    res_accessibility = str(_resolve(accessibility, "none"))
    res_occupancy = int(_resolve(occupancy, 1))

    try:
        mode_enum = TransportMode(res_mode)
    except ValueError:
        mode_enum = TransportMode.PETROL_CAR

    try:
        freq_enum = CommuteFrequency(res_frequency)
    except ValueError:
        freq_enum = CommuteFrequency.DAILY_ROUND_TRIP

    try:
        purpose_enum = CommutePurpose(res_purpose)
    except ValueError:
        purpose_enum = CommutePurpose.OFFICE

    try:
        acc_enum = AccessibilityNeed(res_accessibility)
    except ValueError:
        acc_enum = AccessibilityNeed.NONE

    req = MobilityRequest(
        station_id=res_station_id,
        language=res_language,
        distance_km=res_distance,
        current_mode=mode_enum,
        frequency=freq_enum,
        purpose=purpose_enum,
        accessibility=acc_enum,
        occupancy=res_occupancy,
    )

    plan = MobilityService.generate_mobility_plan(req)

    return ApiResponse(
        success=True,
        message="Sustainable mobility plan generated successfully",
        data=plan,
        is_demo_data=plan.is_demo_data,
    )
