"""Unit tests for Cloud Firestore Persistence Service.

Verifies:
1. User profile creation and retrieval under /users/{userId}.
2. Family preference and member vulnerability updates.
3. Routine schedule preference updates.
4. Routine subcollection persistence (/users/{userId}/routines/{routineId}).
5. Chat session subcollection persistence (/users/{userId}/chat_sessions/{sessionId}).
6. Saved route subcollection persistence (/users/{userId}/saved_routes/{routeId}).
7. Indoor devices & impact logs persistence.
8. Graceful offline fallback when Firestore is unavailable.
9. Account switching data isolation.
"""

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
import pytest

from backend.app.core.firebase import reset_firebase, set_mock_firebase
from backend.app.models.routine import FamilyVulnerabilityInput, RoutinePreferencesInput
from backend.app.models.user import (
    FamilyMemberProfile,
    FamilyPreferencesData,
    LocationPreferences,
    PersistedChatSession,
    PersistedImpactLog,
    PersistedIndoorDevice,
    PersistedRoutineRecord,
    PersistedSavedRoute,
    RoutinePreferencesData,
    UserProfile,
    UserProfileUpdate,
)
from backend.app.services.firestore_service import FirestoreService


class InMemoryFirestoreMock:
    """Lightweight in-memory Firestore database mock for unit testing."""

    def __init__(self):
        # Structure: {"users": {user_id: {"data": {...}, "subcollections": {subname: {doc_id: {...}}}}}}
        self.users = {}

    def collection(self, col_name):
        assert col_name == "users"
        return MockUsersCollectionRef(self)


class MockUsersCollectionRef:
    def __init__(self, db: InMemoryFirestoreMock):
        self.db = db

    def document(self, doc_id):
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

    def collection(self, sub_name):
        return MockSubcollectionRef(self.db, self.user_id, sub_name)


class MockSubcollectionRef:
    def __init__(self, db: InMemoryFirestoreMock, user_id: str, sub_name: str):
        self.db = db
        self.user_id = user_id
        self.sub_name = sub_name
        subs = self.db.users[user_id]["subcollections"]
        if sub_name not in subs:
            subs[sub_name] = {}

    def document(self, doc_id):
        return MockSubDocumentRef(self.db, self.user_id, self.sub_name, doc_id)

    def limit(self, num):
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
        subs = self.db.users[self.user_id]["subcollections"][self.sub_name]
        if merge and self.doc_id in subs:
            subs[self.doc_id].update(data)
        else:
            subs[self.doc_id] = dict(data)


@pytest.fixture
def mock_db():
    db = InMemoryFirestoreMock()
    set_mock_firebase(app_mock=MagicMock(), firestore_mock=db)
    yield db
    reset_firebase()


def test_profile_creation_and_retrieval(mock_db):
    """Verify fresh user profile creation and subsequent retrieval."""
    user_id = "test_user_001"
    update = UserProfileUpdate(
        display_name="Aarav Sharma",
        preferred_language="hi",
        location=LocationPreferences(default_station_id="delhi-punjabi-bagh", default_city="Delhi"),
    )

    created_profile = FirestoreService.upsert_user_profile(
        user_id=user_id,
        update=update,
        fallback_email="aarav@example.com",
    )

    assert created_profile.uid == user_id
    assert created_profile.display_name == "Aarav Sharma"
    assert created_profile.email == "aarav@example.com"
    assert created_profile.preferred_language == "hi"
    assert created_profile.location.default_station_id == "delhi-punjabi-bagh"

    # Fetch back from Firestore
    fetched = FirestoreService.get_user_profile(user_id)
    assert fetched is not None
    assert fetched.uid == user_id
    assert fetched.display_name == "Aarav Sharma"


def test_family_preferences_persistence(mock_db):
    """Verify persisting and updating family members and vulnerabilities."""
    user_id = "test_user_family"

    family_data = FamilyPreferencesData(
        vulnerability=FamilyVulnerabilityInput(
            has_children=True,
            has_seniors=True,
            has_respiratory_condition=True,
            is_pregnant=False,
        ),
        members=[
            FamilyMemberProfile(name="Grandfather", age_group="senior", vulnerabilities=["Asthma"]),
            FamilyMemberProfile(name="Aanya", age_group="child", vulnerabilities=["Dust Allergy"]),
        ],
        configured_precautions=["Run air purifiers 24/7 in bedroom", "Wear N95 on commute"],
    )

    update = UserProfileUpdate(family=family_data)
    profile = FirestoreService.upsert_user_profile(user_id=user_id, update=update)

    assert profile.family.vulnerability.has_seniors is True
    assert profile.family.vulnerability.has_respiratory_condition is True
    assert len(profile.family.members) == 2
    assert profile.family.members[0].name == "Grandfather"
    assert "Run air purifiers 24/7 in bedroom" in profile.family.configured_precautions


def test_routine_preferences_persistence(mock_db):
    """Verify routine timings and preference persistence."""
    user_id = "test_user_routine"

    routine_data = RoutinePreferencesData(
        preferences=RoutinePreferencesInput(
            wakes_up_early=True,
            commutes_to_office=True,
            school_going_kids=True,
            exercises_daily=True,
            preferred_exercise_type="yoga",
        ),
        work_start_time="08:30",
        work_end_time="17:30",
        school_start_time="07:45",
        indoor_alternatives_enabled=True,
    )

    update = UserProfileUpdate(routine=routine_data)
    profile = FirestoreService.upsert_user_profile(user_id=user_id, update=update)

    assert profile.routine.preferences.preferred_exercise_type == "yoga"
    assert profile.routine.work_start_time == "08:30"
    assert profile.routine.school_start_time == "07:45"


def test_routine_subcollection_persistence(mock_db):
    """Verify saving and listing generated daily routines in subcollection."""
    user_id = "user_routines_sub"

    record1 = PersistedRoutineRecord(
        routine_id="rt_20261118_01",
        station_id="delhi-anand-vihar",
        date_str="2026-11-18",
        plan={"morning": "Stay indoors", "aqi": 368},
    )
    record2 = PersistedRoutineRecord(
        routine_id="rt_20261119_02",
        station_id="delhi-anand-vihar",
        date_str="2026-11-19",
        plan={"morning": "Brief walk at noon", "aqi": 210},
    )

    id1 = FirestoreService.save_routine(user_id, record1)
    id2 = FirestoreService.save_routine(user_id, record2)
    assert id1 == "rt_20261118_01"
    assert id2 == "rt_20261119_02"

    saved_list = FirestoreService.list_routines(user_id)
    assert len(saved_list) == 2
    ids = [r["routine_id"] for r in saved_list]
    assert "rt_20261118_01" in ids
    assert "rt_20261119_02" in ids


def test_chat_session_subcollection_persistence(mock_db):
    """Verify persisting conversation sessions in subcollection."""
    user_id = "user_chat_sub"

    session = PersistedChatSession(
        session_id="chat_sess_99",
        title="Smog advisory consultation",
        messages=[
            {"role": "user", "text": "Is it safe to run today?"},
            {"role": "assistant", "text": "No, PM2.5 levels are severe."},
        ],
        station_id="delhi-anand-vihar",
    )

    sess_id = FirestoreService.save_chat_session(user_id, session)
    assert sess_id == "chat_sess_99"

    sessions = FirestoreService.list_chat_sessions(user_id)
    assert len(sessions) == 1
    assert sessions[0]["session_id"] == "chat_sess_99"
    assert len(sessions[0]["messages"]) == 2


def test_saved_routes_subcollection_persistence(mock_db):
    """Verify saving sustainable mobility routes in subcollection."""
    user_id = "user_routes_sub"

    route = PersistedSavedRoute(
        route_id="route_home_office",
        title="Home to Nehru Place",
        origin="Lajpat Nagar",
        destination="Nehru Place",
        distance_km=6.5,
        current_mode="petrol_car",
        recommended_option={"mode": "electric_bus", "emission_saved_kg": 0.95},
    )

    r_id = FirestoreService.save_route(user_id, route)
    assert r_id == "route_home_office"

    routes = FirestoreService.list_routes(user_id)
    assert len(routes) == 1
    assert routes[0]["title"] == "Home to Nehru Place"
    assert routes[0]["distance_km"] == 6.5


def test_indoor_device_and_impact_log_persistence(mock_db):
    """Verify indoor device and environmental impact log persistence."""
    user_id = "user_device_impact"

    device = PersistedIndoorDevice(
        device_id="purifier_bedroom_01",
        device_name="Master Bedroom HEPA",
        room="bedroom",
        filter_type="True HEPA H13",
    )
    dev_id = FirestoreService.save_indoor_device(user_id, device)
    assert dev_id == "purifier_bedroom_01"

    devices = FirestoreService.list_indoor_devices(user_id)
    assert len(devices) == 1
    assert devices[0]["device_name"] == "Master Bedroom HEPA"

    log = PersistedImpactLog(
        log_id="log_metro_commute_01",
        activity_type="clean_commute",
        emission_saved_kg_co2=1.45,
        notes="Took Delhi Metro instead of petrol car",
    )
    log_id = FirestoreService.save_impact_log(user_id, log)
    assert log_id == "log_metro_commute_01"

    logs = FirestoreService.list_impact_logs(user_id)
    assert len(logs) == 1
    assert logs[0]["emission_saved_kg_co2"] == 1.45


def test_firestore_unavailable_graceful_fallback():
    """Verify that when Firestore is offline, methods return None / empty lists without uncaught exceptions."""
    reset_firebase()

    with patch("backend.app.services.firestore_service.is_firebase_available", return_value=False):
        assert FirestoreService.get_user_profile("any_user") is None
        assert FirestoreService.list_routines("any_user") == []
        assert FirestoreService.list_chat_sessions("any_user") == []
        assert FirestoreService.list_routes("any_user") == []
        assert FirestoreService.list_indoor_devices("any_user") == []
        assert FirestoreService.list_impact_logs("any_user") == []


def test_account_switching_data_isolation(mock_db):
    """Verify that User A's and User B's subcollections remain completely isolated."""
    user_a = "user_alpha"
    user_b = "user_beta"

    # User A saves routine
    FirestoreService.save_routine(
        user_a,
        PersistedRoutineRecord(
            routine_id="routine_alpha",
            station_id="delhi-anand-vihar",
            date_str="2026-11-18",
            plan={"summary": "Alpha Schedule"},
        ),
    )

    # User B saves route
    FirestoreService.save_route(
        user_b,
        PersistedSavedRoute(
            route_id="route_beta",
            title="Beta Commute",
            distance_km=10.0,
            current_mode="cng_auto",
        ),
    )

    # Check isolation
    user_a_routines = FirestoreService.list_routines(user_a)
    user_b_routines = FirestoreService.list_routines(user_b)
    assert len(user_a_routines) == 1
    assert len(user_b_routines) == 0  # User B has no routines

    user_a_routes = FirestoreService.list_routes(user_a)
    user_b_routes = FirestoreService.list_routes(user_b)
    assert len(user_a_routes) == 0  # User A has no routes
    assert len(user_b_routes) == 1
