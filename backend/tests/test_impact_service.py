"""Unit tests for Module 6: Environmental Impact Calculation Engine & Service.

Verifies:
1. Strict separation of vehicle-km and passenger-km emission factors.
   - Metro passenger-km factor (22.0 g/pax-km) is NEVER divided by occupancy a second time.
   - Bus vehicle factors are properly allocated across 35 standard passengers.
2. Consistent baseline comparisons (solo private petrol car, 1 passenger, matching distance).
3. Truthful indoor actions: purifiers and ventilation mitigate particulate exposure and NEVER claim false CO2 reductions.
4. Electric Vehicles (EVs) reflect upstream grid intensity (CEA 716 g/kWh) and never claim zero emissions.
5. Carpooling splits vehicle emissions accurately across passenger pool.
6. Timeframe filtering and aggregations (Day, Week, Month, All-Time).
7. Strict data isolation between authenticated records and guest demonstration mode.
8. Optional educational tree-month equivalent calculation with disclaimers.
"""

from datetime import date, datetime, timedelta, timezone
import pytest

from backend.app.models.impact import (
    ImpactActivityType,
    ImpactLogCreate,
    ImpactLogRecord,
    TimeframeFilter,
)
from backend.app.models.mobility import TransportMode
from backend.app.services.impact_service import ImpactService


def test_metro_passenger_km_factor_never_divided_by_occupancy():
    """Verify that Metro factor (22.0 g/pax-km) is treated as a passenger-km factor,

    and is NEVER divided by occupancy even if passengers parameter > 1.
    """
    distance_km = 15.0

    # Test with 1 passenger
    v_kg_1, p_kg_1, base_kg_1, sav_kg_1, notes_1 = ImpactService.calculate_action_emissions(
        activity_type=ImpactActivityType.PUBLIC_TRANSIT,
        mode=TransportMode.METRO,
        distance_km=distance_km,
        passengers=1,
    )

    # 15 km * 22.0 g/pax-km = 330.0 g = 0.33 kg CO2e
    assert p_kg_1 == 0.33
    # Baseline for 15 km in petrol car: 15 * 165.0 g = 2475.0 g = 2.475 kg -> 2.475 kg
    assert base_kg_1 == 2.475
    # Savings: 2.475 - 0.33 = 2.145 kg
    assert sav_kg_1 == 2.145
    assert "passenger-allocated" in notes_1

    # Test with passengers=4: per-passenger emissions for Metro must still be 0.33 kg!
    # (It must NOT be divided into 0.33 / 4 = 0.0825 kg)
    _, p_kg_4, _, sav_kg_4, _ = ImpactService.calculate_action_emissions(
        activity_type=ImpactActivityType.PUBLIC_TRANSIT,
        mode=TransportMode.METRO,
        distance_km=distance_km,
        passengers=4,
    )
    assert p_kg_4 == 0.33
    assert sav_kg_4 == 2.145


def test_bus_vehicle_factor_allocated_across_standard_occupancy():
    """Verify that Public Bus and Electric Bus vehicle-km factors are allocated across

    standard MoHUA occupancy (35 passengers).
    """
    distance_km = 14.0

    # Public Bus: 1100 g/km vehicle level
    v_kg, p_kg, base_kg, sav_kg, notes = ImpactService.calculate_action_emissions(
        activity_type=ImpactActivityType.PUBLIC_TRANSIT,
        mode=TransportMode.PUBLIC_BUS,
        distance_km=distance_km,
    )

    # Vehicle total: 14 km * 1100.0 g/km = 15400 g = 15.4 kg
    assert v_kg == 15.4
    # Per passenger: 15400 / 35 = 440.0 g = 0.44 kg
    assert p_kg == 0.44
    # Baseline: 14 * 165 g = 2310 g = 2.31 kg
    assert base_kg == 2.31
    # Savings: 2.31 - 0.44 = 1.87 kg
    assert sav_kg == 1.87
    assert "35 pax" in notes


def test_electric_bus_grid_indirect_emissions():
    """Verify that e-Buses account for upstream grid power (859.2 g/vehicle-km) and 35 pax occupancy."""
    distance_km = 10.0

    v_kg, p_kg, base_kg, sav_kg, _ = ImpactService.calculate_action_emissions(
        activity_type=ImpactActivityType.EV_TRANSIT,
        mode=TransportMode.ELECTRIC_BUS,
        distance_km=distance_km,
    )

    # Vehicle: 10 * 859.2 = 8592 g = 8.592 kg
    assert v_kg == 8.592
    # Per passenger: 8592 / 35 = 245.485 g = 0.245 kg
    assert p_kg == 0.245
    # Baseline: 10 * 165 = 1650 g = 1.65 kg
    assert base_kg == 1.65
    # Savings: 1.65 - 0.245 = 1.405 kg
    assert sav_kg == 1.405


def test_carpool_splits_vehicle_emissions_accurately():
    """Verify carpool allocation: 3 passengers sharing a 165 g/km petrol car."""
    distance_km = 20.0

    # 3-person pool
    v_kg, p_kg, base_kg, sav_kg, notes = ImpactService.calculate_action_emissions(
        activity_type=ImpactActivityType.CARPOOL,
        mode=TransportMode.CARPOOL,
        distance_km=distance_km,
        passengers=3,
    )

    # Vehicle total: 20 * 165 = 3300 g = 3.3 kg
    assert v_kg == 3.3
    # Per passenger: 3.3 / 3 = 1.1 kg
    assert p_kg == 1.1
    # Baseline: 20 * 165 = 3.3 kg
    assert base_kg == 3.3
    # Savings: 3.3 - 1.1 = 2.2 kg (exactly 66.7% reduction)
    assert sav_kg == 2.2
    assert "3 passengers" in notes


def test_ev_never_described_as_zero_emissions():
    """Verify Electric Cars reflect upstream Indian grid intensity (107.4 g/km) and never report zero emissions."""
    distance_km = 10.0

    v_kg, p_kg, base_kg, sav_kg, notes = ImpactService.calculate_action_emissions(
        activity_type=ImpactActivityType.EV_TRANSIT,
        mode=TransportMode.ELECTRIC_CAR,
        distance_km=distance_km,
        passengers=1,
    )

    # 10 km * 107.4 g/km = 1074 g = 1.074 kg (NOT zero)
    assert v_kg == 1.074
    assert p_kg == 1.074
    assert p_kg > 0.0
    assert base_kg == 1.65
    assert sav_kg == round(1.65 - 1.074, 3)  # 0.576 kg saved vs petrol car


def test_active_travel_zero_emissions():
    """Verify walking and cycling have zero vehicle and passenger emissions."""
    for mode in (TransportMode.WALKING, TransportMode.CYCLING):
        v_kg, p_kg, base_kg, sav_kg, _ = ImpactService.calculate_action_emissions(
            activity_type=ImpactActivityType.ACTIVE_TRAVEL,
            mode=mode,
            distance_km=5.0,
        )
        assert v_kg == 0.0
        assert p_kg == 0.0
        # Baseline: 5 * 165 = 825 g = 0.825 kg
        assert base_kg == 0.825
        assert sav_kg == 0.825


def test_truthful_indoor_safeguards_zero_co2_claims():
    """STRICT INTEGRITY: Air purifiers and natural ventilation mitigate airborne particulates (PM2.5/PM10),

    and must NEVER claim vehicular CO2 greenhouse gas reductions.
    """
    for indoor_type in (ImpactActivityType.PURIFIER_OPTIMIZED, ImpactActivityType.VENTILATION_TIMED):
        v_kg, p_kg, base_kg, sav_kg, notes = ImpactService.calculate_action_emissions(
            activity_type=indoor_type,
            mode=None,
            distance_km=None,
            exposure_avoided_score=25.0,
        )

        assert v_kg == 0.0
        assert p_kg == 0.0
        assert base_kg == 0.0
        assert sav_kg == 0.0
        assert "do not claim vehicular CO2" in notes


def test_log_create_validation():
    """Verify Pydantic validation rejects transit records missing distance_km."""
    # Transit requires distance_km > 0
    with pytest.raises(ValueError):
        ImpactLogCreate(
            activity_type=ImpactActivityType.COMMUTE,
            mode=TransportMode.PETROL_CAR,
            distance_km=None,
        )

    with pytest.raises(ValueError):
        ImpactLogCreate(
            activity_type=ImpactActivityType.COMMUTE,
            mode=TransportMode.PETROL_CAR,
            distance_km=-5.0,
        )

    # Indoor action does NOT require distance_km
    indoor = ImpactLogCreate(
        activity_type=ImpactActivityType.PURIFIER_OPTIMIZED,
        notes="Living room HEPA run",
    )
    assert indoor.distance_km is None


def test_create_log_record_formatting():
    """Verify create_log_record produces properly structured records with data provenance."""
    # Authenticated user record
    payload = ImpactLogCreate(
        activity_type=ImpactActivityType.PUBLIC_TRANSIT,
        mode=TransportMode.METRO,
        distance_km=12.0,
        notes="To client office",
    )
    record = ImpactService.create_log_record(payload, user_id="user_abc123")

    assert record.user_id == "user_abc123"
    assert record.data_provenance == "modeled_estimate"
    assert record.distance_km == 12.0
    # 12 km * 22.0 = 264 g = 0.264 kg
    assert record.per_passenger_emissions_kg_co2e == 0.264
    # Baseline: 12 * 165 = 1980 g = 1.98 kg
    assert record.baseline_emissions_kg_co2e == 1.98
    assert record.emission_saved_kg_co2e == 1.716
    assert record.activity_date == datetime.utcnow().strftime("%Y-%m-%d")

    # Guest user record
    guest_record = ImpactService.create_log_record(payload, user_id=None)
    assert guest_record.user_id is None
    assert guest_record.data_provenance == "simulated_demo"


def test_timeframe_filtering_and_aggregations():
    """Verify filtering and aggregation across Day, Week, and Month windows."""
    ref_date = date(2026, 11, 19)

    # Create mock records spanning multiple days
    records = [
        ImpactLogRecord(
            log_id="rec_today",
            activity_type=ImpactActivityType.PUBLIC_TRANSIT,
            mode=TransportMode.METRO,
            distance_km=15.0,
            passengers=1,
            per_passenger_emissions_kg_co2e=0.33,
            baseline_emissions_kg_co2e=2.475,
            emission_saved_kg_co2e=2.145,
            activity_date="2026-11-19",  # Today
            recorded_at=datetime.utcnow(),
        ),
        ImpactLogRecord(
            log_id="rec_3_days_ago",
            activity_type=ImpactActivityType.CARPOOL,
            mode=TransportMode.CARPOOL,
            distance_km=18.0,
            passengers=3,
            per_passenger_emissions_kg_co2e=0.99,
            baseline_emissions_kg_co2e=2.97,
            emission_saved_kg_co2e=1.98,
            activity_date="2026-11-16",  # 3 days ago (in Week)
            recorded_at=datetime.utcnow(),
        ),
        ImpactLogRecord(
            log_id="rec_15_days_ago",
            activity_type=ImpactActivityType.PUBLIC_TRANSIT,
            mode=TransportMode.ELECTRIC_BUS,
            distance_km=10.0,
            passengers=35,
            per_passenger_emissions_kg_co2e=0.245,
            baseline_emissions_kg_co2e=1.65,
            emission_saved_kg_co2e=1.405,
            activity_date="2026-11-04",  # 15 days ago (in Month, outside Week)
            recorded_at=datetime.utcnow(),
        ),
    ]

    # 1. Day window (today only)
    day_summary = ImpactService.aggregate_summary(records, TimeframeFilter.DAY, reference_date=ref_date)
    assert day_summary.total_activities_logged == 1
    assert day_summary.total_distance_km == 15.0
    assert day_summary.total_savings_kg_co2e == 2.15
    assert len(day_summary.daily_trends) == 1

    # 2. Week window (today + 3 days ago)
    week_summary = ImpactService.aggregate_summary(records, TimeframeFilter.WEEK, reference_date=ref_date)
    assert week_summary.total_activities_logged == 2
    assert week_summary.total_distance_km == 33.0  # 15 + 18
    assert week_summary.total_emissions_kg_co2e == round(0.33 + 0.99, 2)  # 1.32 kg
    assert week_summary.total_savings_kg_co2e == round(2.145 + 1.98, 2)   # 4.13 kg
    assert len(week_summary.daily_trends) == 7

    # 3. Month window (all 3 records)
    month_summary = ImpactService.aggregate_summary(records, TimeframeFilter.MONTH, reference_date=ref_date)
    assert month_summary.total_activities_logged == 3
    assert month_summary.total_distance_km == 43.0  # 15 + 18 + 10
    assert len(month_summary.daily_trends) == 30

    # Modal split check
    assert len(month_summary.mode_breakdown) == 3
    total_pct = sum(m.distance_share_pct for m in month_summary.mode_breakdown)
    assert round(total_pct, 0) == 100.0


def test_educational_tree_month_equivalent():
    """Verify tree-month indicator is calculated cleanly based on US EPA ~1.75 kg/month benchmark."""
    ref_date = date(2026, 11, 19)

    records = [
        ImpactLogRecord(
            log_id="rec_save",
            activity_type=ImpactActivityType.PUBLIC_TRANSIT,
            mode=TransportMode.METRO,
            distance_km=25.0,
            per_passenger_emissions_kg_co2e=0.55,
            baseline_emissions_kg_co2e=4.125,
            emission_saved_kg_co2e=3.50,  # 3.50 kg saved
            activity_date="2026-11-19",
            recorded_at=datetime.utcnow(),
        )
    ]

    summary = ImpactService.aggregate_summary(records, TimeframeFilter.DAY, reference_date=ref_date)
    # 3.50 kg / 1.75 kg/month = 2.0 tree-months
    assert summary.tree_months_equivalent == 2.0
    assert summary.methodology.tree_monthly_absorption_kg == 1.75
    assert "US EPA GHG Equivalencies" in summary.methodology.tree_source


def test_demo_records_guest_isolation():
    """Verify that demonstration records generated for guest mode are tagged simulated_demo

    and never masquerade as live authenticated user records.
    """
    demo_records = ImpactService.get_demo_records()
    assert len(demo_records) >= 5
    for r in demo_records:
        assert r.user_id is None
        assert r.data_provenance == "simulated_demo"

    summary = ImpactService.aggregate_summary(demo_records, TimeframeFilter.WEEK, is_demo_data=True)
    assert summary.is_demo_data is True
    assert summary.total_activities_logged >= 3
    assert summary.total_savings_kg_co2e > 0.0
