from datetime import datetime
from unittest.mock import MagicMock, patch
import httpx
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.models.aqi import AqiCategory, CurrentAqiResponse, HealthAdvisory, PollutantDetail, StationInfo
from backend.app.models.mobility import (
    AccessibilityNeed,
    CommuteFrequency,
    CommutePurpose,
    MobilityRequest,
    TransportMode,
)
from backend.app.services.emissions_service import EmissionsService
from backend.app.services.mobility_service import MobilityService


@pytest.fixture
def mock_cpcb_reading_severe():
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
        aqi=382,
        category=AqiCategory.SEVERE,
        prominent_pollutant="PM2.5",
        pollutants={
            "PM2.5": PollutantDetail(
                name="PM2.5",
                value=245.0,
                unit="µg/m³",
                sub_index=382,
                category=AqiCategory.SEVERE,
                standard_limit=60.0,
                who_limit=15.0,
            )
        },
        health_advisory=HealthAdvisory(
            general_advice="Avoid outdoor activity",
            children_and_seniors="Stay indoors",
            patients_with_respiratory_issues="Use inhalers",
            outdoor_activity="Avoid",
            mask_recommendation="N95 Mandatory",
            purifier_recommendation="Run HEPA",
            ventilation_window="Keep windows closed",
        ),
        weather={"temperature": 18.0, "humidity": 70.0, "condition": "Smoggy"},
        data_source="CPCB Live",
        last_updated=datetime.utcnow(),
        is_demo_data=False,
    )


@pytest.fixture
def mock_cpcb_reading_moderate():
    return CurrentAqiResponse(
        station=StationInfo(
            id="delhi-lodhi-road",
            name="Lodhi Road",
            city="Delhi",
            state="Delhi",
            latitude=28.5918,
            longitude=77.2273,
            is_hotspot=False,
        ),
        aqi=88,
        category=AqiCategory.SATISFACTORY,
        prominent_pollutant="PM10",
        pollutants={
            "PM10": PollutantDetail(
                name="PM10",
                value=75.0,
                unit="µg/m³",
                sub_index=88,
                category=AqiCategory.SATISFACTORY,
                standard_limit=100.0,
                who_limit=45.0,
            )
        },
        health_advisory=HealthAdvisory(
            general_advice="Air quality is acceptable",
            children_and_seniors="Normal activity",
            patients_with_respiratory_issues="Normal",
            outdoor_activity="Safe",
            mask_recommendation="Optional",
            purifier_recommendation="Natural ventilation",
            ventilation_window="11 AM - 4 PM",
        ),
        weather={"temperature": 24.0, "humidity": 45.0, "condition": "Clear"},
        data_source="CPCB Live",
        last_updated=datetime.utcnow(),
        is_demo_data=False,
    )


def test_emission_calculations_standard_modes():
    """Validates direct and upstream grid emission calculations for key transport modes."""
    distance = 10.0  # 10 km

    # 1. Private Petrol Car
    dir_p, grid_p, tot_p, per_p = EmissionsService.calculate_trip_emissions(
        TransportMode.PETROL_CAR, distance, occupancy=1
    )
    assert dir_p == 1650.0
    assert grid_p == 0.0
    assert tot_p == 1650.0
    assert per_p == 1650.0

    # 2. Electric 4W Car (EV) - acknowledges power grid emission intensity
    dir_e, grid_e, tot_e, per_e = EmissionsService.calculate_trip_emissions(
        TransportMode.ELECTRIC_CAR, distance, occupancy=1
    )
    assert dir_e == 0.0
    assert grid_e == 1074.0
    assert tot_e == 1074.0

    # 3. Metro Rail
    dir_m, grid_m, tot_m, per_m = EmissionsService.calculate_trip_emissions(
        TransportMode.METRO, distance, occupancy=1
    )
    assert dir_m == 0.0
    assert grid_m == 220.0
    assert tot_m == 220.0

    # 4. Active Walking and Cycling
    dir_w, grid_w, tot_w, _ = EmissionsService.calculate_trip_emissions(
        TransportMode.WALKING, distance, occupancy=1
    )
    assert tot_w == 0.0
    dir_c, grid_c, tot_c, _ = EmissionsService.calculate_trip_emissions(
        TransportMode.CYCLING, distance, occupancy=1
    )
    assert tot_c == 0.0


def test_carpooling_potential_reductions():
    """Validates multi-occupant carpooling calculations."""
    distance = 15.0  # 15 km one way
    carpool = EmissionsService.calculate_carpooling_potential(distance, round_trips_per_day=2.0)

    # Solo: 165 * 15 = 2475 g
    assert carpool.solo_trip_emissions_g == 2475.0
    # 2-person: 2475 / 2 = 1237.5 g
    assert carpool.shared_2_person_emissions_g == 1237.5
    # 3-person: 2475 / 3 = 825.0 g
    assert carpool.shared_3_person_emissions_g == 825.0
    # Daily savings (round trip = 2 trips) for 3-person pool: (2475 - 825) * 2 = 3300 g = 3.3 kg
    assert carpool.daily_savings_kg == 3.3
    # Annual: 3.3 * 250 = 825 kg
    assert carpool.annual_savings_kg == 825.0


def test_aqi_exposure_safety_rules(mock_cpcb_reading_severe, mock_cpcb_reading_moderate):
    """Ensures active mobility is restricted during Severe smog and encouraged only under acceptable AQI."""
    # Under Severe AQI (382)
    comparisons_severe = EmissionsService.compare_all_modes(
        distance_km=3.0,
        current_mode=TransportMode.PETROL_CAR,
        aqi=mock_cpcb_reading_severe.aqi,
        language="en",
    )
    walk_severe = next(c for c in comparisons_severe if c.mode == TransportMode.WALKING)
    cycle_severe = next(c for c in comparisons_severe if c.mode == TransportMode.CYCLING)
    metro_severe = next(c for c in comparisons_severe if c.mode == TransportMode.METRO)

    assert "Not Advised" in walk_severe.suitability_score
    assert walk_severe.exposure_level == "Severe"
    assert "Not Advised" in cycle_severe.suitability_score
    assert "Optimal" in metro_severe.suitability_score

    # Under Moderate/Satisfactory AQI (88)
    comparisons_mod = EmissionsService.compare_all_modes(
        distance_km=1.5,
        current_mode=TransportMode.PETROL_CAR,
        aqi=mock_cpcb_reading_moderate.aqi,
        language="en",
    )
    walk_mod = next(c for c in comparisons_mod if c.mode == TransportMode.WALKING)
    assert "Optimal" in walk_mod.suitability_score
    assert walk_mod.exposure_level == "Low"


def test_mobility_service_generate_plan_en(mock_cpcb_reading_severe):
    """Verifies complete English mobility plan generation with live CPCB mock."""
    mock_provider = MagicMock()
    mock_provider.get_current_aqi.return_value = mock_cpcb_reading_severe
    with patch(
        "backend.app.services.mobility_service.get_active_aqi_provider",
        return_value=mock_provider,
    ):
        with patch("backend.app.core.config.settings.GEMINI_API_KEY", "test-key"):
            with patch.object(
                MobilityService,
                "_call_gemini_mobility",
                return_value="Sustainable Commute Strategy with Metro",
            ):
                req = MobilityRequest(
                    station_id="delhi-anand-vihar",
                    language="en",
                    distance_km=12.0,
                    current_mode=TransportMode.PETROL_CAR,
                    frequency=CommuteFrequency.DAILY_ROUND_TRIP,
                    purpose=CommutePurpose.OFFICE,
                    occupancy=1,
                )

                plan = MobilityService.generate_mobility_plan(req)

                assert plan.station_name == "Anand Vihar"
                assert plan.aqi == 382
                assert plan.distance_km == 12.0
                assert plan.current_daily_emissions_g == 3960.0  # 165 * 12 * 2
                assert len(plan.mode_comparisons) == 12
                assert plan.recommended_mode == TransportMode.METRO
                assert "Severe" in plan.active_mobility_advisory
                assert len(plan.methodology_notes) >= 4
                assert plan.disclaimer is not None
                assert plan.ai_provider == "google-gemini"
                assert plan.ai_generated is True


def test_mobility_service_generate_plan_hi(mock_cpcb_reading_severe):
    """Verifies Hindi language output and Devanagari labels."""
    mock_provider = MagicMock()
    mock_provider.get_current_aqi.return_value = mock_cpcb_reading_severe
    with patch(
        "backend.app.services.mobility_service.get_active_aqi_provider",
        return_value=mock_provider,
    ):
        with patch("backend.app.core.config.settings.GEMINI_API_KEY", "test-key"):
            with patch.object(
                MobilityService,
                "_call_gemini_mobility",
                return_value="मेट्रो रेल से यात्रा करने पर 86% उत्सर्जन कम होगा",
            ):
                req = MobilityRequest(
                    station_id="delhi-anand-vihar",
                    language="hi",
                    distance_km=5.0,
                    current_mode=TransportMode.TWO_WHEELER,
                    frequency=CommuteFrequency.ONE_WAY,
                    purpose=CommutePurpose.ERRANDS,
                )

                plan = MobilityService.generate_mobility_plan(req)
                assert plan.language == "hi"
                assert (
                    "मेट्रो" in plan.recommended_mode_label
                    or "बस" in plan.recommended_mode_label
                    or "कारपूल" in plan.recommended_mode_label
                )
                assert "चेतावनी" in plan.active_mobility_advisory


def test_mobility_service_gemini_fallback(mock_cpcb_reading_severe):
    """Verifies that HTTP failure in Gemini API seamlessly falls back to the calibrated expert rule engine."""
    mock_provider = MagicMock()
    mock_provider.get_current_aqi.return_value = mock_cpcb_reading_severe
    with patch(
        "backend.app.services.mobility_service.get_active_aqi_provider",
        return_value=mock_provider,
    ):
        with patch("backend.app.core.config.settings.GEMINI_API_KEY", "mock-key"):
            with patch("httpx.Client.post") as mock_post:
                mock_post.return_value = MagicMock(status_code=500, text="Internal Server Error")

                req = MobilityRequest(distance_km=8.0, current_mode=TransportMode.PETROL_CAR)
                plan = MobilityService.generate_mobility_plan(req)

                assert plan.ai_provider == "expert-rules-fallback"
                assert plan.ai_generated is False
                assert "Sustainable Mobility Strategy" in plan.ai_recommendation


def test_mobility_api_endpoints(mock_cpcb_reading_severe):
    """Validates FastAPI POST and GET endpoints, along with input boundaries."""
    from fastapi import HTTPException
    from backend.app.api.v1.endpoints.mobility import plan_sustainable_commute, plan_sustainable_commute_get

    mock_provider = MagicMock()
    mock_provider.get_current_aqi.return_value = mock_cpcb_reading_severe

    with patch("backend.app.services.mobility_service.get_active_aqi_provider", return_value=mock_provider):
        with patch.object(MobilityService, "_call_gemini_mobility", return_value="Mock strategy"):
            # 1. Valid POST
            req_valid = MobilityRequest(
                distance_km=10.0,
                station_id="delhi-anand-vihar",
                language="en",
                current_mode=TransportMode.PETROL_CAR,
                frequency=CommuteFrequency.DAILY_ROUND_TRIP,
                purpose=CommutePurpose.OFFICE,
                occupancy=1,
            )
            res = plan_sustainable_commute(request=req_valid)
            assert res.success is True
            assert res.data.distance_km == 10.0
            assert len(res.data.mode_comparisons) == 12

            # 2. Valid GET
            res_get = plan_sustainable_commute_get(distance_km=7.5, current_mode="metro")
            assert res_get.success is True
            assert res_get.data.distance_km == 7.5

            # 3. Invalid Distance: 0 or negative
            with pytest.raises(Exception):
                plan_sustainable_commute(request=MobilityRequest(distance_km=0))

            # 4. Invalid Distance: > 150 km
            with pytest.raises(Exception):
                plan_sustainable_commute(request=MobilityRequest(distance_km=250))
