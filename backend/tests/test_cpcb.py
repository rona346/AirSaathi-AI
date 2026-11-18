import pytest
from backend.app.models.aqi import AqiCategory
from backend.app.services.cpcb_calculator import (
    calculate_subindex,
    calculate_concentration_for_subindex,
    calculate_overall_aqi,
    get_aqi_category_from_value,
)


def test_aqi_category_breakpoints():
    assert get_aqi_category_from_value(0) == AqiCategory.GOOD
    assert get_aqi_category_from_value(50) == AqiCategory.GOOD
    assert get_aqi_category_from_value(51) == AqiCategory.SATISFACTORY
    assert get_aqi_category_from_value(100) == AqiCategory.SATISFACTORY
    assert get_aqi_category_from_value(101) == AqiCategory.MODERATE
    assert get_aqi_category_from_value(200) == AqiCategory.MODERATE
    assert get_aqi_category_from_value(201) == AqiCategory.POOR
    assert get_aqi_category_from_value(300) == AqiCategory.POOR
    assert get_aqi_category_from_value(301) == AqiCategory.VERY_POOR
    assert get_aqi_category_from_value(400) == AqiCategory.VERY_POOR
    assert get_aqi_category_from_value(401) == AqiCategory.SEVERE
    assert get_aqi_category_from_value(500) == AqiCategory.SEVERE
    assert get_aqi_category_from_value(501) == AqiCategory.SEVERE_PLUS


def test_pm25_subindex_calculation():
    # PM2.5 Good: 0-30 -> 0-50
    assert 0 <= calculate_subindex("PM2.5", 15.0) <= 50
    assert calculate_subindex("PM2.5", 30.0) == 50

    # PM2.5 Satisfactory: 30-60 -> 51-100
    assert 51 <= calculate_subindex("PM2.5", 45.0) <= 100
    assert calculate_subindex("PM2.5", 60.0) == 100

    # PM2.5 Moderate: 60-90 -> 101-200
    assert 101 <= calculate_subindex("PM2.5", 75.0) <= 200
    assert calculate_subindex("PM2.5", 90.0) == 200

    # PM2.5 Poor: 90-120 -> 201-300
    assert 201 <= calculate_subindex("PM2.5", 105.0) <= 300
    assert calculate_subindex("PM2.5", 120.0) == 300

    # PM2.5 Very Poor: 120-250 -> 301-400
    sub = calculate_subindex("PM2.5", 208.0)
    assert sub == 368
    assert calculate_subindex("PM2.5", 250.0) == 400

    # PM2.5 Severe: 250-380 -> 401-500
    assert 401 <= calculate_subindex("PM2.5", 300.0) <= 500


def test_pm10_subindex_calculation():
    # PM10 Good: 0-50 -> 0-50
    assert calculate_subindex("PM10", 25.0) == 25
    assert calculate_subindex("PM10", 50.0) == 50

    # PM10 Moderate: 100-250 -> 101-200
    assert 101 <= calculate_subindex("PM10", 175.0) <= 200

    # PM10 Very Poor: 350-430 -> 301-400
    assert 301 <= calculate_subindex("PM10", 375.0) <= 400


def test_co_and_no2_subindices():
    # CO Good: 0-1.0 -> 0-50
    assert calculate_subindex("CO", 0.5) == 25
    # NO2 Satisfactory: 40-80 -> 51-100
    assert 51 <= calculate_subindex("NO2", 60.0) <= 100


def test_inverse_concentration_calculation():
    # Target 368 on PM2.5 should yield approx 208.0 ug/m3
    conc = calculate_concentration_for_subindex("PM2.5", 368)
    assert 205.0 <= conc <= 210.0
    # Recalculating subindex from this concentration should match 368
    recalc_sub = calculate_subindex("PM2.5", conc)
    assert abs(recalc_sub - 368) <= 1


def test_overall_aqi_and_prominent_pollutant():
    concentrations = {
        "PM2.5": 208.0,  # sub-index ~368 (Very Poor)
        "PM10": 180.0,   # sub-index ~153 (Moderate)
        "NO2": 55.0,     # sub-index ~69 (Satisfactory)
        "SO2": 20.0,     # sub-index ~25 (Good)
        "CO": 1.2,       # sub-index ~60 (Satisfactory)
        "O3": 40.0,      # sub-index ~40 (Good)
    }
    overall_aqi, prominent, sub_indices = calculate_overall_aqi(concentrations)
    assert overall_aqi == 368
    assert prominent == "PM2.5"
    assert sub_indices["PM2.5"] == 368
    assert sub_indices["PM10"] < overall_aqi
