"""API Endpoint Tests for Module 6: Environmental Impact Tracker.

Verifies:
1. GET /api/v1/impact/methodology (public scientific disclosure & citations)
2. GET /api/v1/impact/summary (guest isolation, authenticated Firestore aggregation, timeframe filters)
3. GET /api/v1/impact/logs (pagination limit/offset boundaries, demo fallback, authenticated logs)
4. POST /api/v1/impact/logs (transit calculation, indoor zero CO2 integrity, 401 on guest, input validation)
5. DELETE /api/v1/impact/logs/{log_id} (404 not found, successful deletion, per-user ownership)
6. Cross-user access enforcement (403 Forbidden on mismatched target_user_id or document owner)
7. FastAPI route registration in application routing table
"""

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from backend.app.api.v1.endpoints.impact import (
    create_impact_log,
    delete_impact_log,
    get_impact_methodology,
    get_impact_summary,
    list_impact_logs,
)
from backend.app.main import app
from backend.app.models.impact import (
    ImpactActivityType,
    ImpactLogCreate,
    ImpactLogRecord,
    TimeframeFilter,
)
from backend.app.models.mobility import TransportMode
from backend.app.models.user import AuthenticatedUser


@pytest.fixture
def auth_user_a():
    """Authenticated user fixture for primary caller."""
    return AuthenticatedUser(
        uid="usr_alpha_101",
        email="alpha@airsaathi.test",
        display_name="Alpha Commuter",
        email_verified=True,
    )


@pytest.fixture
def auth_user_b():
    """Secondary authenticated user fixture for cross-account testing."""
    return AuthenticatedUser(
        uid="usr_bravo_202",
        email="bravo@airsaathi.test",
        display_name="Bravo Commuter",
        email_verified=True,
    )


# 1. Methodology Endpoint
def test_get_methodology_endpoint():
    """Verify transparent scientific disclosures, factors, and citations."""
    res = get_impact_methodology()
    assert res.success is True
    assert res.is_demo_data is False
    assert res.data.grid_emission_factor_g_per_kwh == 716.0
    assert "CEA" in res.data.grid_factor_source
    assert res.data.petrol_car_baseline_factor_g_per_km == 165.0
    assert "ARAI" in res.data.baseline_source
    assert res.data.metro_factor_g_per_pax_km == 22.0
    assert "DMRC" in res.data.metro_source
    assert res.data.tree_monthly_absorption_kg == 1.75
    assert "Purifier optimization" in res.data.indoor_action_disclaimer


# 2. Summary - Guest Isolation
def test_guest_summary_returns_isolated_demo_data():
    """Verify unauthenticated guests receive demonstration data flagged is_demo_data=True."""
    res = get_impact_summary(
        timeframe=TimeframeFilter.WEEK,
        user_id=None,
        current_user=None,
    )
    assert res.success is True
    assert res.is_demo_data is True
    assert res.data.is_demo_data is True
    assert res.data.total_activities_logged > 0
    assert res.data.total_savings_kg_co2e > 0.0
    assert len(res.data.daily_trends) == 7
    assert len(res.data.mode_breakdown) > 0
    assert len(res.data.suggestions) >= 2


def test_guest_summary_unauthorized_user_query_raises_401():
    """Verify guest cannot request user-specific summary without an auth token."""
    with pytest.raises(HTTPException) as exc:
        get_impact_summary(
            timeframe=TimeframeFilter.WEEK,
            user_id="usr_alpha_101",
            current_user=None,
        )
    assert exc.value.status_code == 401
    assert "Authentication required" in exc.value.detail


# 3. Summary - Authenticated User
def test_authenticated_summary_aggregates_firestore_records(auth_user_a):
    """Verify authenticated user summary queries user's Firestore records."""
    mock_records = [
        {
            "log_id": "rec_01",
            "user_id": auth_user_a.uid,
            "activity_type": "public_transit",
            "mode": "metro",
            "distance_km": 15.0,
            "passengers": 1,
            "vehicle_emissions_kg_co2e": 0.33,
            "per_passenger_emissions_kg_co2e": 0.33,
            "baseline_emissions_kg_co2e": 2.475,
            "emission_saved_kg_co2e": 2.145,
            "exposure_avoided_score": 25.0,
            "activity_date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "recorded_at": datetime.now(timezone.utc),
            "data_provenance": "modeled_estimate",
        },
        {
            "log_id": "rec_02",
            "user_id": auth_user_a.uid,
            "activity_type": "active_travel",
            "mode": "walking",
            "distance_km": 3.0,
            "passengers": 1,
            "vehicle_emissions_kg_co2e": 0.0,
            "per_passenger_emissions_kg_co2e": 0.0,
            "baseline_emissions_kg_co2e": 0.495,
            "emission_saved_kg_co2e": 0.495,
            "exposure_avoided_score": 10.0,
            "activity_date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "recorded_at": datetime.now(timezone.utc),
            "data_provenance": "modeled_estimate",
        },
    ]

    with patch("backend.app.services.firestore_service.FirestoreService.list_impact_logs", return_value=mock_records):
        res = get_impact_summary(
            timeframe=TimeframeFilter.WEEK,
            user_id=None,
            current_user=auth_user_a,
        )
        assert res.success is True
        assert res.is_demo_data is False
        assert res.data.is_demo_data is False
        assert res.data.total_activities_logged == 2
        assert res.data.total_distance_km == 18.0
        assert res.data.total_emissions_kg_co2e == 0.33
        assert res.data.total_savings_kg_co2e == 2.64


# 4. Logs - Pagination & Guest Isolation
def test_guest_logs_pagination_and_boundaries():
    """Verify pagination limit, offset, and demo dataset isolation for guests."""
    res_page1 = list_impact_logs(
        timeframe=None,
        limit=2,
        offset=0,
        user_id=None,
        current_user=None,
    )
    assert res_page1.success is True
    assert res_page1.is_demo_data is True
    assert len(res_page1.data.items) == 2
    assert res_page1.data.total_count == 6
    assert res_page1.data.limit == 2
    assert res_page1.data.offset == 0
    assert res_page1.data.has_more is True

    # Page 2
    res_page2 = list_impact_logs(
        timeframe=None,
        limit=2,
        offset=2,
        user_id=None,
        current_user=None,
    )
    assert len(res_page2.data.items) == 2
    assert res_page2.data.offset == 2
    assert res_page2.data.has_more is True

    # Last Page
    res_last = list_impact_logs(
        timeframe=None,
        limit=2,
        offset=4,
        user_id=None,
        current_user=None,
    )
    assert len(res_last.data.items) == 2
    assert res_last.data.offset == 4
    assert res_last.data.has_more is False


def test_authenticated_logs_retrieves_user_records(auth_user_a):
    """Verify authenticated user logs endpoint queries user's Firestore data."""
    mock_records = [
        {
            "log_id": "rec_01",
            "user_id": auth_user_a.uid,
            "activity_type": "public_transit",
            "mode": "metro",
            "distance_km": 15.0,
            "passengers": 1,
            "vehicle_emissions_kg_co2e": 0.33,
            "per_passenger_emissions_kg_co2e": 0.33,
            "baseline_emissions_kg_co2e": 2.475,
            "emission_saved_kg_co2e": 2.145,
            "exposure_avoided_score": 25.0,
            "activity_date": "2026-11-19",
            "recorded_at": datetime.now(timezone.utc),
            "data_provenance": "modeled_estimate",
        }
    ]

    with patch("backend.app.services.firestore_service.FirestoreService.list_impact_logs", return_value=mock_records):
        res = list_impact_logs(
            timeframe=None,
            limit=20,
            offset=0,
            user_id=None,
            current_user=auth_user_a,
        )
        assert res.success is True
        assert res.is_demo_data is False
        assert len(res.data.items) == 1
        assert res.data.items[0].log_id == "rec_01"
        assert res.data.has_more is False


# 5. POST /logs - Validation & Calculations
def test_create_impact_log_transit_success(auth_user_a):
    """Verify transit logging calculates verified emissions and persists to Firestore."""
    payload = ImpactLogCreate(
        activity_type=ImpactActivityType.PUBLIC_TRANSIT,
        mode=TransportMode.METRO,
        distance_km=20.0,
        passengers=1,
        notes="Daily commute to Connaught Place",
    )

    with patch("backend.app.services.firestore_service.FirestoreService.save_impact_log") as mock_save:
        res = create_impact_log(payload=payload, current_user=auth_user_a)
        assert res.success is True
        assert res.is_demo_data is False
        assert res.data.user_id == auth_user_a.uid
        assert res.data.mode == TransportMode.METRO
        assert res.data.distance_km == 20.0
        # Metro: 20 * 22.0 / 1000 = 0.44 kg
        assert res.data.per_passenger_emissions_kg_co2e == 0.44
        # Baseline: 20 * 165.0 / 1000 = 3.30 kg
        assert res.data.baseline_emissions_kg_co2e == 3.30
        assert res.data.emission_saved_kg_co2e == 2.86
        assert res.data.data_provenance == "modeled_estimate"
        mock_save.assert_called_once()


def test_create_impact_log_indoor_safeguard_zero_emissions(auth_user_a):
    """Verify indoor actions strictly claim 0.0 kg CO2 emissions and 0.0 kg savings."""
    payload = ImpactLogCreate(
        activity_type=ImpactActivityType.PURIFIER_OPTIMIZED,
        notes="Bedroom purifier runtime scheduled for smog peak",
        exposure_avoided_score=40.0,
    )

    with patch("backend.app.services.firestore_service.FirestoreService.save_impact_log") as mock_save:
        res = create_impact_log(payload=payload, current_user=auth_user_a)
        assert res.success is True
        assert res.data.vehicle_emissions_kg_co2e == 0.0
        assert res.data.per_passenger_emissions_kg_co2e == 0.0
        assert res.data.baseline_emissions_kg_co2e == 0.0
        assert res.data.emission_saved_kg_co2e == 0.0
        assert res.data.exposure_avoided_score == 40.0
        assert "Indoor actions protect lung health" in res.data.methodology_notes
        mock_save.assert_called_once()


def test_create_impact_log_validation_boundaries():
    """Verify boundary rejections: distance required for transit, range constraints."""
    # Transit without distance must fail validation
    with pytest.raises(ValidationError):
        ImpactLogCreate(
            activity_type=ImpactActivityType.COMMUTE,
            mode=TransportMode.PETROL_CAR,
            distance_km=None,
        )

    # Negative distance must fail
    with pytest.raises(ValidationError):
        ImpactLogCreate(
            activity_type=ImpactActivityType.PUBLIC_TRANSIT,
            mode=TransportMode.METRO,
            distance_km=-5.0,
        )

    # Exorbitant distance (> 150 km) must fail
    with pytest.raises(ValidationError):
        ImpactLogCreate(
            activity_type=ImpactActivityType.PUBLIC_TRANSIT,
            mode=TransportMode.METRO,
            distance_km=250.0,
        )

    # Zero passengers must fail (ge=1)
    with pytest.raises(ValidationError):
        ImpactLogCreate(
            activity_type=ImpactActivityType.CARPOOL,
            mode=TransportMode.CARPOOL,
            distance_km=10.0,
            passengers=0,
        )


# 6. DELETE /logs/{log_id}
def test_delete_impact_log_success(auth_user_a):
    """Verify authenticated user can delete their owned log."""
    mock_log = {
        "log_id": "imp_to_delete",
        "user_id": auth_user_a.uid,
        "activity_type": "commute",
    }

    with patch("backend.app.services.firestore_service.FirestoreService.get_impact_log", return_value=mock_log):
        with patch("backend.app.services.firestore_service.FirestoreService.delete_impact_log", return_value=True):
            res = delete_impact_log(
                log_id="imp_to_delete",
                target_user_id=None,
                current_user=auth_user_a,
            )
            assert res.success is True
            assert res.data["log_id"] == "imp_to_delete"
            assert res.data["deleted"] is True


def test_delete_impact_log_not_found_raises_404(auth_user_a):
    """Verify deleting non-existent log raises 404 Not Found."""
    with patch("backend.app.services.firestore_service.FirestoreService.get_impact_log", return_value=None):
        with pytest.raises(HTTPException) as exc:
            delete_impact_log(
                log_id="nonexistent_log",
                target_user_id=None,
                current_user=auth_user_a,
            )
        assert exc.value.status_code == 404
        assert "not found" in exc.value.detail


# 7. Cross-User Access Enforcement (403 Forbidden)
def test_cross_user_access_blocked_summary(auth_user_a, auth_user_b):
    """Verify User A cannot query User B's summary."""
    with pytest.raises(HTTPException) as exc:
        get_impact_summary(
            timeframe=TimeframeFilter.WEEK,
            user_id=auth_user_b.uid,
            current_user=auth_user_a,
        )
    assert exc.value.status_code == 403
    assert "Access forbidden" in exc.value.detail


def test_cross_user_access_blocked_logs(auth_user_a, auth_user_b):
    """Verify User A cannot list User B's logs."""
    with pytest.raises(HTTPException) as exc:
        list_impact_logs(
            timeframe=None,
            user_id=auth_user_b.uid,
            current_user=auth_user_a,
        )
    assert exc.value.status_code == 403
    assert "Access forbidden" in exc.value.detail


def test_cross_user_access_blocked_delete(auth_user_a, auth_user_b):
    """Verify User A cannot delete with target_user_id of User B."""
    with pytest.raises(HTTPException) as exc:
        delete_impact_log(
            log_id="imp_secret_b",
            target_user_id=auth_user_b.uid,
            current_user=auth_user_a,
        )
    assert exc.value.status_code == 403
    assert "Access forbidden" in exc.value.detail


def test_cross_user_document_ownership_delete_blocked(auth_user_a, auth_user_b):
    """Verify that if a document has user_id of User B, User A cannot delete it."""
    mock_log = {
        "log_id": "imp_secret_b",
        "user_id": auth_user_b.uid,  # Owned by User B
        "activity_type": "commute",
    }

    with patch("backend.app.services.firestore_service.FirestoreService.get_impact_log", return_value=mock_log):
        with pytest.raises(HTTPException) as exc:
            delete_impact_log(
                log_id="imp_secret_b",
                target_user_id=None,
                current_user=auth_user_a,
            )
        assert exc.value.status_code == 403
        assert "Access forbidden" in exc.value.detail


# 8. Route Registration
def test_fastapi_app_impact_router_registered():
    """Verify that impact endpoints are properly mounted in the FastAPI app."""
    openapi_schema = app.openapi()
    paths = openapi_schema.get("paths", {})
    assert "/api/v1/impact/summary" in paths
    assert "/api/v1/impact/logs" in paths
    assert "/api/v1/impact/logs/{log_id}" in paths
    assert "/api/v1/impact/methodology" in paths
