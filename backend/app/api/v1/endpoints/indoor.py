from typing import Optional
from fastapi import APIRouter, Body, Query
from backend.app.core.utils import resolve_query_param
from backend.app.models.indoor import (
    CleaningMethod,
    CookingFuel,
    HouseholdInput,
    IndoorAssessmentRequest,
    IndoorAssessmentResponse,
    RoomType,
    VentilationStatus,
)
from backend.app.models.response import ApiResponse
from backend.app.services.indoor_service import IndoorAirService

router = APIRouter()


@router.post("/assess", response_model=ApiResponse[IndoorAssessmentResponse])
def assess_indoor_air(
    request: IndoorAssessmentRequest = Body(...),
):
    """
    Perform a qualitative indoor air quality assessment based on:
    - Ambient outdoor CPCB telemetry & infiltration
    - Household emission sources (cooking, tadka, smoking, incense)
    - Ventilation patterns and CADR purifier sizing
    - Room-specific mitigation protocols (bedroom, kitchen, living, children's, study)
    """
    assessment = IndoorAirService.evaluate_indoor_air(request)
    return ApiResponse(
        success=True,
        message="Indoor air quality assessment generated successfully",
        data=assessment,
        is_demo_data=assessment.outdoor_is_demo,
    )


@router.get("/assess", response_model=ApiResponse[IndoorAssessmentResponse])
def assess_indoor_air_get(
    station_id: str = Query("delhi-anand-vihar", description="Identifier of ambient CPCB station"),
    language: str = Query("en", description="Output language ('en' or 'hi')"),
    room_type: str = Query("living_room", description="Selected room type"),
    room_area_sqft: float = Query(150.0, description="Room area in square feet"),
    heavy_frying: bool = Query(True, description="Frequent Indian tadka or deep frying"),
    has_chimney: bool = Query(True, description="Has kitchen chimney"),
    has_exhaust: bool = Query(True, description="Has kitchen exhaust fan"),
    burns_incense: bool = Query(True, description="Burns agarbatti, dhoop, or mosquito coils"),
    indoor_smoking: bool = Query(False, description="Indoor smoking present"),
    has_purifier: bool = Query(False, description="Has air purifier"),
    purifier_has_hepa: bool = Query(True, description="Purifier has true HEPA filter"),
):
    """
    Convenience GET endpoint for qualitative indoor air evaluation with URL query parameters.
    """
    res_station_id = str(resolve_query_param(station_id, "delhi-anand-vihar"))
    res_lang = str(resolve_query_param(language, "en"))
    res_room = str(resolve_query_param(room_type, "living_room"))
    res_area = float(resolve_query_param(room_area_sqft, 150.0))
    res_frying = bool(resolve_query_param(heavy_frying, True))
    res_chimney = bool(resolve_query_param(has_chimney, True))
    res_exhaust = bool(resolve_query_param(has_exhaust, True))
    res_incense = bool(resolve_query_param(burns_incense, True))
    res_smoking = bool(resolve_query_param(indoor_smoking, False))
    res_purifier = bool(resolve_query_param(has_purifier, False))
    res_hepa = bool(resolve_query_param(purifier_has_hepa, True))

    # Match room_type enum safely
    valid_rooms = {r.value: r for r in RoomType}
    selected_room = valid_rooms.get(res_room, RoomType.LIVING_ROOM)

    household = HouseholdInput(
        room_type=selected_room,
        room_area_sqft=res_area,
        heavy_frying_or_tadka=res_frying,
        has_kitchen_chimney=res_chimney,
        has_kitchen_exhaust=res_exhaust,
        burns_agarbatti_or_dhoop=res_incense,
        indoor_smoking=res_smoking,
        has_air_purifier=res_purifier,
        purifier_has_hepa=res_hepa,
    )

    request = IndoorAssessmentRequest(
        station_id=res_station_id,
        language=res_lang,
        household=household,
    )

    assessment = IndoorAirService.evaluate_indoor_air(request)
    return ApiResponse(
        success=True,
        message="Indoor air quality assessment retrieved successfully",
        data=assessment,
        is_demo_data=assessment.outdoor_is_demo,
    )
