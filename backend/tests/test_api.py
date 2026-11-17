import pytest
from backend.app.api.v1.endpoints.health import check_health
from backend.app.api.v1.endpoints.aqi import list_stations, get_current_aqi, get_forecast
from backend.app.services.aqi_service import AqiService, get_aqi_category


def test_aqi_category_logic():
    assert get_aqi_category(45).value == "Good"
    assert get_aqi_category(85).value == "Satisfactory"
    assert get_aqi_category(150).value == "Moderate"
    assert get_aqi_category(250).value == "Poor"
    assert get_aqi_category(350).value == "Very Poor"
    assert get_aqi_category(450).value == "Severe"
    assert get_aqi_category(520).value == "Severe+"


def test_health_endpoint():
    res = check_health()
    assert res.success is True
    assert res.data["status"] == "online"
    assert res.data["service"] == "AirSaathi AI Backend"
    assert res.is_demo_data is False


def test_stations_endpoint():
    res = list_stations()
    assert res.success is True
    assert len(res.data) >= 5
    station_names = [s.name for s in res.data]
    assert "Anand Vihar" in station_names
    assert "Punjabi Bagh" in station_names


def test_current_aqi_endpoint():
    res = get_current_aqi("delhi-anand-vihar")
    assert res.success is True
    data = res.data
    assert data.station.name == "Anand Vihar"
    assert data.aqi == 368
    assert data.category.value == "Very Poor"
    assert "PM2.5" in data.pollutants
    assert data.pollutants["PM2.5"].value > 0
    assert data.is_demo_data is True
    assert "Central Pollution Control Board" in data.data_source


def test_forecast_endpoint():
    res = get_forecast("delhi-anand-vihar")
    assert res.success is True
    forecast = res.data
    assert len(forecast.forecast_24h) == 24
    assert forecast.station_name == "Anand Vihar"
    assert "06:00 AM" in forecast.peak_aqi_window
    assert forecast.is_demo_data is True
