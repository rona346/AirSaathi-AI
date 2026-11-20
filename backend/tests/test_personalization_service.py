"""Unit tests for Module 7: Personalization and Household Advisory Service.

Verifies:
1. Pydantic model validation, defaults, and bounds.
2. Deterministic advisory generation across AQI scenarios (Good, Moderate, Poor, Severe).
3. Alert threshold sensitivity behavior (sensitive vs standard vs high tolerance).
4. Asset-aware guidance (HEPA purifier, kitchen exhaust, indoor monitor).
5. Commute and daily activity window matching without city-specific assumptions.
6. Provenance preservation (live CPCB vs demo/fallback).
7. Missing/unavailable AQI handling (explicit unavailable status without fabrication).
8. Mandatory exposure-mitigation disclaimer and zero medical claims.
9. Alert threshold non-interference with official AQI and CPCB categories.
10. Scientific corrections: pediatric mask framing, senior seasonal neutrality,
    HEPA runtime reasonableness, kitchen negative pressure/window avoidance during severe smog,
    and non-prescriptive respiratory guidance.
"""

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
import pytest

from backend.app.models.aqi import (
    AqiCategory,
    CurrentAqiResponse,
    HealthAdvisory,
    PollutantDetail,
    StationInfo,
)
from backend.app.models.routine import FamilyVulnerabilityInput
from backend.app.models.user import (
    AlertThresholdPreference,
    FamilyPreferencesData,
    HouseholdCleanAirPreferences,
    HouseholdDemographics,
    PersonalizedAdvisoryResponse,
)
from backend.app.services.personalization_service import (
    DISCLAIMER_TEXT,
    PersonalizationService,
)


def make_mock_aqi_response(
    aqi: int = 160,
    category: AqiCategory = AqiCategory.MODERATE,
    is_demo: bool = False,
    data_source: str = "data.gov.in (Official CPCB)",
    station_id: str = "delhi-anand-vihar",
) -> CurrentAqiResponse:
    """Helper to construct verified CurrentAqiResponse instances for testing."""
    station = StationInfo(
        id=station_id,
        name="Anand Vihar",
        city="Delhi",
        state="Delhi",
        latitude=28.6508,
        longitude=77.3152,
        is_hotspot=True,
    )
    return CurrentAqiResponse(
        station=station,
        aqi=aqi,
        category=category,
        prominent_pollutant="PM2.5",
        pollutants={
            "PM2.5": PollutantDetail(
                name="PM2.5",
                value=75.0,
                unit="µg/m³",
                sub_index=aqi,
                category=category,
                standard_limit=60.0,
                who_limit=15.0,
            )
        },
        health_advisory=HealthAdvisory(
            general_advice="Air quality acceptable for healthy adults.",
            children_and_seniors="Limit prolonged outdoor exertion.",
            patients_with_respiratory_issues="Keep relief inhaler handy.",
            outdoor_activity="Moderate exertion permissible.",
            mask_recommendation="Optional for general public.",
            purifier_recommendation="Use in bedrooms.",
            ventilation_window="12:00 PM - 03:00 PM",
        ),
        weather={},
        data_source=data_source,
        last_updated=datetime(2026, 11, 20, 10, 30, tzinfo=timezone.utc),
        is_demo_data=is_demo,
    )


def test_models_defaults_and_validation():
    """Verify default values and bounds for Module 7 models."""
    demographics = HouseholdDemographics()
    assert demographics.has_adults is True
    assert demographics.has_children is False
    assert demographics.has_seniors is False
    assert demographics.has_infants is False

    preferences = HouseholdCleanAirPreferences()
    assert preferences.alert_threshold == AlertThresholdPreference.STANDARD
    assert preferences.preferred_transit_mode == "public_transit"  # neutral default
    assert preferences.has_kitchen_exhaust is True
    assert preferences.has_hepa_purifier is False

    family = FamilyPreferencesData()
    assert family.household_size == 2
    assert family.vulnerability.has_children is False
    assert family.demographics.has_children is False
    assert family.members == []


def test_good_aqi_normal_guidance():
    """Verify that under Good air quality, advisory yields positive/normal guidance."""
    aqi_data = make_mock_aqi_response(aqi=45, category=AqiCategory.GOOD)
    family = FamilyPreferencesData(
        household_size=4,
        demographics=HouseholdDemographics(has_infants=True, has_children=True, has_adults=True),
        preferences=HouseholdCleanAirPreferences(has_hepa_purifier=True),
    )

    advisory = PersonalizationService.generate_advisory(family=family, aqi_data=aqi_data)

    assert advisory.status == "active"
    assert advisory.aqi == 45
    assert advisory.category == "Good"
    assert advisory.threshold_applied == AlertThresholdPreference.STANDARD
    assert advisory.disclaimer == DISCLAIMER_TEXT

    # Infants under good AQI receive normal guidance
    infant_action = next((a for a in advisory.actions if a.target_group == "infants"), None)
    assert infant_action is not None
    assert infant_action.priority == "good"
    assert "Infant Outdoor Air Quality Normal" in infant_action.title

    # HEPA purifier under good AQI operates as needed without continuous mandates
    purifier_action = next((a for a in advisory.actions if a.category == "indoor_asset" and "Filtration" in a.title), None)
    assert purifier_action is not None
    assert purifier_action.priority == "good"


def test_alert_threshold_sensitivity_trigger():
    """Verify that a 'sensitive' threshold triggers elevated caution at Moderate AQI (140) whereas 'standard' does not."""
    aqi_data = make_mock_aqi_response(aqi=140, category=AqiCategory.MODERATE)

    # Household 1: Standard threshold (triggers at >200)
    fam_standard = FamilyPreferencesData(
        demographics=HouseholdDemographics(has_children=True, has_seniors=True),
        preferences=HouseholdCleanAirPreferences(
            alert_threshold=AlertThresholdPreference.STANDARD,
            school_commute_active=True,
            morning_outdoor_window=True,
        ),
    )
    adv_standard = PersonalizationService.generate_advisory(family=fam_standard, aqi_data=aqi_data)
    child_act_std = next((a for a in adv_standard.actions if a.target_group == "children"), None)
    assert child_act_std is None

    # Household 2: Sensitive threshold (triggers at >100)
    fam_sensitive = FamilyPreferencesData(
        demographics=HouseholdDemographics(has_children=True, has_seniors=True),
        preferences=HouseholdCleanAirPreferences(
            alert_threshold=AlertThresholdPreference.SENSITIVE,
            school_commute_active=True,
            morning_outdoor_window=True,
        ),
    )
    adv_sensitive = PersonalizationService.generate_advisory(family=fam_sensitive, aqi_data=aqi_data)
    child_act_sens = next((a for a in adv_sensitive.actions if a.target_group == "children"), None)
    assert child_act_sens is not None
    assert child_act_sens.priority == "caution"
    assert "Commute" in child_act_sens.title or "School" in child_act_sens.title


def test_poor_aqi_multi_generational_actions():
    """Verify complete actions generated for multi-generational household under Poor AQI (280)."""
    aqi_data = make_mock_aqi_response(aqi=280, category=AqiCategory.POOR)
    family = FamilyPreferencesData(
        household_size=5,
        vulnerability=FamilyVulnerabilityInput(
            has_children=True,
            has_seniors=True,
            has_respiratory_condition=True,
            is_pregnant=True,
        ),
        demographics=HouseholdDemographics(
            has_infants=True,
            has_children=True,
            has_adults=True,
            has_seniors=True,
        ),
        preferences=HouseholdCleanAirPreferences(
            has_hepa_purifier=True,
            has_kitchen_exhaust=True,
            has_indoor_monitor=True,
            preferred_transit_mode="public_transit",
            school_commute_active=True,
            morning_outdoor_window=True,
            office_commute_active=True,
        ),
    )

    advisory = PersonalizationService.generate_advisory(family=family, aqi_data=aqi_data)

    assert advisory.status == "active"
    assert advisory.aqi == 280
    assert advisory.household_size == 5

    categories = {a.category for a in advisory.actions}
    assert "demographic" in categories
    assert "indoor_asset" in categories
    assert "commute" in categories

    targets = {a.target_group for a in advisory.actions}
    assert "infants" in targets
    assert "children" in targets
    assert "seniors" in targets
    assert "respiratory_sensitive" in targets
    assert "pregnant" in targets

    assert advisory.equipment_status["has_hepa_purifier"] is True
    assert advisory.equipment_status["has_kitchen_exhaust"] is True
    assert advisory.equipment_status["has_indoor_monitor"] is True

    assert "Infant Respiratory Shield" in advisory.active_safeguards
    assert "Pediatric Airway Safeguard" in advisory.active_safeguards
    assert "Senior Cardiovascular Safeguard" in advisory.active_safeguards
    assert "Asthma & Allergy Preparedness" in advisory.active_safeguards
    assert "HEPA Indoor Filtration" in advisory.active_safeguards


def test_active_commute_warning_under_smog():
    """Verify warning when preferred transit is active (cycling/walking) during high smog."""
    aqi_data = make_mock_aqi_response(aqi=340, category=AqiCategory.VERY_POOR)
    family = FamilyPreferencesData(
        preferences=HouseholdCleanAirPreferences(preferred_transit_mode="cycling"),
    )

    advisory = PersonalizationService.generate_advisory(family=family, aqi_data=aqi_data)
    commute_act = next((a for a in advisory.actions if a.category == "commute" and "Active Commute" in a.title), None)

    assert commute_act is not None
    assert commute_act.priority == "urgent"
    assert "cycling" in commute_act.description


def test_provenance_preservation_live_vs_demo():
    """Verify that live data and demo data maintain their exact data_source and is_demo_data flags."""
    live_aqi = make_mock_aqi_response(aqi=220, is_demo=False, data_source="data.gov.in (Official CPCB)")
    demo_aqi = make_mock_aqi_response(aqi=220, is_demo=True, data_source="CPCB Calibrated Baseline")

    family = FamilyPreferencesData()

    adv_live = PersonalizationService.generate_advisory(family=family, aqi_data=live_aqi)
    assert adv_live.is_demo_data is False
    assert adv_live.data_source == "data.gov.in (Official CPCB)"

    adv_demo = PersonalizationService.generate_advisory(family=family, aqi_data=demo_aqi)
    assert adv_demo.is_demo_data is True
    assert adv_demo.data_source == "CPCB Calibrated Baseline"


def test_missing_or_unavailable_aqi_handling():
    """Verify that missing AQI data returns an explicit unavailable status without fabricating numbers."""
    family = FamilyPreferencesData(household_size=3)

    adv = PersonalizationService.generate_advisory(family=family, aqi_data=None, station_id=None)
    assert adv.status == "unavailable"
    assert adv.aqi is None
    assert adv.category is None
    assert adv.data_source == "Unavailable"
    assert len(adv.actions) == 1
    assert adv.actions[0].title == "Air Quality Telemetry Unavailable"
    assert adv.household_size == 3
    assert adv.disclaimer == DISCLAIMER_TEXT

    with patch("backend.app.services.personalization_service.get_active_aqi_provider", side_effect=RuntimeError("Provider down")):
        adv_err = PersonalizationService.generate_advisory(family=family, aqi_data=None, station_id="unknown_station")
        assert adv_err.status == "unavailable"
        assert adv_err.aqi is None


def test_threshold_does_not_modify_official_aqi_or_category():
    """Verify that setting alert_threshold to sensitive or high_tolerance never alters official AQI reading or CPCB category."""
    aqi_data = make_mock_aqi_response(aqi=185, category=AqiCategory.MODERATE)

    for thresh in (AlertThresholdPreference.SENSITIVE, AlertThresholdPreference.STANDARD, AlertThresholdPreference.HIGH_TOLERANCE):
        fam = FamilyPreferencesData(preferences=HouseholdCleanAirPreferences(alert_threshold=thresh))
        adv = PersonalizationService.generate_advisory(family=fam, aqi_data=aqi_data)
        assert adv.aqi == 185
        assert adv.category == "Moderate"
        assert adv.threshold_applied == thresh


# --- NEW SCIENTIFIC & SAFETY AUDIT VERIFICATION TESTS ---

def test_pediatric_advice_avoids_unqualified_adult_n95_mandates():
    """Verify pediatric advice avoids unqualified adult N95 mandates, emphasizes assembly shifting, and never masks infants."""
    aqi_data = make_mock_aqi_response(aqi=260, category=AqiCategory.POOR)
    family = FamilyPreferencesData(
        demographics=HouseholdDemographics(has_infants=True, has_children=True),
        preferences=HouseholdCleanAirPreferences(school_commute_active=True),
    )

    advisory = PersonalizationService.generate_advisory(family=family, aqi_data=aqi_data)

    # 1. Child guidance must prioritize outdoor exposure reduction & indoor school assemblies
    child_action = next((a for a in advisory.actions if a.target_group == "children"), None)
    assert child_action is not None
    assert "outdoor morning assemblies" in child_action.description.lower()
    assert "indoors" in child_action.description.lower()
    # Must NOT contain blanket mandate like "Ensure children wear certified pediatric-fit N95"
    assert "certified pediatric-fit n95" not in child_action.description.lower()

    # 2. Infant guidance must NEVER recommend masks of any kind
    infant_action = next((a for a in advisory.actions if a.target_group == "infants"), None)
    assert infant_action is not None
    assert "mask" not in infant_action.description.lower()
    assert "mask" not in infant_action.title.lower()


def test_transit_defaults_to_public_transit():
    """Verify that HouseholdCleanAirPreferences defaults to a neutral 'public_transit' mode."""
    pref = HouseholdCleanAirPreferences()
    assert pref.preferred_transit_mode == "public_transit"


def test_no_unsupported_city_specific_metro_assumptions():
    """Verify that transit recommendations avoid hardcoded Delhi Metro references and support generic public transit."""
    aqi_data = make_mock_aqi_response(aqi=220, category=AqiCategory.POOR, station_id="udaipur-ashok-nagar")
    family = FamilyPreferencesData(
        preferences=HouseholdCleanAirPreferences(preferred_transit_mode="public_transit")
    )

    advisory = PersonalizationService.generate_advisory(family=family, aqi_data=aqi_data)
    commute_action = next((a for a in advisory.actions if a.category == "commute"), None)

    assert commute_action is not None
    # Must not contain hardcoded "Delhi Metro"
    assert "delhi metro" not in commute_action.title.lower()
    assert "delhi metro" not in commute_action.description.lower()
    assert "Public Transit" in commute_action.title


def test_senior_advice_avoids_unconditional_winter_inversion_claims():
    """Verify senior outdoor advice avoids unconditional seasonal claims like 'winter inversion' or 'cold morning smog'."""
    aqi_data = make_mock_aqi_response(aqi=240, category=AqiCategory.POOR)
    family = FamilyPreferencesData(
        demographics=HouseholdDemographics(has_seniors=True),
        preferences=HouseholdCleanAirPreferences(morning_outdoor_window=True),
    )

    advisory = PersonalizationService.generate_advisory(family=family, aqi_data=aqi_data)
    senior_action = next((a for a in advisory.actions if a.target_group == "seniors"), None)

    assert senior_action is not None
    # No unconditional seasonal assertions
    assert "winter inversion" not in senior_action.rationale.lower()
    assert "winter inversion" not in senior_action.description.lower()
    assert "cold morning smog" not in senior_action.rationale.lower()


def test_hepa_advice_avoids_continuous_or_auto_mode_assumptions():
    """Verify HEPA advice avoids mandating continuous 24/7 runtime and does not assume auto/eco mode hardware."""
    # Scenario A: Elevated AQI
    aqi_high = make_mock_aqi_response(aqi=210, category=AqiCategory.POOR)
    fam_hepa = FamilyPreferencesData(preferences=HouseholdCleanAirPreferences(has_hepa_purifier=True))
    adv_high = PersonalizationService.generate_advisory(family=fam_hepa, aqi_data=aqi_high)
    purifier_high = next((a for a in adv_high.actions if a.category == "indoor_asset" and "Filtration" in a.title), None)

    assert purifier_high is not None
    # Must not prescribe rigid 24/7 continuous runtime
    assert "continuously" not in purifier_high.description.lower()
    assert "prioritize operating" in purifier_high.description.lower()

    # Scenario B: Moderate AQI
    aqi_mod = make_mock_aqi_response(aqi=75, category=AqiCategory.SATISFACTORY)
    adv_mod = PersonalizationService.generate_advisory(family=fam_hepa, aqi_data=aqi_mod)
    purifier_mod = next((a for a in adv_mod.actions if a.category == "indoor_asset" and "Filtration" in a.title), None)

    assert purifier_mod is not None
    # Must not assume "auto/eco mode"
    assert "auto/eco mode" not in purifier_mod.description.lower()


def test_kitchen_advice_avoids_opening_windows_during_severe_aqi():
    """Verify that during severe outdoor smog, kitchen advice explicitly avoids advising opening exterior windows."""
    aqi_severe = make_mock_aqi_response(aqi=320, category=AqiCategory.VERY_POOR)

    # Case 1: Household with exhaust
    fam_exhaust = FamilyPreferencesData(preferences=HouseholdCleanAirPreferences(has_kitchen_exhaust=True))
    adv_exhaust = PersonalizationService.generate_advisory(family=fam_exhaust, aqi_data=aqi_severe)
    act_exhaust = next((a for a in adv_exhaust.actions if a.category == "indoor_asset" and "Kitchen" in a.title), None)
    assert act_exhaust is not None
    assert "avoiding opening windows facing heavy outdoor smog" in act_exhaust.description.lower()

    # Case 2: Household without exhaust
    fam_no_exhaust = FamilyPreferencesData(preferences=HouseholdCleanAirPreferences(has_kitchen_exhaust=False))
    adv_no_exhaust = PersonalizationService.generate_advisory(family=fam_no_exhaust, aqi_data=aqi_severe)
    act_no_exhaust = next((a for a in adv_no_exhaust.actions if a.category == "indoor_asset" and "Kitchen" in a.title), None)
    assert act_no_exhaust is not None
    # Must explicitly warn against opening exterior windows to severe smog
    assert "avoid opening exterior windows" in act_no_exhaust.description.lower()


def test_respiratory_advice_avoids_specific_drug_or_device_prescriptions():
    """Verify respiratory advice references physician management and avoids drug/device prescriptions."""
    aqi_data = make_mock_aqi_response(aqi=180, category=AqiCategory.MODERATE)
    family = FamilyPreferencesData(
        vulnerability=FamilyVulnerabilityInput(has_respiratory_condition=True)
    )

    advisory = PersonalizationService.generate_advisory(family=family, aqi_data=aqi_data)
    resp_action = next((a for a in advisory.actions if a.target_group == "respiratory_sensitive"), None)

    assert resp_action is not None
    # Must avoid specific drug names and device prescriptions
    assert "bronchodilator" not in resp_action.description.lower()
    assert "spacer" not in resp_action.description.lower()
    # Must use physician-directed framing
    assert "physician-prescribed" in resp_action.description.lower()
