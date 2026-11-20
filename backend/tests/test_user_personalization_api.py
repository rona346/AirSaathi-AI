"""API Endpoint and Cloud Firestore Integration Tests for Module 7.

Tests coverage:
1. Authenticated profile retrieval with Module 7 fields (/api/v1/user/me).
2. Authenticated partial household preference updates.
3. Explicit empty-list handling where applicable.
4. Preservation of legacy vulnerability and unrelated profile fields.
5. Unauthenticated request rejection (HTTP 401).
6. User-specific profile isolation and cross-user rejection (HTTP 403).
7. Personalized advisory with valid live AQI data (/api/v1/user/me/personalized-advisory).
8. Personalized advisory with demo/fallback AQI data.
9. Missing or unavailable AQI behavior (status="unavailable").
10. Correct provenance and observation timestamp.
11. No fabricated measurements.
12. Station resolution from user profile location vs query param override.
13. Existing profile and subcollection endpoint regression.
14. FastAPI OpenAPI route registration check.
"""

from contextlib import contextmanager
from datetime import datetime
from unittest.mock import MagicMock, patch
import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from backend.app.api.v1.endpoints.user import (
    get_auth_service_status,
    get_current_user_profile,
    get_personalized_advisory,
    get_user_chat_sessions,
    get_user_profile_by_id,
    get_user_routes,
    get_user_routines,
    save_user_chat_session,
    save_user_route,
    save_user_routine,
    update_current_user_profile,
)
from backend.app.core.auth import get_current_user, verify_user_ownership
from backend.app.core.firebase import reset_firebase, set_mock_firebase
from backend.app.main import app
from backend.app.models.aqi import (
    AqiCategory,
    CurrentAqiResponse,
    HealthAdvisory,
    PollutantDetail,
    StationInfo,
)
from backend.app.models.indoor import HouseholdInput
from backend.app.models.mobility import MobilityRequest
from backend.app.models.routine import FamilyVulnerabilityInput
from backend.app.models.user import (
    AlertThresholdPreference,
    AuthenticatedUser,
    FamilyMemberProfile,
    FamilyPreferencesData,
    FamilyPreferencesUpdate,
    HouseholdCleanAirPreferences,
    HouseholdDemographics,
    LocationPreferences,
    PersistedChatSession,
    PersistedRoutineRecord,
    PersistedSavedRoute,
    RoutinePreferencesData,
    UserProfile,
    UserProfileUpdate,
)


# ---------------------------------------------------------------------------
# In-Memory Firestore Mock Setup
# ---------------------------------------------------------------------------

class InMemoryFirestoreMock:
    """In-memory Firestore client mock for authenticated API integration tests."""

    def __init__(self):
        self.users = {}

    def collection(self, col_name: str):
        assert col_name == "users"
        return MockUsersCollectionRef(self)


class MockUsersCollectionRef:
    def __init__(self, db: InMemoryFirestoreMock):
        self.db = db

    def document(self, doc_id: str):
        return MockUserDocumentRef(self.db, doc_id)


class MockUserDocumentRef:
    def __init__(self, db: InMemoryFirestoreMock, user_id: str):
        self.db = db
        self.user_id = user_id
        if user_id not in self.db.users:
            self.db.users[user_id] = {"data": None, "subcollections": {}}

    def get(self):
        user_record = self.db.users.get(self.user_id)
        exists = user_record is not None and user_record["data"] is not None
        mock_snap = MagicMock()
        mock_snap.exists = exists
        mock_snap.to_dict.return_value = user_record["data"] if exists else None
        return mock_snap

    def set(self, data, merge=False):
        user_entry = self.db.users[self.user_id]
        if merge and user_entry["data"]:
            user_entry["data"].update(data)
        else:
            user_entry["data"] = dict(data)

    def collection(self, sub_name: str):
        return MockSubcollectionRef(self.db, self.user_id, sub_name)


class MockSubcollectionRef:
    def __init__(self, db: InMemoryFirestoreMock, user_id: str, sub_name: str):
        self.db = db
        self.user_id = user_id
        self.sub_name = sub_name
        subs = self.db.users[user_id]["subcollections"]
        if sub_name not in subs:
            subs[sub_name] = {}

    def document(self, doc_id: str):
        return MockSubDocumentRef(self.db, self.user_id, self.sub_name, doc_id)

    def limit(self, num: int):
        return self

    def stream(self):
        docs_dict = self.db.users[self.user_id]["subcollections"].get(self.sub_name, {})
        result = []
        for doc_id, doc_data in docs_dict.items():
            m = MagicMock()
            m.id = doc_id
            m.to_dict.return_value = doc_data
            result.append(m)
        return result


class MockSubDocumentRef:
    def __init__(self, db: InMemoryFirestoreMock, user_id: str, sub_name: str, doc_id: str):
        self.db = db
        self.user_id = user_id
        self.sub_name = sub_name
        self.doc_id = doc_id

    def set(self, data, merge=False):
        subs = self.db.users[self.user_id]["subcollections"]
        if self.sub_name not in subs:
            subs[self.sub_name] = {}
        if merge and self.doc_id in subs[self.sub_name]:
            subs[self.sub_name][self.doc_id].update(data)
        else:
            subs[self.sub_name][self.doc_id] = dict(data)


# ---------------------------------------------------------------------------
# Test Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def setup_test_environment():
    """Reset Firebase state and connect in-memory mock Firestore for each test."""
    reset_firebase()
    mock_db = InMemoryFirestoreMock()
    set_mock_firebase(app_mock=MagicMock(), firestore_mock=mock_db)
    yield mock_db
    reset_firebase()


@pytest.fixture
def auth_user_a():
    """Primary authenticated user fixture."""
    return AuthenticatedUser(
        uid="usr_alpha_123",
        email="alpha@airsaathi.test",
        display_name="Alpha User",
        email_verified=True,
    )


@pytest.fixture
def auth_user_b():
    """Secondary authenticated user fixture for cross-user isolation tests."""
    return AuthenticatedUser(
        uid="usr_bravo_456",
        email="bravo@airsaathi.test",
        display_name="Bravo User",
        email_verified=True,
    )


def make_mock_aqi_reading(
    station_id="delhi-anand-vihar",
    station_name="Anand Vihar",
    city="Delhi",
    aqi=265,
    category=AqiCategory.POOR,
    is_demo=False,
    data_source="data.gov.in (Official CPCB)",
    observed_at=None,
):
    """Helper to generate verified CurrentAqiResponse objects."""
    if observed_at is None:
        observed_at = datetime(2026, 11, 20, 10, 30, 0)
    return CurrentAqiResponse(
        station=StationInfo(
            id=station_id,
            name=station_name,
            city=city,
            state="Delhi",
            latitude=28.6508,
            longitude=77.3152,
            is_hotspot=True,
        ),
        aqi=aqi,
        category=category,
        prominent_pollutant="PM2.5",
        pollutants={
            "PM2.5": PollutantDetail(
                name="PM2.5",
                value=115.0,
                unit="µg/m³",
                sub_index=aqi,
                category=category,
                standard_limit=60.0,
                who_limit=15.0,
            ),
        },
        health_advisory=HealthAdvisory(
            general_advice="Poor air quality advisory",
            children_and_seniors="Limit outdoor exposure",
            patients_with_respiratory_issues="Stay indoors",
            outdoor_activity="Avoid vigorous workouts",
            mask_recommendation="Wear N95 mask outdoors",
            purifier_recommendation="Run HEPA filtration indoors",
            ventilation_window="Keep windows closed",
        ),
        weather={},
        last_updated=observed_at,
        data_source=data_source,
        is_demo_data=is_demo,
    )


@contextmanager
def patch_active_aqi_provider(mock_provider):
    """Context manager to ensure both endpoint and personalization service see mock provider."""
    with patch("backend.app.api.v1.endpoints.user.get_active_aqi_provider", return_value=mock_provider), \
         patch("backend.app.services.personalization_service.get_active_aqi_provider", return_value=mock_provider):
        yield mock_provider


# ---------------------------------------------------------------------------
# Test Cases
# ---------------------------------------------------------------------------

def test_authenticated_profile_retrieval_with_module7_fields(auth_user_a):
    """1. Verify GET /api/v1/user/me returns newly added household_size, demographics, and preferences."""
    resp = get_current_user_profile(current_user=auth_user_a)
    assert resp.success is True
    assert resp.is_demo_data is False
    profile = resp.data

    assert profile.uid == "usr_alpha_123"
    family = profile.family

    # Module 7 household-level fields
    assert family.household_size == 2
    assert family.demographics.has_infants is False
    assert family.demographics.has_children is False
    assert family.demographics.has_teens is False
    assert family.demographics.has_adults is True
    assert family.demographics.has_seniors is False

    assert family.preferences.alert_threshold == AlertThresholdPreference.STANDARD
    assert family.preferences.preferred_transit_mode == "public_transit"
    assert family.preferences.has_hepa_purifier is False
    assert family.preferences.has_kitchen_exhaust is True

    # Legacy backward compatibility fields
    assert family.vulnerability.has_children is False
    assert family.vulnerability.has_seniors is False
    assert family.members == []
    assert family.configured_precautions == []


def test_authenticated_partial_household_preference_updates(auth_user_a):
    """2. Verify PUT /api/v1/user/me updates household fields and preserves unspecified ones."""
    update_payload = UserProfileUpdate(
        family=FamilyPreferencesUpdate(
            household_size=4,
            demographics=HouseholdDemographics(
                has_seniors=True,
                has_children=True,
            ),
            preferences=HouseholdCleanAirPreferences(
                alert_threshold=AlertThresholdPreference.SENSITIVE,
                has_hepa_purifier=True,
            ),
        )
    )
    resp = update_current_user_profile(update=update_payload, current_user=auth_user_a)
    assert resp.success is True
    family = resp.data.family

    assert family.household_size == 4
    assert family.demographics.has_seniors is True
    assert family.demographics.has_children is True
    # Default unmentioned demographic preserved
    assert family.demographics.has_adults is True

    assert family.preferences.alert_threshold == AlertThresholdPreference.SENSITIVE
    assert family.preferences.has_hepa_purifier is True
    # Default unmentioned preference preserved
    assert family.preferences.has_kitchen_exhaust is True

    # Bidirectional sync to legacy vulnerability
    assert family.vulnerability.has_seniors is True
    assert family.vulnerability.has_children is True


def test_explicit_empty_list_handling(auth_user_a):
    """3. Verify explicit empty lists correctly clear arrays, while omitted fields are preserved."""
    # Step 1: Add a member and precaution
    populate_payload = UserProfileUpdate(
        family=FamilyPreferencesUpdate(
            members=[
                FamilyMemberProfile(name="Aarav", age_group="child", vulnerabilities=["asthma"])
            ],
            configured_precautions=["wear_n95_in_traffic"],
        )
    )
    resp1 = update_current_user_profile(update=populate_payload, current_user=auth_user_a)
    assert resp1.success is True
    assert len(resp1.data.family.members) == 1
    assert len(resp1.data.family.configured_precautions) == 1

    # Step 2: Explicitly pass empty lists to clear them
    clear_payload = UserProfileUpdate(
        family=FamilyPreferencesUpdate(
            members=[],
            configured_precautions=[],
        )
    )
    resp2 = update_current_user_profile(update=clear_payload, current_user=auth_user_a)
    assert resp2.success is True
    assert resp2.data.family.members == []
    assert resp2.data.family.configured_precautions == []

    # Step 3: Omitted members field in subsequent update must not restore or corrupt
    subsequent_payload = UserProfileUpdate(
        family=FamilyPreferencesUpdate(
            household_size=3,
        )
    )
    resp3 = update_current_user_profile(update=subsequent_payload, current_user=auth_user_a)
    assert resp3.success is True
    assert resp3.data.family.household_size == 3
    assert resp3.data.family.members == []
    assert resp3.data.family.configured_precautions == []


def test_preservation_of_legacy_vulnerability_and_unrelated_profile_fields(auth_user_a):
    """4. Verify updating Module 7 fields leaves routine, location, mobility, and medical flags intact."""
    # Step 1: Seed profile with custom routine, location, mobility, and legacy medical vulnerability
    seed_payload = UserProfileUpdate(
        location=LocationPreferences(
            default_station_id="bengaluru-btm-layout",
            default_city="Bengaluru",
        ),
        routine=RoutinePreferencesData(
            work_start_time="10:30",
            work_end_time="19:00",
        ),
        mobility=MobilityRequest(
            distance_km=25.5,
        ),
        family=FamilyPreferencesUpdate(
            vulnerability=FamilyVulnerabilityInput(
                has_respiratory_condition=True,
                is_pregnant=True,
            )
        ),
    )
    resp1 = update_current_user_profile(update=seed_payload, current_user=auth_user_a)
    assert resp1.success is True

    # Step 2: Perform partial update containing only Module 7 fields
    m7_payload = UserProfileUpdate(
        family=FamilyPreferencesUpdate(
            household_size=5,
            preferences=HouseholdCleanAirPreferences(
                has_indoor_monitor=True,
            ),
        )
    )
    resp2 = update_current_user_profile(update=m7_payload, current_user=auth_user_a)
    assert resp2.success is True
    data = resp2.data

    # Module 7 fields updated
    assert data.family.household_size == 5
    assert data.family.preferences.has_indoor_monitor is True

    # Legacy vulnerability preserved
    assert data.family.vulnerability.has_respiratory_condition is True
    assert data.family.vulnerability.is_pregnant is True

    # Unrelated profile objects preserved
    assert data.location.default_city == "Bengaluru"
    assert data.location.default_station_id == "bengaluru-btm-layout"
    assert data.routine.work_start_time == "10:30"
    assert data.mobility.distance_km == 25.5


def test_unauthenticated_request_rejection_401():
    """5. Verify unauthenticated, empty-token, and expired-token requests receive HTTP 401."""
    # Missing credentials
    with pytest.raises(HTTPException) as exc1:
        get_current_user(None)
    assert exc1.value.status_code == 401
    assert "missing or empty Bearer token" in exc1.value.detail

    # Empty Bearer token
    with pytest.raises(HTTPException) as exc2:
        get_current_user(HTTPAuthorizationCredentials(scheme="Bearer", credentials="   "))
    assert exc2.value.status_code == 401

    # Expired token
    with patch("backend.app.core.auth.verify_id_token", side_effect=ValueError("Token has expired")):
        with pytest.raises(HTTPException) as exc3:
            get_current_user(HTTPAuthorizationCredentials(scheme="Bearer", credentials="expired.token"))
        assert exc3.value.status_code == 401
        assert "Invalid or expired" in exc3.value.detail

    # Malformed token
    with patch("backend.app.core.auth.verify_id_token", side_effect=ValueError("Malformed JWT")):
        with pytest.raises(HTTPException) as exc4:
            get_current_user(HTTPAuthorizationCredentials(scheme="Bearer", credentials="bad.token"))
        assert exc4.value.status_code == 401


def test_user_specific_profile_isolation(auth_user_a, auth_user_b):
    """6. Verify user isolation: User A's data is never exposed to User B and cross-user paths yield 403."""
    # User A sets household size 5 in Delhi
    update_current_user_profile(
        update=UserProfileUpdate(
            family=FamilyPreferencesUpdate(household_size=5),
            location=LocationPreferences(default_city="Delhi"),
        ),
        current_user=auth_user_a,
    )

    # User B sets household size 1 in Mumbai
    update_current_user_profile(
        update=UserProfileUpdate(
            family=FamilyPreferencesUpdate(household_size=1),
            location=LocationPreferences(default_city="Mumbai"),
        ),
        current_user=auth_user_b,
    )

    # User A gets own profile
    resp_a = get_current_user_profile(current_user=auth_user_a)
    assert resp_a.data.uid == "usr_alpha_123"
    assert resp_a.data.family.household_size == 5
    assert resp_a.data.location.default_city == "Delhi"

    # User B gets own profile
    resp_b = get_current_user_profile(current_user=auth_user_b)
    assert resp_b.data.uid == "usr_bravo_456"
    assert resp_b.data.family.household_size == 1
    assert resp_b.data.location.default_city == "Mumbai"

    # User A attempts cross-user access to User B
    with pytest.raises(HTTPException) as exc_a:
        get_user_profile_by_id(target_user_id=auth_user_b.uid, current_user=auth_user_a)
    assert exc_a.value.status_code == 403
    assert "Access forbidden" in exc_a.value.detail

    # User B attempts cross-user access to User A
    with pytest.raises(HTTPException) as exc_b:
        get_user_profile_by_id(target_user_id=auth_user_a.uid, current_user=auth_user_b)
    assert exc_b.value.status_code == 403


def test_personalized_advisory_with_valid_live_aqi_data(auth_user_a):
    """7. Verify GET /api/v1/user/me/personalized-advisory returns structured recommendations with live AQI data."""
    # Set household profile with infant, senior, and HEPA purifier
    update_current_user_profile(
        update=UserProfileUpdate(
            family=FamilyPreferencesUpdate(
                household_size=4,
                demographics=HouseholdDemographics(has_infants=True, has_seniors=True),
                preferences=HouseholdCleanAirPreferences(
                    has_hepa_purifier=True,
                    alert_threshold=AlertThresholdPreference.STANDARD,
                ),
            )
        ),
        current_user=auth_user_a,
    )

    mock_live_aqi = make_mock_aqi_reading(
        station_id="delhi-anand-vihar",
        aqi=265,
        category=AqiCategory.POOR,
        is_demo=False,
        data_source="data.gov.in (Official CPCB)",
    )

    mock_provider = MagicMock()
    mock_provider.get_current_aqi.return_value = mock_live_aqi

    with patch_active_aqi_provider(mock_provider):
        resp = get_personalized_advisory(station_id=None, current_user=auth_user_a)
        assert resp.success is True
        assert resp.is_demo_data is False
        assert resp.message == "Personalized household advisory generated successfully"

        advisory = resp.data
        assert advisory.status == "active"
        assert advisory.is_demo_data is False
        assert advisory.data_source == "data.gov.in (Official CPCB)"
        assert advisory.station_id == "delhi-anand-vihar"
        assert advisory.aqi == 265
        assert advisory.category == "Poor"
        assert advisory.threshold_applied == AlertThresholdPreference.STANDARD
        assert advisory.household_size == 4

        # Safeguards & equipment
        assert "Infant Respiratory Shield" in advisory.active_safeguards
        assert "Senior Cardiovascular Safeguard" in advisory.active_safeguards
        assert "HEPA Indoor Filtration" in advisory.active_safeguards
        assert advisory.equipment_status["has_hepa_purifier"] is True

        # Non-medical disclaimer
        assert "AirSaathi provides atmospheric exposure-mitigation guidance" in advisory.disclaimer
        assert "not medical diagnosis" in advisory.disclaimer

        # Action titles verify demographic customization
        action_titles = [a.title for a in advisory.actions]
        assert "Infant Respiratory Shield" in action_titles
        assert "Senior Outdoor Activity Exposure Caution" in action_titles
        assert "Prioritize HEPA Air Filtration Indoors" in action_titles


def test_personalized_advisory_with_demo_fallback_aqi_data(auth_user_a):
    """8. Verify that demo/fallback AQI data transparently propagates is_demo_data=True."""
    mock_demo_aqi = make_mock_aqi_reading(
        station_id="delhi-anand-vihar",
        aqi=368,
        category=AqiCategory.VERY_POOR,
        is_demo=True,
        data_source="Calibrated CPCB Baseline",
    )

    mock_provider = MagicMock()
    mock_provider.get_current_aqi.return_value = mock_demo_aqi

    with patch_active_aqi_provider(mock_provider):
        resp = get_personalized_advisory(station_id=None, current_user=auth_user_a)
        assert resp.is_demo_data is True
        assert resp.data.is_demo_data is True
        assert resp.data.data_source == "Calibrated CPCB Baseline"
        assert resp.data.status == "active"
        assert resp.data.aqi == 368


def test_missing_or_unavailable_aqi_behavior(auth_user_a):
    """9. Verify explicit status="unavailable" without crashing when telemetry is unavailable."""
    mock_provider = MagicMock()
    mock_provider.get_current_aqi.side_effect = RuntimeError("CPCB station network timeout")

    with patch_active_aqi_provider(mock_provider):
        resp = get_personalized_advisory(
            station_id="nonexistent-station",
            current_user=auth_user_a,
        )
        assert resp.success is True
        assert resp.message == "Ambient air quality telemetry unavailable"
        advisory = resp.data

        assert advisory.status == "unavailable"
        assert advisory.aqi is None
        assert advisory.category is None
        assert advisory.prominent_pollutant is None
        assert advisory.observed_at is None
        assert advisory.data_source == "Unavailable"
        assert advisory.is_demo_data is False

        # Action explains telemetry unavailability
        assert len(advisory.actions) == 1
        assert advisory.actions[0].title == "Air Quality Telemetry Unavailable"
        assert "not medical diagnosis" in advisory.disclaimer


def test_correct_provenance_and_observation_timestamp(auth_user_a):
    """10. Verify exact station metadata and observation timestamps are preserved without drift."""
    fixed_time = datetime(2026, 11, 20, 8, 45, 0)
    mock_reading = make_mock_aqi_reading(
        station_id="noida-sector-62",
        station_name="Sector 62, Noida",
        city="Noida",
        aqi=210,
        category=AqiCategory.POOR,
        is_demo=False,
        data_source="data.gov.in (Official CPCB)",
        observed_at=fixed_time,
    )

    mock_provider = MagicMock()
    mock_provider.get_current_aqi.return_value = mock_reading

    with patch_active_aqi_provider(mock_provider):
        resp = get_personalized_advisory(
            station_id="noida-sector-62",
            current_user=auth_user_a,
        )
        advisory = resp.data

        assert advisory.station_id == "noida-sector-62"
        assert advisory.station_name == "Sector 62, Noida"
        assert advisory.city == "Noida"
        assert advisory.data_source == "data.gov.in (Official CPCB)"
        assert advisory.observed_at == fixed_time


def test_no_fabricated_measurements(auth_user_a):
    """11. Verify that when telemetry is invalid or missing, no artificial AQI values are invented."""
    mock_provider = MagicMock()
    # Telemetry unavailable / missing
    mock_provider.get_current_aqi.return_value = None

    with patch_active_aqi_provider(mock_provider):
        resp = get_personalized_advisory(current_user=auth_user_a)
        advisory = resp.data

        # Crucial zero-fabrication assertions
        assert advisory.status == "unavailable"
        assert advisory.aqi is None
        assert advisory.category is None
        assert advisory.prominent_pollutant is None
        assert advisory.observed_at is None
        assert advisory.data_source == "Unavailable"
        assert advisory.is_demo_data is False


def test_station_resolution_from_profile_location_and_override(auth_user_a):
    """12. Verify user configured station is used by default, and query param station_id overrides it."""
    # Configure user with default station in Bengaluru
    update_current_user_profile(
        update=UserProfileUpdate(
            location=LocationPreferences(
                default_station_id="bengaluru-btm-layout",
                default_city="Bengaluru",
            )
        ),
        current_user=auth_user_a,
    )

    captured_stations = []

    def mock_get_current_aqi(station_id: str):
        captured_stations.append(station_id)
        return make_mock_aqi_reading(station_id=station_id, aqi=88, category=AqiCategory.SATISFACTORY)

    mock_provider = MagicMock()
    mock_provider.get_current_aqi.side_effect = mock_get_current_aqi

    with patch_active_aqi_provider(mock_provider):
        # Call 1: Without query parameter -> should resolve to profile default ("bengaluru-btm-layout")
        resp1 = get_personalized_advisory(station_id=None, current_user=auth_user_a)
        assert resp1.success is True
        assert captured_stations[-1] == "bengaluru-btm-layout"

        # Call 2: With explicit query parameter override -> should use override ("delhi-punjabi-bagh")
        resp2 = get_personalized_advisory(
            station_id="delhi-punjabi-bagh",
            current_user=auth_user_a,
        )
        assert resp2.success is True
        assert captured_stations[-1] == "delhi-punjabi-bagh"


def test_existing_profile_and_subcollection_endpoints_regression(auth_user_a):
    """13. Verify existing status and subcollection endpoints (routines, chats, routes) function without regressions."""
    # 1. Status endpoint
    status_resp = get_auth_service_status()
    assert status_resp.success is True
    assert status_resp.data["firebase_available"] is True

    # 2. Routines subcollection
    routine_payload = PersistedRoutineRecord(
        routine_id="rt_test_101",
        station_id="delhi-anand-vihar",
        date_str="2026-11-20",
        plan={"summary": "Optimal morning routine"},
    )
    save_rt = save_user_routine(record=routine_payload, current_user=auth_user_a)
    assert save_rt.success is True
    assert save_rt.data["routine_id"] == "rt_test_101"

    list_rt = get_user_routines(limit=15, current_user=auth_user_a)
    assert list_rt.success is True
    assert len(list_rt.data) == 1

    # 3. Chat sessions subcollection
    chat_payload = PersistedChatSession(
        session_id="chat_test_202",
        title="Air Quality Chat",
        messages=[{"role": "user", "text": "Is it safe outside?"}],
    )
    save_chat = save_user_chat_session(session=chat_payload, current_user=auth_user_a)
    assert save_chat.success is True
    assert save_chat.data["session_id"] == "chat_test_202"

    list_chat = get_user_chat_sessions(limit=20, current_user=auth_user_a)
    assert list_chat.success is True
    assert len(list_chat.data) == 1

    # 4. Saved routes subcollection
    route_payload = PersistedSavedRoute(
        route_id="rt_route_303",
        title="Office Commute",
        distance_km=12.0,
        current_mode="car",
    )
    save_route = save_user_route(route=route_payload, current_user=auth_user_a)
    assert save_route.success is True
    assert save_route.data["route_id"] == "rt_route_303"

    list_routes = get_user_routes(limit=20, current_user=auth_user_a)
    assert list_routes.success is True
    assert len(list_routes.data) == 1


def test_fastapi_user_router_registered():
    """14. Verify OpenAPI routing table mounts Module 7 and existing user endpoints."""
    openapi_schema = app.openapi()
    paths = openapi_schema.get("paths", {})

    assert "/api/v1/user/status" in paths
    assert "/api/v1/user/me" in paths
    assert "/api/v1/user/me/personalized-advisory" in paths
    assert "/api/v1/user/me/routines" in paths
    assert "/api/v1/user/me/chat-sessions" in paths
    assert "/api/v1/user/me/routes" in paths
    assert "/api/v1/user/{target_user_id}/profile" in paths

    # Verify HTTP method mapping
    assert "get" in paths["/api/v1/user/me/personalized-advisory"]
    assert "get" in paths["/api/v1/user/me"]
    assert "put" in paths["/api/v1/user/me"]
