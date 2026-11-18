from typing import Optional
from fastapi import APIRouter, Body, Query
from backend.app.models.response import ApiResponse
from backend.app.models.routine import (
    FamilyVulnerabilityInput,
    RoutinePlanRequest,
    RoutinePlanResponse,
    RoutinePreferencesInput,
)
from backend.app.services.routine_planner_service import RoutinePlannerService

router = APIRouter()


@router.post("/plan", response_model=ApiResponse[RoutinePlanResponse])
def create_routine_plan(
    request: RoutinePlanRequest = Body(...),
):
    """
    Generate an AI-driven, pollution-aware daily routine schedule based on:
    - Real-time or verified CPCB ambient AQI telemetry
    - Diurnal inversion & atmospheric mixing layer behavior
    - Family vulnerability factors (children, seniors, asthma, pregnancy)
    - Bilingual Hindi/English generation
    """
    plan = RoutinePlannerService.generate_routine_plan(request)
    return ApiResponse(
        success=True,
        message="Daily routine schedule generated successfully",
        data=plan,
        is_demo_data=plan.is_demo_data,
    )


@router.get("/plan", response_model=ApiResponse[RoutinePlanResponse])
def get_routine_plan_get(
    station_id: str = Query("delhi-anand-vihar", description="Identifier of the monitoring station"),
    language: str = Query("en", description="Output language ('en' or 'hi')"),
    has_children: bool = Query(False, description="Presence of children (<12 yrs)"),
    has_seniors: bool = Query(False, description="Presence of seniors (60+ yrs)"),
    has_respiratory: bool = Query(False, description="Presence of asthma or respiratory conditions"),
    is_pregnant: bool = Query(False, description="Presence of pregnant family member"),
    exercise_type: str = Query("walk", description="Preferred exercise: walk, run, gym, yoga, cycling"),
):
    """
    Convenience GET endpoint for fetching a personalized routine plan with URL query parameters.
    """
    family = FamilyVulnerabilityInput(
        has_children=has_children,
        has_seniors=has_seniors,
        has_respiratory_condition=has_respiratory,
        is_pregnant=is_pregnant,
    )
    prefs = RoutinePreferencesInput(
        preferred_exercise_type=exercise_type,
    )
    request = RoutinePlanRequest(
        station_id=station_id,
        language=language,
        family_profile=family,
        preferences=prefs,
    )
    plan = RoutinePlannerService.generate_routine_plan(request)
    return ApiResponse(
        success=True,
        message="Daily routine schedule retrieved successfully",
        data=plan,
        is_demo_data=plan.is_demo_data,
    )
