"""Environmental Impact Tracker Endpoints for AirSaathi AI (Module 6).

Provides:
- GET /api/v1/impact/summary (Timeframe aggregation, daily trends, modal split, suggestions)
- GET /api/v1/impact/logs (Paginated impact action history)
- POST /api/v1/impact/logs (Log new environmental action; authenticated users only)
- DELETE /api/v1/impact/logs/{log_id} (Delete logged action; authenticated owner only)
- GET /api/v1/impact/methodology (Transparent scientific disclosures, emission factors, and citations)

Strict Architectural Rules:
- Enforces Firebase authentication and per-user ownership.
- Guest mode strictly isolates and returns simulated demonstration data.
- Input validation boundaries: distance_km > 0 for transit, 1-100 passengers, 1-100 pagination.
- Cross-user data isolation: Throws 403 Forbidden on mismatched target_user_id.
"""

from typing import Any, Dict, Optional
from fastapi import APIRouter, Body, Depends, HTTPException, Query, status

from backend.app.core.auth import (
    get_current_user,
    get_optional_user,
    verify_user_ownership,
)
from backend.app.models.impact import (
    CalculationMethodologyDetail,
    ImpactLogCreate,
    ImpactLogRecord,
    ImpactSummaryResponse,
    PaginatedImpactLogs,
    TimeframeFilter,
)
from backend.app.models.response import ApiResponse
from backend.app.models.user import AuthenticatedUser
from backend.app.services.firestore_service import FirestoreService
from backend.app.services.impact_service import ImpactService

router = APIRouter()


@router.get("/summary", response_model=ApiResponse[ImpactSummaryResponse])
def get_impact_summary(
    timeframe: TimeframeFilter = Query(
        TimeframeFilter.WEEK,
        description="Aggregation window: day, week, month, all_time",
    ),
    user_id: Optional[str] = Query(
        None,
        description="Optional target user ID to verify per-user authorization boundaries",
    ),
    current_user: Optional[AuthenticatedUser] = Depends(get_optional_user),
):
    """Retrieve aggregated environmental impact summary (emissions, savings, daily trends, modal split).

    Authenticated users query their persistent Cloud Firestore logs.
    Unauthenticated guest users receive isolated demonstration data.
    """
    if user_id is not None:
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required to query user-specific impact summary.",
            )
        verify_user_ownership(user_id, current_user)

    if current_user:
        records = ImpactService.get_user_records(user_id=current_user.uid, limit=200)
        summary = ImpactService.aggregate_summary(
            records=records,
            timeframe=timeframe,
            is_demo_data=False,
        )
        return ApiResponse(
            success=True,
            message=f"Impact summary for timeframe '{timeframe.value}' retrieved successfully",
            data=summary,
            is_demo_data=False,
        )

    # Guest demonstration mode: isolated in-memory dataset
    demo_records = ImpactService.get_demo_records()
    summary = ImpactService.aggregate_summary(
        records=demo_records,
        timeframe=timeframe,
        is_demo_data=True,
    )
    return ApiResponse(
        success=True,
        message=f"Impact summary for timeframe '{timeframe.value}' retrieved (demonstration data)",
        data=summary,
        is_demo_data=True,
    )


@router.get("/logs", response_model=ApiResponse[PaginatedImpactLogs])
def list_impact_logs(
    timeframe: Optional[TimeframeFilter] = Query(
        None,
        description="Optional timeframe filter: day, week, month, all_time",
    ),
    limit: int = Query(20, ge=1, le=100, description="Page size limit (1 to 100)"),
    offset: int = Query(0, ge=0, description="Pagination offset (>= 0)"),
    user_id: Optional[str] = Query(
        None,
        description="Optional target user ID to verify per-user authorization boundaries",
    ),
    current_user: Optional[AuthenticatedUser] = Depends(get_optional_user),
):
    """List paginated environmental activity logs.

    Authenticated users retrieve their persisted records.
    Guest users receive demonstration records.
    """
    if user_id is not None:
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required to query user-specific impact logs.",
            )
        verify_user_ownership(user_id, current_user)

    if current_user:
        records = ImpactService.get_user_records(user_id=current_user.uid, limit=200)
        if timeframe is not None:
            records = ImpactService.filter_records_by_timeframe(records, timeframe)

        total_count = len(records)
        paginated_items = records[offset : offset + limit]
        has_more = (offset + limit) < total_count

        return ApiResponse(
            success=True,
            message=f"Retrieved {len(paginated_items)} impact logs",
            data=PaginatedImpactLogs(
                items=paginated_items,
                total_count=total_count,
                limit=limit,
                offset=offset,
                has_more=has_more,
            ),
            is_demo_data=False,
        )

    # Guest demonstration mode
    records = ImpactService.get_demo_records()
    if timeframe is not None:
        records = ImpactService.filter_records_by_timeframe(records, timeframe)

    # Sort newest activity_date first
    records.sort(key=lambda r: (r.activity_date, r.recorded_at), reverse=True)
    total_count = len(records)
    paginated_items = records[offset : offset + limit]
    has_more = (offset + limit) < total_count

    return ApiResponse(
        success=True,
        message=f"Retrieved {len(paginated_items)} demo impact logs",
        data=PaginatedImpactLogs(
            items=paginated_items,
            total_count=total_count,
            limit=limit,
            offset=offset,
            has_more=has_more,
        ),
        is_demo_data=True,
    )


@router.post("/logs", response_model=ApiResponse[ImpactLogRecord], status_code=status.HTTP_201_CREATED)
def create_impact_log(
    payload: ImpactLogCreate = Body(..., description="Action log details"),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Record an environmental action or commute.

    Requires an authenticated Firebase user.
    Calculates emissions, baseline, and avoided emissions using verified benchmarks.
    Persists the record under /users/{uid}/impact_logs/{log_id}.
    """
    record = ImpactService.create_log_record(payload=payload, user_id=current_user.uid)
    FirestoreService.save_impact_log(user_id=current_user.uid, log=record)

    return ApiResponse(
        success=True,
        message="Environmental activity logged successfully",
        data=record,
        is_demo_data=False,
    )


@router.delete("/logs/{log_id}", response_model=ApiResponse[Dict[str, Any]])
def delete_impact_log(
    log_id: str,
    target_user_id: Optional[str] = Query(
        None,
        description="Optional target user ID to verify per-user authorization",
    ),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Delete an environmental activity log owned by the authenticated user.

    Enforces per-user ownership: throws 404 if log does not exist in user's subcollection,
    or 403 if target_user_id does not match the authenticated caller.
    """
    if target_user_id is not None:
        verify_user_ownership(target_user_id, current_user)

    existing_doc = FirestoreService.get_impact_log(user_id=current_user.uid, log_id=log_id)
    if not existing_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Impact log '{log_id}' not found.",
        )

    # Verify document ownership if stored with a user_id
    doc_user_id = existing_doc.get("user_id")
    if doc_user_id and doc_user_id != current_user.uid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: you do not have permission to delete another user's impact log.",
        )

    deleted = FirestoreService.delete_impact_log(user_id=current_user.uid, log_id=log_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete impact log from persistence store.",
        )

    return ApiResponse(
        success=True,
        message=f"Impact log '{log_id}' deleted successfully",
        data={"log_id": log_id, "deleted": True},
        is_demo_data=False,
    )


@router.get("/methodology", response_model=ApiResponse[CalculationMethodologyDetail])
def get_impact_methodology():
    """Retrieve transparent calculation methodology, benchmark emission factors, and citations."""
    methodology = ImpactService.get_methodology()
    return ApiResponse(
        success=True,
        message="Impact calculation methodology and benchmark citations",
        data=methodology,
        is_demo_data=False,
    )
