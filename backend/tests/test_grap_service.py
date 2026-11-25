"""
Unit tests for CAQM GRAP (Graded Response Action Plan) evaluation service.

Verifies:
1. Exact threshold boundaries for CAQM stages (0-200, 201-300, 301-400, 401-450, >450).
2. Delhi-NCR geographic jurisdiction limits (non-NCR cities return applicable=False).
3. Indicative AQI status labeling and statutory executive order disclaimers.
4. Clean integration into CurrentAqiResponse through AqiService.
"""

import pytest
from backend.app.models.aqi import GrapStage
from backend.app.services.aqi_service import AqiService
from backend.app.services.grap_service import (
    evaluate_grap,
    get_grap_stage_for_aqi,
    is_ncr_location,
)


class TestGrapJurisdiction:
    def test_ncr_cities_detected(self):
        assert is_ncr_location(city="Delhi") is True
        assert is_ncr_location(city="new delhi") is True
        assert is_ncr_location(city="Noida") is True
        assert is_ncr_location(city="Greater Noida") is True
        assert is_ncr_location(city="Ghaziabad") is True
        assert is_ncr_location(city="Gurugram") is True
        assert is_ncr_location(city="Gurgaon") is True
        assert is_ncr_location(city="Faridabad") is True
        assert is_ncr_location(city="Alwar") is True

    def test_ncr_states_detected(self):
        assert is_ncr_location(state="Delhi") is True
        assert is_ncr_location(state="NCT of Delhi") is True

    def test_non_ncr_locations_excluded(self):
        assert is_ncr_location(city="Mumbai", state="Maharashtra") is False
        assert is_ncr_location(city="Bengaluru", state="Karnataka") is False
        assert is_ncr_location(city="Udaipur", state="Rajasthan") is False
        assert is_ncr_location(city="Kolkata", state="West Bengal") is False
        assert is_ncr_location(city="Chennai", state="Tamil Nadu") is False
        assert is_ncr_location(city="Pune", state="Maharashtra") is False
        assert is_ncr_location(city="", state="") is False
        assert is_ncr_location(city=None, state=None) is False


class TestGrapThresholdBoundaries:
    @pytest.mark.parametrize("aqi", [0, 50, 100, 150, 199, 200])
    def test_normal_aqi_no_grap_curbs(self, aqi: int):
        assert get_grap_stage_for_aqi(aqi) == GrapStage.NONE

    @pytest.mark.parametrize("aqi", [201, 202, 250, 299, 300])
    def test_stage_1_boundary(self, aqi: int):
        assert get_grap_stage_for_aqi(aqi) == GrapStage.STAGE_1

    @pytest.mark.parametrize("aqi", [301, 302, 350, 399, 400])
    def test_stage_2_boundary(self, aqi: int):
        assert get_grap_stage_for_aqi(aqi) == GrapStage.STAGE_2

    @pytest.mark.parametrize("aqi", [401, 402, 425, 449, 450])
    def test_stage_3_boundary(self, aqi: int):
        assert get_grap_stage_for_aqi(aqi) == GrapStage.STAGE_3

    @pytest.mark.parametrize("aqi", [451, 452, 480, 500, 850])
    def test_stage_4_boundary(self, aqi: int):
        assert get_grap_stage_for_aqi(aqi) == GrapStage.STAGE_4


class TestGrapEvaluationLogic:
    def test_non_ncr_evaluation(self):
        status = evaluate_grap(aqi=460, city="Mumbai", state="Maharashtra")
        assert status.applicable is False
        assert status.stage == GrapStage.NONE
        assert "Outside Delhi-NCR" in status.stage_name
        assert status.status_type == "indicative_aqi_based"
        assert status.is_official_order is False
        assert "outside Delhi-NCR" in status.notice
        assert any("statutory only within the National Capital Region" in c for c in status.curbs_summary)

    def test_ncr_stage_1_evaluation(self):
        status = evaluate_grap(aqi=245, city="Delhi", state="Delhi")
        assert status.applicable is True
        assert status.stage == GrapStage.STAGE_1
        assert "Stage I — Poor" in status.stage_name
        assert status.aqi_threshold == "201–300"
        assert status.status_type == "indicative_aqi_based"
        assert status.is_official_order is False
        assert any("anti-smog guns" in curb.lower() for curb in status.curbs_summary)
        # Verify September 2026 revised measures advanced to Stage I:
        assert any("dg set" in curb.lower() for curb in status.curbs_summary)
        assert any("bs-iv" in curb.lower() and "bus" in curb.lower() for curb in status.curbs_summary)
        assert "Indicative stage modeled from ambient CPCB AQI telemetry" in status.notice
        assert "September 2026" in status.notice

    def test_ncr_stage_2_evaluation(self):
        status = evaluate_grap(aqi=340, city="Noida", state="Uttar Pradesh")
        assert status.applicable is True
        assert status.stage == GrapStage.STAGE_2
        assert "Stage II — Very Poor" in status.stage_name
        assert status.aqi_threshold == "301–400"
        assert any("sweeping" in curb.lower() for curb in status.curbs_summary)
        assert any("parking fee" in curb.lower() for curb in status.curbs_summary)

    def test_ncr_stage_3_evaluation(self):
        status = evaluate_grap(aqi=415, city="Gurugram", state="Haryana")
        assert status.applicable is True
        assert status.stage == GrapStage.STAGE_3
        assert "Stage III — Severe" in status.stage_name
        assert status.aqi_threshold == "401–450"
        assert any("construction" in curb.lower() for curb in status.curbs_summary)
        # Verify vehicle restriction covers Sonipat under revised schedule:
        assert any("sonipat" in curb.lower() for curb in status.curbs_summary)
        assert any("bs-iii petrol and bs-iv diesel" in curb.lower() for curb in status.curbs_summary)

    def test_ncr_stage_4_evaluation(self):
        status = evaluate_grap(aqi=475, city="Delhi", state="Delhi")
        assert status.applicable is True
        assert status.stage == GrapStage.STAGE_4
        assert "Stage IV — Severe+" in status.stage_name
        assert status.aqi_threshold == "> 450"
        assert any("trucks" in curb.lower() for curb in status.curbs_summary)


class TestAqiServiceGrapIntegration:
    def test_delhi_station_has_applicable_grap(self):
        data = AqiService.get_current_aqi("delhi-anand-vihar")
        assert data.grap_status is not None
        assert data.grap_status.applicable is True
        assert data.grap_status.stage in [
            GrapStage.STAGE_1,
            GrapStage.STAGE_2,
            GrapStage.STAGE_3,
            GrapStage.STAGE_4,
        ]
        assert data.grap_status.is_official_order is False

    def test_mumbai_station_has_non_applicable_grap(self):
        data = AqiService.get_current_aqi("mumbai-bandra-kurla")
        assert data.grap_status is not None
        assert data.grap_status.applicable is False
        assert data.grap_status.stage == GrapStage.NONE
        assert "Outside Delhi-NCR" in data.grap_status.stage_name

    def test_bengaluru_station_has_non_applicable_grap(self):
        data = AqiService.get_current_aqi("bengaluru-btm-layout")
        assert data.grap_status is not None
        assert data.grap_status.applicable is False
