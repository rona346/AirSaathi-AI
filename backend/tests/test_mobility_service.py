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
from backend.app.services.transit_service import TransitAvailabilityStatus, TransitService


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
        aqi=425,
        category=AqiCategory.SEVERE,
        prominent_pollutant="PM2.5",
        pollutants={
            "PM2.5": PollutantDetail(
                name="PM2.5",
                value=280.0,
                unit="µg/m³",
                sub_index=425,
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


def test_emission_calculations_and_occupancy_assumptions():
    """Validates vehicle-level vs passenger-level emissions, grid factor (~716 g CO2/kWh),

    and occupancy assumptions across all transport modes.
    """
    distance = 10.0  # 10 km

    # 1. Private Petrol Car (solo default: 165 g/km * 10 km = 1650 g direct, 0 grid)
    dir_p, grid_p, tot_p, per_p = EmissionsService.calculate_trip_emissions(
        TransportMode.PETROL_CAR, distance, occupancy=1
    )
    assert dir_p == 1650.0
    assert grid_p == 0.0
    assert tot_p == 1650.0
    assert per_p == 1650.0

    # 2. Electric 4W Car (EV): Zero tailpipe, upstream grid 107.4 g/km (0.15 kWh/km * 716 g/kWh)
    dir_e, grid_e, tot_e, per_e = EmissionsService.calculate_trip_emissions(
        TransportMode.ELECTRIC_CAR, distance, occupancy=1
    )
    assert dir_e == 0.0
    assert grid_e == 1074.0
    assert tot_e == 1074.0
    assert per_e == 1074.0  # Solo driver

    # 3. Public Bus: Vehicle direct 1100 g/km * 10 km = 11,000 g; occupancy 35 -> 314.3 g/pax
    dir_b, grid_b, tot_b, per_b = EmissionsService.calculate_trip_emissions(
        TransportMode.PUBLIC_BUS, distance, occupancy=1
    )
    assert dir_b == 11000.0
    assert grid_b == 0.0
    assert tot_b == 11000.0
    assert per_b == 314.3

    # 4. Electric Bus: Vehicle grid 859.2 g/km * 10 km = 8,592 g; occupancy 35 -> 245.5 g/pax
    dir_eb, grid_eb, tot_eb, per_eb = EmissionsService.calculate_trip_emissions(
        TransportMode.ELECTRIC_BUS, distance, occupancy=1
    )
    assert dir_eb == 0.0
    assert grid_eb == 8592.0
    assert tot_eb == 8592.0
    assert per_eb == 245.5

    # 5. CNG Auto: Vehicle direct 72 g/km * 10 km = 720 g; occupancy 2 -> 360.0 g/pax
    dir_a, grid_a, tot_a, per_a = EmissionsService.calculate_trip_emissions(
        TransportMode.CNG_AUTO, distance, occupancy=1
    )
    assert dir_a == 720.0
    assert per_a == 360.0

    # 6. Active Walking & Cycling: Exactly 0.0 g
    dir_w, grid_w, tot_w, per_w = EmissionsService.calculate_trip_emissions(
        TransportMode.WALKING, distance, occupancy=1
    )
    assert tot_w == 0.0
    assert per_w == 0.0


def test_carpooling_potential_reductions():
    """Validates multi-occupant carpooling reductions and savings formulas."""
    distance = 15.0
    carpool = EmissionsService.calculate_carpooling_potential(distance, round_trips_per_day=2.0)

    # Solo: 165 * 15 = 2475 g
    assert carpool.solo_trip_emissions_g == 2475.0
    # 2-person: 2475 / 2 = 1237.5 g (50% reduction)
    assert carpool.shared_2_person_emissions_g == 1237.5
    # 3-person: 2475 / 3 = 825.0 g (67% reduction)
    assert carpool.shared_3_person_emissions_g == 825.0
    # 4-person: 2475 / 4 = 618.8 g (75% reduction)
    assert carpool.shared_4_person_emissions_g == 618.8
    # Daily savings for 3-person pool (round trip = 2 trips): (2475 - 825) * 2 = 3300 g = 3.3 kg
    assert carpool.daily_savings_kg == 3.3
    # Annual: 3.3 * 250 = 825 kg
    assert carpool.annual_savings_kg == 825.0


def test_udaipur_no_metro_availability():
    """Test 1: For Udaipur, verifies Metro is never recommended as an available transport option."""
    req = MobilityRequest(
        city="Udaipur",
        distance_km=15.0,  # Long distance where Metro is normally considered in metro cities
        current_mode=TransportMode.PETROL_CAR,
        language="en",
    )
    plan = MobilityService.generate_mobility_plan(req)

    # 1. Metro must NOT be the recommended mode
    assert plan.recommended_mode != TransportMode.METRO
    assert plan.recommended_mode in (TransportMode.CARPOOL, TransportMode.PUBLIC_BUS, TransportMode.ELECTRIC_BUS)

    # 2. Recommendation reason must explicitly note metro unviability in Udaipur
    assert "Udaipur" in plan.recommended_mode_reason
    assert "not operational" in plan.recommended_mode_reason.lower() or "unavailable" in plan.recommended_mode_reason.lower()

    # 3. Metro in mode comparisons must be explicitly marked as unavailable
    metro_detail = next(m for m in plan.mode_comparisons if m.mode == TransportMode.METRO)
    assert metro_detail.availability_status == "unavailable"
    assert "Not Available in Udaipur" in metro_detail.suitability_score
    assert "Metro rail service is not operational in Udaipur" in metro_detail.aqi_safety_verdict
    assert metro_detail.co2e_savings_pct == 0.0


def test_city_with_metro_availability_delhi(mock_cpcb_reading_severe):
    """Test 2: A city with Metro availability (Delhi) allows Metro recommendation with qualified language."""
    mock_provider = MagicMock()
    mock_provider.get_current_aqi.return_value = mock_cpcb_reading_severe

    with patch("backend.app.services.mobility_service.get_active_aqi_provider", return_value=mock_provider):
        req = MobilityRequest(
            city="Delhi",
            station_id="delhi-anand-vihar",
            distance_km=12.0,
            current_mode=TransportMode.PETROL_CAR,
            language="en",
        )
        plan = MobilityService.generate_mobility_plan(req)

        # Metro is operational in Delhi
        assert plan.recommended_mode == TransportMode.METRO

        metro_detail = next(m for m in plan.mode_comparisons if m.mode == TransportMode.METRO)
        assert metro_detail.availability_status == "available"
        assert "Recommended" in metro_detail.suitability_score
        assert "Optimal Today" not in metro_detail.suitability_score
        assert "Safe" not in metro_detail.suitability_score  # No absolute claims
        assert metro_detail.co2e_savings_pct > 80.0


def test_unknown_city_neutral_recommendation():
    """Test 3: If city or transport availability is unknown, uses neutral recommendation and clearly communicates limitation."""
    req = MobilityRequest(
        city="Ruritania",
        station_id="ruritania-unknown",
        distance_km=14.0,
        current_mode=TransportMode.PETROL_CAR,
        language="en",
    )
    plan = MobilityService.generate_mobility_plan(req)

    # Must NOT recommend Metro
    assert plan.recommended_mode != TransportMode.METRO
    assert plan.recommended_mode == TransportMode.CARPOOL

    # Must clearly communicate the limitation in recommendation reason
    assert "unverified" in plan.recommended_mode_reason.lower()

    metro_detail = next(m for m in plan.mode_comparisons if m.mode == TransportMode.METRO)
    assert metro_detail.availability_status == "unverified"
    assert "Unverified" in metro_detail.suitability_score


def test_aqi_advisory_thresholds_and_qualified_language(mock_cpcb_reading_severe, mock_cpcb_reading_moderate):
    """Test 4: Reviews advisory thresholds against CPCB categories and ensures qualified, non-absolute safety language."""
    # 1. Severe AQI (425 >= 401)
    comparisons_severe = EmissionsService.compare_all_modes(
        distance_km=3.0,
        current_mode=TransportMode.PETROL_CAR,
        aqi=mock_cpcb_reading_severe.aqi,
        city="Delhi",
        language="en",
    )
    walk_severe = next(c for c in comparisons_severe if c.mode == TransportMode.WALKING)
    metro_severe = next(c for c in comparisons_severe if c.mode == TransportMode.METRO)
    car_severe = next(c for c in comparisons_severe if c.mode == TransportMode.PETROL_CAR)

    assert "High Health Risk - Not Advised" in walk_severe.suitability_score
    assert walk_severe.exposure_level == "Severe"

    # Metro and Cars must use qualified language, never "Safe" or "Optimal Today"
    assert "Recommended - Lower Exposure" in metro_severe.suitability_score
    assert "Optimal Today" not in metro_severe.suitability_score
    assert "Enclosed Cabin Safe" not in car_severe.aqi_safety_verdict
    assert "does not provide zero exposure" in car_severe.aqi_safety_verdict

    # 2. Satisfactory/Good AQI (88 <= 100)
    comparisons_mod = EmissionsService.compare_all_modes(
        distance_km=1.5,
        current_mode=TransportMode.PETROL_CAR,
        aqi=mock_cpcb_reading_moderate.aqi,
        city="Delhi",
        language="en",
    )
    walk_mod = next(c for c in comparisons_mod if c.mode == TransportMode.WALKING)
    assert "Favorable - Active Travel" in walk_mod.suitability_score
    assert walk_mod.exposure_level == "Minimal"


def test_demo_versus_live_data_labelling():
    """Test 5: Validates live vs demo data labelling, source attribution, and preserves city rather than defaulting to Anand Vihar."""
    # 1. Test unverified city station fallback
    req_custom = MobilityRequest(city="Udaipur", distance_km=5.0)
    plan_custom = MobilityService.generate_mobility_plan(req_custom)
    assert plan_custom.is_demo_data is True
    assert plan_custom.city == "Udaipur"
    assert "Anand Vihar" not in plan_custom.city

    # 2. Test live CPCB mock
    live_reading = CurrentAqiResponse(
        station=StationInfo(
            id="mumbai-bandra-kurla",
            name="Bandra Kurla Complex",
            city="Mumbai",
            state="Maharashtra",
            latitude=19.0657,
            longitude=72.8687,
            is_hotspot=False,
        ),
        aqi=160,
        category=AqiCategory.MODERATE,
        prominent_pollutant="PM10",
        pollutants={},
        health_advisory=HealthAdvisory(
            general_advice="Moderate",
            children_and_seniors="Take breaks",
            patients_with_respiratory_issues="Normal",
            outdoor_activity="Moderate",
            mask_recommendation="Optional",
            purifier_recommendation="Bedrooms",
            ventilation_window="Noon",
        ),
        weather={"temperature": 29.0, "humidity": 65.0, "condition": "Hazy"},
        data_source="CPCB Live Telemetry",
        last_updated=datetime.utcnow(),
        is_demo_data=False,
    )
    mock_provider = MagicMock()
    mock_provider.get_current_aqi.return_value = live_reading

    with patch("backend.app.services.mobility_service.get_active_aqi_provider", return_value=mock_provider):
        req_live = MobilityRequest(station_id="mumbai-bandra-kurla", distance_km=8.0)
        plan_live = MobilityService.generate_mobility_plan(req_live)
        assert plan_live.is_demo_data is False
        assert plan_live.data_source == "CPCB Live Telemetry"
        assert plan_live.city == "Mumbai"


def test_api_fallback_behaviour(mock_cpcb_reading_severe):
    """Test 6: Validates seamless expert-rule fallback when Gemini API fails."""
    mock_provider = MagicMock()
    mock_provider.get_current_aqi.return_value = mock_cpcb_reading_severe
    with patch("backend.app.services.mobility_service.get_active_aqi_provider", return_value=mock_provider):
        with patch("backend.app.core.config.settings.GEMINI_API_KEY", "mock-key"):
            with patch("httpx.Client.post") as mock_post:
                mock_post.return_value = MagicMock(status_code=500, text="Internal Server Error")

                req = MobilityRequest(distance_km=8.0, current_mode=TransportMode.PETROL_CAR, city="Delhi")
                plan = MobilityService.generate_mobility_plan(req)

                assert plan.ai_provider == "expert-rules-fallback"
                assert plan.ai_generated is False
                assert "Sustainable Mobility Strategy (Delhi" in plan.ai_recommendation


def test_mobility_api_endpoints(mock_cpcb_reading_severe):
    """Test 7: Validates FastAPI POST and GET endpoints with city query parameters and distance constraints."""
    from backend.app.api.v1.endpoints.mobility import plan_sustainable_commute, plan_sustainable_commute_get

    mock_provider = MagicMock()
    mock_provider.get_current_aqi.return_value = mock_cpcb_reading_severe

    with patch("backend.app.services.mobility_service.get_active_aqi_provider", return_value=mock_provider):
        with patch.object(MobilityService, "_call_gemini_mobility", return_value="Mock strategy"):
            # 1. Valid POST with city
            req_valid = MobilityRequest(
                city="Delhi",
                distance_km=10.0,
                language="en",
                current_mode=TransportMode.PETROL_CAR,
                frequency=CommuteFrequency.DAILY_ROUND_TRIP,
                purpose=CommutePurpose.OFFICE,
                occupancy=1,
            )
            res = plan_sustainable_commute(request=req_valid)
            assert res.success is True
            assert res.data.distance_km == 10.0
            assert res.data.city == "Delhi"
            assert len(res.data.mode_comparisons) == 12

            # 2. Valid GET with city parameter
            res_get = plan_sustainable_commute_get(distance_km=7.5, city="Udaipur", current_mode="petrol_car")
            assert res_get.success is True
            assert res_get.data.distance_km == 7.5
            assert res_get.data.city == "Udaipur"
            assert res_get.data.recommended_mode != TransportMode.METRO

            # 3. Invalid Distance: 0 or negative
            with pytest.raises(Exception):
                plan_sustainable_commute(request=MobilityRequest(distance_km=0))

            # 4. Invalid Distance: > 150 km
            with pytest.raises(Exception):
                plan_sustainable_commute(request=MobilityRequest(distance_km=250))
