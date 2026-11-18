"""User Profile and Authenticated Resource Management Endpoints.

Provides:
- User profile & preferences management (/api/v1/user/me)
- Subcollection endpoints: routines, chat-sessions, routes, indoor-devices, impact-logs
- Cross-user ownership enforcement (403 on mismatched user ID)
- Service availability status (/api/v1/user/status)
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Body, Depends, HTTPException, Query, status

from backend.app.core.auth import get_current_user, verify_user_ownership
from backend.app.core.firebase import is_firebase_available
from backend.app.models.response import ApiResponse
from backend.app.models.user import (
    AuthenticatedUser,
    PersistedChatSession,
    PersistedImpactLog,
    PersistedIndoorDevice,
    PersistedRoutineRecord,
    PersistedSavedRoute,
    UserProfile,
    UserProfileUpdate,
)
from backend.app.services.firestore_service import FirestoreService

router = APIRouter()


@router.get("/status", response_model=ApiResponse[Dict[str, Any]])
def get_auth_service_status():
    """Check whether Firebase Admin and Cloud Firestore are active on this backend."""
    available = is_firebase_available()
    return ApiResponse(
        success=True,
        message="Firebase service status",
        data={
            "firebase_available": available,
            "mode": "authenticated_firestore" if available else "guest_demonstration",
            "persistence_active": available,
        },
        is_demo_data=not available,
    )


@router.get("/me", response_model=ApiResponse[UserProfile])
def get_current_user_profile(
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Retrieve the authenticated user's profile and preferences."""
    profile = FirestoreService.get_user_profile(current_user.uid)
    if profile is None:
        # Initialize default profile for first-time sign-in
        profile = FirestoreService.upsert_user_profile(
            user_id=current_user.uid,
            update=UserProfileUpdate(
                display_name=current_user.display_name,
            ),
            fallback_email=current_user.email,
            fallback_display_name=current_user.display_name,
        )

    return ApiResponse(
        success=True,
        message="User profile retrieved successfully",
        data=profile,
        is_demo_data=False,
    )


@router.put("/me", response_model=ApiResponse[UserProfile])
def update_current_user_profile(
    update: UserProfileUpdate = Body(...),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Update display name, location, family profile, routine preferences, or language."""
    profile = FirestoreService.upsert_user_profile(
        user_id=current_user.uid,
        update=update,
        fallback_email=current_user.email,
        fallback_display_name=current_user.display_name,
    )
    return ApiResponse(
        success=True,
        message="User profile and preferences updated successfully",
        data=profile,
        is_demo_data=False,
    )


@router.get("/me/routines", response_model=ApiResponse[List[Dict[str, Any]]])
def get_user_routines(
    limit: int = Query(15, ge=1, le=50),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Retrieve saved daily routines for the authenticated user."""
    routines = FirestoreService.list_routines(current_user.uid, limit=limit)
    return ApiResponse(
        success=True,
        message=f"Retrieved {len(routines)} saved routines",
        data=routines,
        is_demo_data=False,
    )


@router.post("/me/routines", response_model=ApiResponse[Dict[str, str]])
def save_user_routine(
    record: PersistedRoutineRecord = Body(...),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Save a generated daily routine under the authenticated user's ownership."""
    routine_id = FirestoreService.save_routine(current_user.uid, record)
    return ApiResponse(
        success=True,
        message="Daily routine saved to Cloud Firestore",
        data={"routine_id": routine_id},
        is_demo_data=False,
    )


@router.get("/me/chat-sessions", response_model=ApiResponse[List[Dict[str, Any]]])
def get_user_chat_sessions(
    limit: int = Query(20, ge=1, le=50),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Retrieve chat history sessions for the authenticated user."""
    sessions = FirestoreService.list_chat_sessions(current_user.uid, limit=limit)
    return ApiResponse(
        success=True,
        message=f"Retrieved {len(sessions)} chat sessions",
        data=sessions,
        is_demo_data=False,
    )


@router.post("/me/chat-sessions", response_model=ApiResponse[Dict[str, str]])
def save_user_chat_session(
    session: PersistedChatSession = Body(...),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Save or update a chat session for the authenticated user."""
    session_id = FirestoreService.save_chat_session(current_user.uid, session)
    return ApiResponse(
        success=True,
        message="Chat session persisted successfully",
        data={"session_id": session_id},
        is_demo_data=False,
    )


@router.get("/me/routes", response_model=ApiResponse[List[Dict[str, Any]]])
def get_user_routes(
    limit: int = Query(20, ge=1, le=50),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Retrieve saved sustainable mobility routes for the authenticated user."""
    routes = FirestoreService.list_routes(current_user.uid, limit=limit)
    return ApiResponse(
        success=True,
        message=f"Retrieved {len(routes)} saved routes",
        data=routes,
        is_demo_data=False,
    )


@router.post("/me/routes", response_model=ApiResponse[Dict[str, str]])
def save_user_route(
    route: PersistedSavedRoute = Body(...),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Save a sustainable commute route under the authenticated user's ownership."""
    route_id = FirestoreService.save_route(current_user.uid, route)
    return ApiResponse(
        success=True,
        message="Commute route persisted successfully",
        data={"route_id": route_id},
        is_demo_data=False,
    )


@router.get("/{target_user_id}/profile", response_model=ApiResponse[UserProfile])
def get_user_profile_by_id(
    target_user_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """
    Explicit user ID endpoint to enforce and test strict cross-user access boundaries.
    Throws HTTP 403 Forbidden if user A attempts to read user B's profile.
    """
    verify_user_ownership(target_user_id, current_user)
    profile = FirestoreService.get_user_profile(target_user_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found",
        )
    return ApiResponse(
        success=True,
        message="User profile retrieved",
        data=profile,
        is_demo_data=False,
    )
