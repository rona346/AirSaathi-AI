import json
from datetime import datetime
from unittest.mock import MagicMock, patch
import pytest

from backend.app.models.aqi import AqiCategory, CurrentAqiResponse, HealthAdvisory, PollutantDetail, StationInfo
from backend.app.models.indoor import (
    CleaningMethod,
    CookingFuel,
    HouseholdInput,
    IndoorAssessmentRequest,
    IndoorAssessmentResponse,
    QualitativeRiskLevel,
    RoomType,
    VentilationStatus,
)
from backend.app.services.indoor_service import IndoorAirService


@pytest.fixture
def mock_outdoor_cpcb():
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
        data_source="Central Pollution Control Board (CPCB) - CAAQMS Live",
        last_updated=datetime(2026, 11, 18, 15, 0, 0),
        is_demo_data=False,
    )


def test_indoor_assessment_structure(mock_outdoor_cpcb):
    with patch("backend.app.services.indoor_service.get_active_aqi_provider") as mock_get_provider:
        mock_provider = MagicMock()
        mock_provider.get_current_aqi.return_value = mock_outdoor_cpcb
        mock_get_provider.return_value = mock_provider

        req = IndoorAssessmentRequest(
            station_id="delhi-anand-vihar",
            language="en",
            household=HouseholdInput(
                room_type=RoomType.LIVING_ROOM,
                room_area_sqft=200.0,
                heavy_frying_or_tadka=True,
                burns_agarbatti_or_dhoop=True,
            ),
        )

        res = IndoorAirService.evaluate_indoor_air(req)

        assert isinstance(res, IndoorAssessmentResponse)
        assert res.has_connected_indoor_sensor is False
        assert res.qualitative_risk in (QualitativeRiskLevel.HIGH, QualitativeRiskLevel.SEVERE)
        assert 0 <= res.risk_score_numeric <= 100
        assert res.purifier_guidance.recommended_min_cadr_m3h > 0
        assert "bedroom" in res.room_recommendations
        assert "kitchen" in res.room_recommendations
        assert len(res.actionable_checklist) >= 3
        assert "NASA" in res.plant_myth_clarification or "plants" in res.plant_myth_clarification.lower()
        assert "Medical Disclaimer" in res.disclaimer


def test_no_indoor_sensor_truthfulness(mock_outdoor_cpcb):
    """Ensure the system never fabricates numerical indoor AQI without physical sensors."""
    with patch("backend.app.services.indoor_service.get_active_aqi_provider") as mock_get_provider:
        mock_provider = MagicMock()
        mock_provider.get_current_aqi.return_value = mock_outdoor_cpcb
        mock_get_provider.return_value = mock_provider

        res = IndoorAirService.evaluate_indoor_air(IndoorAssessmentRequest(station_id="delhi-anand-vihar"))
        assert res.has_connected_indoor_sensor is False
        assert "Without physical in-situ air sensors" in res.sensor_notice or "बिना प्रमाणित इनडोर सेंसर" in res.sensor_notice
        # Ensure there is NO field called indoor_aqi or numerical indoor concentration
        assert not hasattr(res, "indoor_aqi")


def test_bilingual_indoor_output(mock_outdoor_cpcb):
    with patch("backend.app.services.indoor_service.get_active_aqi_provider") as mock_get_provider:
        mock_provider = MagicMock()
        mock_provider.get_current_aqi.return_value = mock_outdoor_cpcb
        mock_get_provider.return_value = mock_provider

        # English
        res_en = IndoorAirService.evaluate_indoor_air(IndoorAssessmentRequest(language="en"))
        assert res_en.language == "en"
        assert "Medical Disclaimer" in res_en.disclaimer
        assert "Ventilation" in res_en.ventilation.action or "Seal" in res_en.ventilation.action

        # Hindi
        res_hi = IndoorAirService.evaluate_indoor_air(IndoorAssessmentRequest(language="hi"))
        assert res_hi.language == "hi"
        assert "चिकित्सीय अस्वीकरण" in res_hi.disclaimer
        assert "सेंसर प्रकटीकरण" in res_hi.sensor_notice


def test_cadr_calculation(mock_outdoor_cpcb):
    with patch("backend.app.services.indoor_service.get_active_aqi_provider") as mock_get_provider:
        mock_provider = MagicMock()
        mock_provider.get_current_aqi.return_value = mock_outdoor_cpcb
        mock_get_provider.return_value = mock_provider

        # Room: 200 sqft, 10 ft ceiling
        # Volume = 200 * 10 * 0.0283168 = 56.63 m³
        # CADR = 56.63 * 4.5 ACH = ~254 m³/h
        req = IndoorAssessmentRequest(
            household=HouseholdInput(room_area_sqft=200.0, ceiling_height_ft=10.0)
        )
        res = IndoorAirService.evaluate_indoor_air(req)
        assert 240 <= res.purifier_guidance.recommended_min_cadr_m3h <= 270
        assert res.purifier_guidance.target_ach == 4.5


def test_outdoor_provenance_propagation(mock_outdoor_cpcb):
    with patch("backend.app.services.indoor_service.get_active_aqi_provider") as mock_get_provider:
        mock_provider = MagicMock()

        # Case 1: Live CPCB Data
        mock_outdoor_cpcb.is_demo_data = False
        mock_outdoor_cpcb.data_source = "Live CPCB Feed"
        mock_provider.get_current_aqi.return_value = mock_outdoor_cpcb
        mock_get_provider.return_value = mock_provider

        res_live = IndoorAirService.evaluate_indoor_air(IndoorAssessmentRequest())
        assert res_live.outdoor_is_demo is False
        assert res_live.outdoor_data_source == "Live CPCB Feed"
        assert res_live.outdoor_aqi == 379

        # Case 2: Demo Baseline Data
        mock_outdoor_cpcb.is_demo_data = True
        mock_outdoor_cpcb.data_source = "CPCB Demo Baseline"
        mock_provider.get_current_aqi.return_value = mock_outdoor_cpcb

        res_demo = IndoorAirService.evaluate_indoor_air(IndoorAssessmentRequest())
        assert res_demo.outdoor_is_demo is True
        assert res_demo.outdoor_data_source == "CPCB Demo Baseline"


def test_plant_myth_clarification(mock_outdoor_cpcb):
    with patch("backend.app.services.indoor_service.get_active_aqi_provider") as mock_get_provider:
        mock_provider = MagicMock()
        mock_provider.get_current_aqi.return_value = mock_outdoor_cpcb
        mock_get_provider.return_value = mock_provider

        res = IndoorAirService.evaluate_indoor_air(IndoorAssessmentRequest())
        myth_text = res.plant_myth_clarification.lower()
        assert "plant" in myth_text
        assert "hepa" in myth_text or "filtration" in myth_text
        assert "replace" in myth_text or "substitute" in myth_text


MOCK_GEMINI_PAYLOAD = {
    "qualitative_risk": "High",
    "risk_score_numeric": 72,
    "risk_summary": "High particulate infiltration with indoor cooking emissions.",
    "ventilation": {
        "action": "Seal",
        "optimal_window": "01:00 PM - 02:00 PM",
        "duration_minutes": 15,
        "rationale": "Peak boundary layer dispersion window.",
        "precautions": ["Keep windows sealed at night", "Run kitchen exhaust"],
    },
    "purifier_guidance": {
        "room_area_sqft": 150.0,
        "recommended_min_cadr_m3h": 250,
        "recommended_min_cadr_cfm": 150,
        "target_ach": 4.5,
        "filter_type_guidance": "True HEPA H13/H14 filter.",
        "placement_tips": ["Place 1 meter away from walls", "Avoid corners"],
        "maintenance_schedule": "Vacuum pre-filter bi-weekly.",
    },
    "kitchen_guidance": {
        "risk_summary": "High PM2.5 spike during tadka.",
        "chimney_exhaust_guidance": "Run exhaust 2 mins prior to cooking.",
        "cooking_habits_advice": ["Cover pans with lids", "Avoid dry roasting spices unventilated"],
        "combustion_safety": "Check for blue flame on LPG burner.",
    },
    "room_recommendations": {
        "bedroom": {
            "room_name": "Bedroom",
            "primary_threats": ["Nocturnal particulate settling"],
            "immediate_actions": ["Seal windows", "Run purifier on sleep mode"],
            "night_protocol": "Keep purifier 2m from bed",
            "lifestyle_adjustments": ["Wet mop floor before sleeping"],
        },
        "kitchen": {
            "room_name": "Kitchen",
            "primary_threats": ["Acrolein and ultrafine particulates"],
            "immediate_actions": ["Run chimney on maximum"],
            "night_protocol": None,
            "lifestyle_adjustments": ["Isolate kitchen door while frying"],
        },
    },
    "actionable_checklist": [
        "Seal windows during night inversion",
        "Operate ducted chimney during cooking",
        "Use wet mopping instead of dry brooming",
        "Run HEPA purifier at target ACH",
    ],
    "plant_myth_clarification": "Potted plants cannot replace mechanical HEPA filtration in real homes.",
}


def test_gemini_successful_json(mock_outdoor_cpcb):
    from backend.app.core.config import settings

    with patch("backend.app.services.indoor_service.get_active_aqi_provider") as mock_get_provider:
        mock_provider = MagicMock()
        mock_provider.get_current_aqi.return_value = mock_outdoor_cpcb
        mock_get_provider.return_value = mock_provider

        with patch("backend.app.services.indoor_service.generate_gemini_text") as mock_gen:
            mock_gen.return_value = json.dumps(MOCK_GEMINI_PAYLOAD)
            with patch.object(settings, "GEMINI_API_KEY", "test-key"):
                res = IndoorAirService.evaluate_indoor_air(IndoorAssessmentRequest())

                assert res.ai_provider == "google-gemini"
                assert res.ai_generated is True
                assert res.has_connected_indoor_sensor is False
                assert res.qualitative_risk == QualitativeRiskLevel.HIGH
                assert res.risk_score_numeric == 72
                assert res.station_id == "delhi-anand-vihar"
                assert res.outdoor_aqi == 379
                assert res.purifier_guidance.recommended_min_cadr_m3h == 250
                assert "bedroom" in res.room_recommendations
                assert len(res.actionable_checklist) == 4
                mock_gen.assert_called_once()


def test_gemini_markdown_fenced_json(mock_outdoor_cpcb):
    from backend.app.core.config import settings

    with patch("backend.app.services.indoor_service.get_active_aqi_provider") as mock_get_provider:
        mock_provider = MagicMock()
        mock_provider.get_current_aqi.return_value = mock_outdoor_cpcb
        mock_get_provider.return_value = mock_provider

        fenced_payload = f"```json\n{json.dumps(MOCK_GEMINI_PAYLOAD)}\n```"

        with patch("backend.app.services.indoor_service.generate_gemini_text") as mock_gen:
            mock_gen.return_value = fenced_payload
            with patch.object(settings, "GEMINI_API_KEY", "test-key"):
                res = IndoorAirService.evaluate_indoor_air(IndoorAssessmentRequest())

                assert res.ai_provider == "google-gemini"
                assert res.ai_generated is True
                assert res.qualitative_risk == QualitativeRiskLevel.HIGH
                assert res.risk_score_numeric == 72
                assert res.has_connected_indoor_sensor is False


def test_gemini_fallback_on_api_error_and_malformed(mock_outdoor_cpcb):
    from backend.app.core.config import settings

    with patch("backend.app.services.indoor_service.get_active_aqi_provider") as mock_get_provider:
        mock_provider = MagicMock()
        mock_provider.get_current_aqi.return_value = mock_outdoor_cpcb
        mock_get_provider.return_value = mock_provider

        # Test None output
        with patch("backend.app.services.indoor_service.generate_gemini_text", return_value=None):
            with patch.object(settings, "GEMINI_API_KEY", "test-key"):
                res_none = IndoorAirService.evaluate_indoor_air(IndoorAssessmentRequest())
                assert res_none.ai_provider == "expert-rules-fallback"
                assert res_none.ai_generated is False
                assert res_none.has_connected_indoor_sensor is False

        # Test Empty output
        with patch("backend.app.services.indoor_service.generate_gemini_text", return_value="   "):
            with patch.object(settings, "GEMINI_API_KEY", "test-key"):
                res_empty = IndoorAirService.evaluate_indoor_air(IndoorAssessmentRequest())
                assert res_empty.ai_provider == "expert-rules-fallback"
                assert res_empty.ai_generated is False

        # Test API Exception
        with patch("backend.app.services.indoor_service.generate_gemini_text", side_effect=RuntimeError("Google GenAI API failure")):
            with patch.object(settings, "GEMINI_API_KEY", "test-key"):
                res_exc = IndoorAirService.evaluate_indoor_air(IndoorAssessmentRequest())
                assert res_exc.ai_provider == "expert-rules-fallback"
                assert res_exc.ai_generated is False

        # Test Malformed JSON
        with patch("backend.app.services.indoor_service.generate_gemini_text", return_value="{malformed json ..."):
            with patch.object(settings, "GEMINI_API_KEY", "test-key"):
                res_bad = IndoorAirService.evaluate_indoor_air(IndoorAssessmentRequest())
                assert res_bad.ai_provider == "expert-rules-fallback"
                assert res_bad.ai_generated is False

        # Test Non-dict JSON (e.g., JSON array)
        with patch("backend.app.services.indoor_service.generate_gemini_text", return_value='["not", "a", "dict"]'):
            with patch.object(settings, "GEMINI_API_KEY", "test-key"):
                res_arr = IndoorAirService.evaluate_indoor_air(IndoorAssessmentRequest())
                assert res_arr.ai_provider == "expert-rules-fallback"
                assert res_arr.ai_generated is False


def test_indoor_api_endpoints(mock_outdoor_cpcb):
    from backend.app.api.v1.endpoints.indoor import assess_indoor_air, assess_indoor_air_get

    with patch("backend.app.services.indoor_service.get_active_aqi_provider") as mock_get_provider:
        mock_provider = MagicMock()
        mock_provider.get_current_aqi.return_value = mock_outdoor_cpcb
        mock_get_provider.return_value = mock_provider

        # Test POST
        req = IndoorAssessmentRequest(
            station_id="delhi-anand-vihar",
            language="en",
            household=HouseholdInput(room_type=RoomType.BEDROOM, has_air_purifier=True),
        )
        post_res = assess_indoor_air(request=req)
        assert post_res.success is True
        assert post_res.data.station_id == "delhi-anand-vihar"
        assert post_res.data.purifier_guidance is not None

        # Test GET
        get_res = assess_indoor_air_get(
            station_id="delhi-anand-vihar",
            language="hi",
            room_type="kitchen",
            heavy_frying=True,
            burns_incense=True,
        )
        assert get_res.success is True
        assert get_res.data.language == "hi"
        assert get_res.data.has_connected_indoor_sensor is False
