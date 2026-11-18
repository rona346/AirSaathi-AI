import pytest
from datetime import datetime
from backend.app.models.aqi import StationInfo
from backend.app.services.live_aqi_provider import (
    DataGovInProvider,
    normalize_pollutant_name,
    parse_cpcb_timestamp,
    get_active_aqi_provider,
)

SAMPLE_STATION = StationInfo(
    id="delhi-anand-vihar",
    name="Anand Vihar",
    city="Delhi",
    state="Delhi",
    latitude=28.6508,
    longitude=77.3152,
    is_hotspot=True,
)

SAMPLE_7_POLLUTANTS_FIXTURE = [
    {
        "country": "India",
        "state": "Delhi",
        "city": "Delhi",
        "station": "Anand Vihar, Delhi - DPCC",
        "last_update": "18-11-2026 15:00:00",
        "latitude": "28.6508",
        "longitude": "77.3152",
        "pollutant_id": "NH3",
        "min_value": "2",
        "max_value": "5",
        "avg_value": "3",
    },
    {
        "country": "India",
        "state": "Delhi",
        "city": "Delhi",
        "station": "Anand Vihar, Delhi - DPCC",
        "last_update": "18-11-2026 15:00:00",
        "latitude": "28.6508",
        "longitude": "77.3152",
        "pollutant_id": "PM2.5",
        "min_value": "59",
        "max_value": "391",
        "avg_value": "222",
    },
    {
        "country": "India",
        "state": "Delhi",
        "city": "Delhi",
        "station": "Anand Vihar, Delhi - DPCC",
        "last_update": "18-11-2026 15:00:00",
        "latitude": "28.6508",
        "longitude": "77.3152",
        "pollutant_id": "SO2",
        "min_value": "14",
        "max_value": "66",
        "avg_value": "40",
    },
    {
        "country": "India",
        "state": "Delhi",
        "city": "Delhi",
        "station": "Anand Vihar, Delhi - DPCC",
        "last_update": "18-11-2026 15:00:00",
        "latitude": "28.6508",
        "longitude": "77.3152",
        "pollutant_id": "PM10",
        "min_value": "77",
        "max_value": "285",
        "avg_value": "207",
    },
    {
        "country": "India",
        "state": "Delhi",
        "city": "Delhi",
        "station": "Anand Vihar, Delhi - DPCC",
        "last_update": "18-11-2026 15:00:00",
        "latitude": "28.6508",
        "longitude": "77.3152",
        "pollutant_id": "NO2",
        "min_value": "25",
        "max_value": "71",
        "avg_value": "46",
    },
    {
        "country": "India",
        "state": "Delhi",
        "city": "Delhi",
        "station": "Anand Vihar, Delhi - DPCC",
        "last_update": "18-11-2026 15:00:00",
        "latitude": "28.6508",
        "longitude": "77.3152",
        "pollutant_id": "CO",
        "min_value": "97",
        "max_value": "154",
        "avg_value": "25",
    },
    {
        "country": "India",
        "state": "Delhi",
        "city": "Delhi",
        "station": "Anand Vihar, Delhi - DPCC",
        "last_update": "18-11-2026 15:00:00",
        "latitude": "28.6508",
        "longitude": "77.3152",
        "pollutant_id": "OZONE",
        "min_value": "5",
        "max_value": "56",
        "avg_value": "30",
    },
]


def test_timestamp_parser():
    dt = parse_cpcb_timestamp("18-11-2026 15:00:00")
    assert dt.day == 18
    assert dt.month == 11
    assert dt.year == 2026
    assert dt.hour == 15
    assert dt.minute == 0


def test_pollutant_normalization():
    assert normalize_pollutant_name("OZONE") == "O3"
    assert normalize_pollutant_name("ozone") == "O3"
    assert normalize_pollutant_name("PM2.5") == "PM2.5"
    assert normalize_pollutant_name("pm10") == "PM10"


def test_parse_records_full_cpcb():
    provider = DataGovInProvider("dummy-key")
    res = provider.parse_records(SAMPLE_7_POLLUTANTS_FIXTURE, SAMPLE_STATION)

    assert res is not None
    assert res.is_demo_data is False
    assert "data.gov.in" in res.data_source
    assert res.station.id == "delhi-anand-vihar"
    assert res.prominent_pollutant == "PM2.5"
    # PM2.5 avg is 222 -> subindex is 379 (Very Poor)
    assert res.aqi == 379
    assert res.category.value == "Very Poor"
    assert "PM2.5" in res.pollutants
    assert "PM10" in res.pollutants
    assert "O3" in res.pollutants
    assert res.pollutants["PM2.5"].value == 222.0
    assert res.pollutants["PM2.5"].sub_index == 379
    assert res.last_updated.year == 2026


def test_reject_single_pollutant_alone():
    provider = DataGovInProvider("dummy-key")
    single_pol = [SAMPLE_7_POLLUTANTS_FIXTURE[1]]  # Only PM2.5
    res = provider.parse_records(single_pol, SAMPLE_STATION)
    # Must reject overall AQI calculation from one pollutant alone
    assert res is None


def test_reject_without_particulates():
    provider = DataGovInProvider("dummy-key")
    no_pm = [
        SAMPLE_7_POLLUTANTS_FIXTURE[0],  # NH3
        SAMPLE_7_POLLUTANTS_FIXTURE[2],  # SO2
        SAMPLE_7_POLLUTANTS_FIXTURE[4],  # NO2
    ]
    res = provider.parse_records(no_pm, SAMPLE_STATION)
    # CPCB requires PM2.5 or PM10
    assert res is None


def test_handle_na_and_missing_pollutant_values():
    provider = DataGovInProvider("dummy-key")
    dirty_fixture = [
        {
            "station": "Anand Vihar, Delhi - DPCC",
            "pollutant_id": "PM2.5",
            "avg_value": "NA",
            "max_value": "222",
            "last_update": "18-11-2026 15:00:00",
        },
        {
            "station": "Anand Vihar, Delhi - DPCC",
            "pollutant_id": "PM10",
            "avg_value": "207",
            "max_value": "285",
            "last_update": "18-11-2026 15:00:00",
        },
        {
            "station": "Anand Vihar, Delhi - DPCC",
            "pollutant_id": "NO2",
            "avg_value": "null",
            "max_value": "NA",
            "last_update": "18-11-2026 15:00:00",
        },
        {
            "station": "Anand Vihar, Delhi - DPCC",
            "pollutant_id": "SO2",
            "avg_value": "40",
            "last_update": "18-11-2026 15:00:00",
        },
    ]
    res = provider.parse_records(dirty_fixture, SAMPLE_STATION)
    assert res is not None
    # 3 valid pollutants: PM2.5 (from max_value fallback), PM10, SO2
    assert "PM2.5" in res.pollutants
    assert "PM10" in res.pollutants
    assert "SO2" in res.pollutants
    assert "NO2" not in res.pollutants


def test_provider_caching():
    provider = DataGovInProvider("dummy-key", cache_ttl=300)
    # Pre-populate cache
    dummy_res = provider.parse_records(SAMPLE_7_POLLUTANTS_FIXTURE, SAMPLE_STATION)
    provider._cache[SAMPLE_STATION.id] = (datetime.utcnow(), dummy_res)

    # Calling get_current_aqi should return cached without HTTP call
    retrieved = provider.get_current_aqi(SAMPLE_STATION.id)
    assert retrieved.aqi == dummy_res.aqi
    assert retrieved.is_demo_data is False


def test_provider_error_fallback():
    # Invalid key that causes HTTP 400
    provider = DataGovInProvider("invalid-key-xyz")
    # Calling get_current_aqi falls back gracefully to calibrated baseline
    res = provider.get_current_aqi(SAMPLE_STATION.id)
    assert res is not None
    assert res.is_demo_data is True
    assert "Mock Baseline" in res.data_source
