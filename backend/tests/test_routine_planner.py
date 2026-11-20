import json
from datetime import datetime
from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.models.aqi import AqiCategory, CurrentAqiResponse, HealthAdvisory, PollutantDetail, StationInfo
from backend.app.models.routine import (
    FamilyVulnerabilityInput,
    RoutinePlanRequest,
    RoutinePlanResponse,
    RoutinePreferencesInput,
)
from backend.app.services.routine_planner_service import RoutinePlannerService


@pytest.fixture
def sample_aqi_reading():
    """Mock a realistic CPCB reading for testing."""
    return CurrentAqiResponse(
        station=StationInfo(
            id="delhi-anand-vihar",
            name="Anand Vihar",
            city="Delhi",
            state="Delhi",
            latitude=28.6469,
            longitude=77.3160,
            is_hotspot=True,
        ),
        aqi=379,
        category=AqiCategory.VERY_POOR,
        prominent_pollutant="PM2.5",
        pollutants={
            "PM2.5": PollutantDetail(
                name="PM2.5",
                value=222.0,
                unit="µg/m³",
                sub_index=379,
                category=AqiCategory.VERY_POOR,
                standard_limit=60.0,
                who_limit=15.0,
            ),
            "PM10": PollutantDetail(
                name="PM10",
                value=207.0,
                unit="µg/m³",
                sub_index=172,
                category=AqiCategory.MODERATE,
                standard_limit=100.0,
                who_limit=45.0,
            ),
        },
        health_advisory=HealthAdvisory(
            general_advice="High health risk",
            children_and_seniors="Avoid outdoor activity",
            patients_with_respiratory_issues="Remain indoors",
            outdoor_activity="Avoid",
            mask_recommendation="N95 Mandatory",
            purifier_recommendation="Run continuously",
            ventilation_window="Brief mid-day only",
        ),
        weather={"temperature": 18.0, "humidity": 68.0, "condition": "Smoggy"},
        data_source="Central Pollution Control Board (CPCB) - CAAQMS",
        last_updated=datetime(2026, 11, 18, 15, 0, 0),
        is_demo_data=False,
    )


def test_routine_plan_structure(sample_aqi_reading):
    with patch("backend.app.services.routine_planner_service.get_active_aqi_provider") as mock_get_provider:
        mock_provider = MagicMock()
        mock_provider.get_current_aqi.return_value = sample_aqi_reading
        mock_get_provider.return_value = mock_provider

        req = RoutinePlanRequest(
            station_id="delhi-anand-vihar",
            language="en",
            family_profile=FamilyVulnerabilityInput(has_children=True, has_seniors=True),
        )

        plan = RoutinePlannerService.generate_routine_plan(req)

        assert isinstance(plan, RoutinePlanResponse)
        assert plan.station_id == "delhi-anand-vihar"
        assert plan.aqi == 379
        assert plan.category == "Very Poor"
        assert plan.is_demo_data is False
        assert len(plan.morning) >= 1
        assert len(plan.afternoon) >= 1
        assert len(plan.evening) >= 1
        assert plan.school_commute.status in ("Caution", "Avoid")
        assert plan.office_commute.status == "Caution"
        assert plan.exercise_plan.status in ("Indoor Alternative", "Caution", "Avoid")
        assert "Medical Disclaimer" in plan.disclaimer
        assert len(plan.family_precautions) >= 2


def test_bilingual_support_english_and_hindi(sample_aqi_reading):
    with patch("backend.app.services.routine_planner_service.get_active_aqi_provider") as mock_get_provider:
        mock_provider = MagicMock()
        mock_provider.get_current_aqi.return_value = sample_aqi_reading
        mock_get_provider.return_value = mock_provider

        # English Request
        en_req = RoutinePlanRequest(station_id="delhi-anand-vihar", language="en")
        en_plan = RoutinePlannerService.generate_routine_plan(en_req)
        assert en_plan.language == "en"
        assert "School Commute" in en_plan.school_commute.title or "Transit" in en_plan.school_commute.title
        assert "Medical Disclaimer" in en_plan.disclaimer

        # Hindi Request
        hi_req = RoutinePlanRequest(station_id="delhi-anand-vihar", language="hi")
        hi_plan = RoutinePlannerService.generate_routine_plan(hi_req)
        assert hi_plan.language == "hi"
        assert "स्कूल" in hi_plan.school_commute.title
        assert "चिकित्सीय अस्वीकरण" in hi_plan.disclaimer


def test_vulnerability_customization(sample_aqi_reading):
    with patch("backend.app.services.routine_planner_service.get_active_aqi_provider") as mock_get_provider:
        mock_provider = MagicMock()
        mock_provider.get_current_aqi.return_value = sample_aqi_reading
        mock_get_provider.return_value = mock_provider

        family = FamilyVulnerabilityInput(
            has_children=True,
            has_seniors=True,
            has_respiratory_condition=True,
            is_pregnant=True,
        )
        req = RoutinePlanRequest(station_id="delhi-anand-vihar", language="en", family_profile=family)
        plan = RoutinePlannerService.generate_routine_plan(req)

        # Must have alerts for all 4 vulnerable cohorts
        joined_precautions = " ".join(plan.family_precautions).lower()
        assert "children" in joined_precautions
        assert "seniors" in joined_precautions
        assert "respiratory" in joined_precautions
        assert "mothers" in joined_precautions or "expectant" in joined_precautions or "pregnant" in joined_precautions


def test_demo_live_provenance_propagation(sample_aqi_reading):
    with patch("backend.app.services.routine_planner_service.get_active_aqi_provider") as mock_get_provider:
        mock_provider = MagicMock()

        # Case 1: Live Data
        sample_aqi_reading.is_demo_data = False
        sample_aqi_reading.data_source = "CPCB Live Test"
        mock_provider.get_current_aqi.return_value = sample_aqi_reading
        mock_get_provider.return_value = mock_provider

        plan_live = RoutinePlannerService.generate_routine_plan(RoutinePlanRequest(station_id="delhi-anand-vihar"))
        assert plan_live.is_demo_data is False
        assert plan_live.data_source == "CPCB Live Test"

        # Case 2: Demo Data Fallback
        sample_aqi_reading.is_demo_data = True
        sample_aqi_reading.data_source = "CPCB Demo Baseline"
        mock_provider.get_current_aqi.return_value = sample_aqi_reading

        plan_demo = RoutinePlannerService.generate_routine_plan(RoutinePlanRequest(station_id="delhi-anand-vihar"))
        assert plan_demo.is_demo_data is True
        assert plan_demo.data_source == "CPCB Demo Baseline"


def test_gemini_prompt_builder(sample_aqi_reading):
    family = FamilyVulnerabilityInput(has_children=True)
    prefs = RoutinePreferencesInput(preferred_exercise_type="run")
    prompt_en = RoutinePlannerService._build_gemini_prompt(sample_aqi_reading, family, prefs, "en")
    assert "Anand Vihar" in prompt_en
    assert "DIURNAL ATMOSPHERIC INVERSION" in prompt_en
    assert "Output a strictly valid JSON object" in prompt_en

    prompt_hi = RoutinePlannerService._build_gemini_prompt(sample_aqi_reading, family, prefs, "hi")
    assert "Hindi" in prompt_hi or "Devanagari" in prompt_hi


def test_gemini_response_validation():
    # Valid candidate payload matching Pydantic schema
    sample_candidate = {
        "morning": [
            {
                "title": "Morning Walk",
                "recommended_time": "11:00 AM - 12:00 PM",
                "status": "Caution",
                "risk_level": "High",
                "advice": "Shift walking indoors",
                "rationale": "High PM2.5 levels",
                "indoor_alternative": "Treadmill walking",
                "precautions": ["Wear N95"],
            }
        ],
        "afternoon": [
            {
                "title": "Natural Flush",
                "recommended_time": "01:00 PM - 02:00 PM",
                "status": "Recommended",
                "risk_level": "Moderate",
                "advice": "15 min ventilation",
                "rationale": "Peak boundary layer",
                "indoor_alternative": None,
                "precautions": [],
            }
        ],
        "evening": [
            {
                "title": "Night Protection",
                "recommended_time": "09:00 PM - 06:00 AM",
                "status": "Recommended",
                "risk_level": "Low",
                "advice": "Purifier on auto",
                "rationale": "Clean air sleep",
                "indoor_alternative": None,
                "precautions": [],
            }
        ],
        "school_commute": {
            "title": "School Transit",
            "recommended_time": "07:30 AM - 08:30 AM",
            "status": "Caution",
            "risk_level": "High",
            "advice": "N95 mask mandatory",
            "rationale": "Morning inversion",
            "indoor_alternative": None,
            "precautions": ["Pediatric mask"],
        },
        "office_commute": {
            "title": "Office Transit",
            "recommended_time": "09:00 AM - 10:00 AM",
            "status": "Caution",
            "risk_level": "High",
            "advice": "Metro travel preferred",
            "rationale": "Traffic soot avoidance",
            "indoor_alternative": "WFH",
            "precautions": ["Recirculation in car"],
        },
        "exercise_plan": {
            "title": "Exercise",
            "recommended_time": "12:30 PM",
            "status": "Indoor Alternative",
            "risk_level": "High",
            "advice": "Do indoor yoga",
            "rationale": "Lung strain",
            "indoor_alternative": "Yoga",
            "precautions": [],
        },
        "chores_plan": {
            "title": "Errands",
            "recommended_time": "02:00 PM",
            "status": "Caution",
            "risk_level": "Moderate",
            "advice": "Dry clothes inside",
            "rationale": "Soot on fabric",
            "indoor_alternative": None,
            "precautions": [],
        },
        "family_precautions": ["Keep inhaler handy"],
    }

    # Verify Pydantic can validate the JSON structure when metadata is injected
    meta = {
        "station_id": "delhi-anand-vihar",
        "station_name": "Anand Vihar",
        "city": "Delhi",
        "aqi": 379,
        "category": "Very Poor",
        "prominent_pollutant": "PM2.5",
        "is_demo_data": False,
        "data_source": "CPCB Live",
        "observed_at": datetime.utcnow().isoformat(),
        "language": "en",
        "ai_provider": "google-gemini",
        "ai_generated": True,
        "generated_at": datetime.utcnow().isoformat(),
        "disclaimer": "Medical Disclaimer",
    }
    sample_candidate.update(meta)
    validated = RoutinePlanResponse.model_validate(sample_candidate)
    assert validated.ai_provider == "google-gemini"
    assert validated.ai_generated is True
    assert validated.aqi == 379


def test_routine_api_endpoints(sample_aqi_reading):
    from backend.app.api.v1.endpoints.routine import create_routine_plan, get_routine_plan_get

    with patch("backend.app.services.routine_planner_service.get_active_aqi_provider") as mock_get_provider:
        mock_provider = MagicMock()
        mock_provider.get_current_aqi.return_value = sample_aqi_reading
        mock_get_provider.return_value = mock_provider

        # Test POST endpoint function
        req = RoutinePlanRequest(
            station_id="delhi-anand-vihar",
            language="en",
            family_profile=FamilyVulnerabilityInput(has_children=True, has_seniors=True),
            preferences=RoutinePreferencesInput(preferred_exercise_type="gym"),
        )
        post_res = create_routine_plan(request=req)
        assert post_res.success is True
        assert post_res.data.station_id == "delhi-anand-vihar"
        assert post_res.data.school_commute is not None
        assert post_res.data.office_commute is not None

        # Test GET endpoint function
        get_res = get_routine_plan_get(
            station_id="delhi-anand-vihar",
            language="hi",
            has_children=True,
            has_seniors=False,
            has_respiratory=True,
            is_pregnant=False,
            exercise_type="walk",
        )
        assert get_res.success is True
        assert get_res.data.language == "hi"
        assert "स्कूल" in get_res.data.school_commute.title


def test_sanitize_json_text_markdown_fences():
    # Test plain JSON
    raw_plain = '{"key": "value"}'
    assert RoutinePlannerService._sanitize_json_text(raw_plain) == '{"key": "value"}'

    # Test ```json\n...\n```
    raw_json_fence = '```json\n{"key": "value"}\n```'
    assert RoutinePlannerService._sanitize_json_text(raw_json_fence) == '{"key": "value"}'

    # Test ```\n...\n```
    raw_plain_fence = '```\n{"key": "value"}\n```'
    assert RoutinePlannerService._sanitize_json_text(raw_plain_fence) == '{"key": "value"}'

    # Test with extra whitespace
    raw_spaced = '   ```json   \n   {"key": "value"}   \n   ```   '
    assert RoutinePlannerService._sanitize_json_text(raw_spaced) == '{"key": "value"}'


VALID_ROUTINE_SCHEDULE = {
    "morning": [],
    "afternoon": [],
    "evening": [],
    "school_commute": {
        "title": "School Commute",
        "recommended_time": "07:30 AM",
        "status": "Caution",
        "risk_level": "High",
        "advice": "Wear N95",
        "rationale": "Inversion layer",
        "indoor_alternative": None,
        "precautions": [],
    },
    "office_commute": {
        "title": "Office Commute",
        "recommended_time": "09:00 AM",
        "status": "Caution",
        "risk_level": "High",
        "advice": "Metro preferred",
        "rationale": "High NO2",
        "indoor_alternative": None,
        "precautions": [],
    },
    "exercise_plan": {
        "title": "Exercise",
        "recommended_time": "01:00 PM",
        "status": "Indoor Alternative",
        "risk_level": "Critical",
        "advice": "Indoor yoga only",
        "rationale": "Lung strain",
        "indoor_alternative": "Yoga",
        "precautions": [],
    },
    "chores_plan": {
        "title": "Chores",
        "recommended_time": "02:00 PM",
        "status": "Caution",
        "risk_level": "Moderate",
        "advice": "Dry clothes indoors",
        "rationale": "Soot on damp fabric",
        "indoor_alternative": None,
        "precautions": [],
    },
    "family_precautions": ["Keep children indoors"],
}


def test_gemini_successful_structured_json(sample_aqi_reading):
    from backend.app.core.config import settings

    with patch("backend.app.services.routine_planner_service.get_active_aqi_provider") as mock_get_provider:
        mock_provider = MagicMock()
        mock_provider.get_current_aqi.return_value = sample_aqi_reading
        mock_get_provider.return_value = mock_provider

        with patch("backend.app.services.routine_planner_service.generate_gemini_text") as mock_gen:
            mock_gen.return_value = json.dumps(VALID_ROUTINE_SCHEDULE)
            with patch.object(settings, "GEMINI_API_KEY", "test-key"):
                req = RoutinePlanRequest(station_id="delhi-anand-vihar", language="en")
                plan = RoutinePlannerService.generate_routine_plan(req)

                assert plan.ai_provider == "google-gemini"
                assert plan.ai_generated is True
                assert plan.station_id == "delhi-anand-vihar"
                assert plan.aqi == 379
                assert plan.school_commute.title == "School Commute"
                assert plan.office_commute.status == "Caution"
                mock_gen.assert_called_once()


def test_gemini_markdown_fenced_json(sample_aqi_reading):
    from backend.app.core.config import settings

    with patch("backend.app.services.routine_planner_service.get_active_aqi_provider") as mock_get_provider:
        mock_provider = MagicMock()
        mock_provider.get_current_aqi.return_value = sample_aqi_reading
        mock_get_provider.return_value = mock_provider

        fenced = f"```json\n{json.dumps(VALID_ROUTINE_SCHEDULE)}\n```"

        with patch("backend.app.services.routine_planner_service.generate_gemini_text") as mock_gen:
            mock_gen.return_value = fenced
            with patch.object(settings, "GEMINI_API_KEY", "test-key"):
                req = RoutinePlanRequest(station_id="delhi-anand-vihar", language="en")
                plan = RoutinePlannerService.generate_routine_plan(req)

                assert plan.ai_provider == "google-gemini"
                assert plan.ai_generated is True
                assert plan.school_commute.title == "School Commute"


def test_gemini_fallback_modes(sample_aqi_reading):
    from backend.app.core.config import settings

    with patch("backend.app.services.routine_planner_service.get_active_aqi_provider") as mock_get_provider:
        mock_provider = MagicMock()
        mock_provider.get_current_aqi.return_value = sample_aqi_reading
        mock_get_provider.return_value = mock_provider

        req = RoutinePlanRequest(station_id="delhi-anand-vihar", language="en")

        # Case 1: None output
        with patch("backend.app.services.routine_planner_service.generate_gemini_text", return_value=None):
            with patch.object(settings, "GEMINI_API_KEY", "test-key"):
                plan_none = RoutinePlannerService.generate_routine_plan(req)
                assert plan_none.ai_provider == "expert-rules-fallback"
                assert plan_none.ai_generated is False

        # Case 2: Empty/whitespace output
        with patch("backend.app.services.routine_planner_service.generate_gemini_text", return_value="   "):
            with patch.object(settings, "GEMINI_API_KEY", "test-key"):
                plan_empty = RoutinePlannerService.generate_routine_plan(req)
                assert plan_empty.ai_provider == "expert-rules-fallback"
                assert plan_empty.ai_generated is False

        # Case 3: Malformed JSON
        with patch("backend.app.services.routine_planner_service.generate_gemini_text", return_value="{malformed json ..."):
            with patch.object(settings, "GEMINI_API_KEY", "test-key"):
                plan_bad = RoutinePlannerService.generate_routine_plan(req)
                assert plan_bad.ai_provider == "expert-rules-fallback"
                assert plan_bad.ai_generated is False

        # Case 4: Non-dict JSON (e.g. JSON array)
        with patch("backend.app.services.routine_planner_service.generate_gemini_text", return_value='["not", "a", "dict"]'):
            with patch.object(settings, "GEMINI_API_KEY", "test-key"):
                plan_arr = RoutinePlannerService.generate_routine_plan(req)
                assert plan_arr.ai_provider == "expert-rules-fallback"
                assert plan_arr.ai_generated is False

        # Case 5: API Exception
        with patch("backend.app.services.routine_planner_service.generate_gemini_text", side_effect=RuntimeError("Google GenAI API failure")):
            with patch.object(settings, "GEMINI_API_KEY", "test-key"):
                plan_exc = RoutinePlannerService.generate_routine_plan(req)
                assert plan_exc.ai_provider == "expert-rules-fallback"
                assert plan_exc.ai_generated is False

