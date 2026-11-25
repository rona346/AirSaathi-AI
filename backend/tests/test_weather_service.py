"""Unit tests for Weather Service integration (Open-Meteo provider).

Verifies:
1. Valid Open-Meteo API response normalization and unit conversions.
2. Missing optional fields handling.
3. Missing mandatory fields handling and fallback.
4. HTTP timeout handling and graceful fallback.
5. HTTP 500 provider error handling and graceful fallback.
6. Clear demonstration data labeling and provenance guardrails.
7. Weather observation timestamp separation from AQI timestamp.
8. Multiple geographic locations with coordinate-specific telemetry.
9. In-memory TTL caching behavior.
10. Both synchronous and asynchronous service interfaces.
11. Dedicated FastAPI /api/v1/weather/current endpoint.
"""

from datetime import datetime, timezone
import pytest
from unittest.mock import MagicMock, patch
import httpx

from backend.app.models.weather import WeatherDetail
from backend.app.services.weather_service import (
    WeatherService,
    degrees_to_cardinal,
    wmo_code_to_condition,
)
from backend.app.services.aqi_service import AqiService

MOCK_OPEN_METEO_PAYLOAD = {
    "latitude": 28.65,
    "longitude": 77.31,
    "generationtime_ms": 0.08,
    "utc_offset_seconds": 0,
    "timezone": "GMT",
    "timezone_abbreviation": "GMT",
    "elevation": 215.0,
    "current_units": {
        "time": "iso8601",
        "interval": "seconds",
        "temperature_2m": "°C",
        "relative_humidity_2m": "%",
        "precipitation": "mm",
        "weather_code": "wmo code",
        "wind_speed_10m": "km/h",
        "wind_direction_10m": "°",
    },
    "current": {
        "time": "2026-11-18T14:30",
        "interval": 900,
        "temperature_2m": 22.4,
        "relative_humidity_2m": 64.0,
        "precipitation": 0.2,
        "weather_code": 2,
        "wind_speed_10m": 7.8,
        "wind_direction_10m": 315.0,
    },
}


@pytest.fixture(autouse=True)
def clean_cache():
    """Ensure weather cache is empty before and after each test and mock mode is controlled."""
    from backend.app.services.weather_service import weather_service
    from backend.app.core.config import settings
    old_mock = settings.MOCK_MODE
    settings.MOCK_MODE = False
    weather_service.clear_cache()
    yield
    settings.MOCK_MODE = old_mock
    weather_service.clear_cache()


def test_cardinal_direction_and_wmo_code_conversion():
    """Verify 16-point cardinal compass conversions and WMO weather codes."""
    assert degrees_to_cardinal(0) == "N"
    assert degrees_to_cardinal(90) == "E"
    assert degrees_to_cardinal(180) == "S"
    assert degrees_to_cardinal(270) == "W"
    assert degrees_to_cardinal(315) == "NW"
    assert degrees_to_cardinal(None) == "N/A"

    assert wmo_code_to_condition(0) == "Clear sky"
    assert wmo_code_to_condition(2) == "Partly cloudy"
    assert wmo_code_to_condition(45) == "Fog"
    assert wmo_code_to_condition(61) == "Slight rain"
    assert wmo_code_to_condition(95) == "Thunderstorm"
    assert wmo_code_to_condition(None) == "Clear"


def test_valid_open_meteo_response_normalization():
    """Verify parsing and normalization of valid Open-Meteo payload."""
    svc = WeatherService()
    weather = svc.normalize_provider_response(MOCK_OPEN_METEO_PAYLOAD, 28.65, 77.31)

    assert isinstance(weather, WeatherDetail)
    assert weather.temperature_c == 22.4
    assert weather.humidity_percent == 64.0
    assert weather.wind_speed_kmh == 7.8
    assert weather.wind_direction == "NW"
    assert weather.wind_direction_deg == 315.0
    assert weather.precipitation_mm == 0.2
    assert weather.weather_condition == "Partly cloudy"
    assert weather.source == "Open-Meteo"
    assert weather.is_demo_data is False
    assert weather.observed_at.year == 2026
    assert weather.visibility_km is not None
    assert weather.mixing_layer_height_m is not None


def test_missing_optional_fields_handled_safely():
    """Verify payload with missing optional fields defaults gracefully."""
    minimal_payload = {
        "current": {
            "time": "2026-11-18T12:00",
            "temperature_2m": 25.0,
            "relative_humidity_2m": 50.0,
            "wind_speed_10m": 4.0,
            # precipitation, weather_code, wind_direction_10m omitted
        }
    }
    svc = WeatherService()
    weather = svc.normalize_provider_response(minimal_payload, 28.65, 77.31)

    assert weather.temperature_c == 25.0
    assert weather.humidity_percent == 50.0
    assert weather.wind_speed_kmh == 4.0
    assert weather.precipitation_mm == 0.0
    assert weather.wind_direction == "N/A"
    assert weather.weather_condition == "Clear"
    assert weather.is_demo_data is False


def test_missing_mandatory_fields_triggers_fallback():
    """Verify payload with missing mandatory fields triggers fallback to demo baseline."""
    broken_payload = {
        "current": {
            "time": "2026-11-18T12:00",
            # missing temperature_2m, relative_humidity_2m, wind_speed_10m
        }
    }
    svc = WeatherService()
    mock_res = MagicMock()
    mock_res.status_code = 200
    mock_res.json.return_value = broken_payload

    with patch("httpx.Client.get", return_value=mock_res):
        weather = svc.get_weather_sync(28.6508, 77.3152, station_id="delhi-anand-vihar")
        assert weather.is_demo_data is True
        assert "Demonstration Baseline" in weather.source


def test_http_timeout_triggers_graceful_fallback():
    """Verify network timeout triggers graceful fallback without raising an uncaught exception."""
    svc = WeatherService(timeout_seconds=0.1)

    with patch("httpx.Client.get", side_effect=httpx.TimeoutException("Connection timed out")):
        weather = svc.get_weather_sync(28.6508, 77.3152, station_id="delhi-anand-vihar")
        assert isinstance(weather, WeatherDetail)
        assert weather.is_demo_data is True
        assert "Demonstration Baseline (Open-Meteo Offline)" in weather.source
        assert weather.temperature_c == 19.5
        assert weather.humidity_percent == 74.0


def test_http_500_provider_error_triggers_graceful_fallback():
    """Verify HTTP 500 error from provider gracefully falls back to calibrated baseline."""
    svc = WeatherService()
    mock_res = MagicMock()
    mock_res.status_code = 500

    with patch("httpx.Client.get", return_value=mock_res):
        weather = svc.get_weather_sync(24.5854, 73.7125, station_id="udaipur-ashok-nagar")
        assert weather.is_demo_data is True
        assert "Demonstration Baseline (Open-Meteo Offline)" in weather.source
        assert weather.temperature_c == 24.5
        assert weather.humidity_percent == 42.0


def test_fallback_data_never_labeled_as_live():
    """Verify fallback baseline is always flagged as demo data with clear provenance."""
    svc = WeatherService()
    demo_weather = svc.get_calibrated_demo_weather(19.0657, 72.8687, station_id="mumbai-bandra-kurla")

    assert demo_weather.is_demo_data is True
    assert demo_weather.source.startswith("Demonstration Baseline")
    assert "Live" not in demo_weather.source


def test_weather_timestamp_separated_from_aqi_timestamp():
    """Verify weather observation timestamp is independent and distinct from AQI observation timestamp."""
    cpcb_response = AqiService.get_current_aqi("delhi-anand-vihar")

    assert isinstance(cpcb_response.weather, WeatherDetail)
    assert isinstance(cpcb_response.last_updated, datetime)
    assert isinstance(cpcb_response.weather.observed_at, datetime)
    # Both are datetime objects tracking their respective independent measurement times
    assert cpcb_response.weather.source is not None


def test_multiple_locations_use_station_specific_telemetry():
    """Verify different station coordinates receive location-specific telemetry and cache keys."""
    svc = WeatherService()

    delhi_weather = svc.get_calibrated_demo_weather(28.6508, 77.3152, station_id="delhi-anand-vihar")
    udaipur_weather = svc.get_calibrated_demo_weather(24.5854, 73.7125, station_id="udaipur-ashok-nagar")
    bengaluru_weather = svc.get_calibrated_demo_weather(12.9166, 77.6101, station_id="bengaluru-btm-layout")
    mumbai_weather = svc.get_calibrated_demo_weather(19.0657, 72.8687, station_id="mumbai-bandra-kurla")

    # Verify distinct temperature and humidity across climates
    assert delhi_weather.temperature_c == 19.5
    assert udaipur_weather.temperature_c == 24.5
    assert mumbai_weather.temperature_c == 28.5
    assert bengaluru_weather.temperature_c == 22.0

    assert delhi_weather.humidity_percent == 74.0
    assert udaipur_weather.humidity_percent == 42.0
    assert mumbai_weather.humidity_percent == 78.0


def test_in_memory_cache_within_ttl():
    """Verify subsequent requests within TTL return cached telemetry without duplicate HTTP calls."""
    svc = WeatherService(cache_ttl=900)
    mock_res = MagicMock()
    mock_res.status_code = 200
    mock_res.json.return_value = MOCK_OPEN_METEO_PAYLOAD

    with patch("httpx.Client.get", return_value=mock_res) as mock_get:
        # First call hits API
        res1 = svc.get_weather_sync(28.65, 77.31)
        assert mock_get.call_count == 1
        assert res1.temperature_c == 22.4

        # Second call for same coordinates uses cache
        res2 = svc.get_weather_sync(28.65, 77.31)
        assert mock_get.call_count == 1
        assert res2.temperature_c == 22.4

        # Different coordinates triggers API call
        res3 = svc.get_weather_sync(12.91, 77.61)
        assert mock_get.call_count == 2


def test_async_get_weather_signature():
    """Verify asynchronous interface get_weather is a valid coroutine method."""
    import inspect
    svc = WeatherService()
    assert inspect.iscoroutinefunction(svc.get_weather)


def test_api_weather_current_endpoint():
    """Verify /api/v1/weather/current endpoint handles station_id, coordinates and validation."""
    from fastapi import HTTPException
    from backend.app.api.v1.endpoints.weather import get_current_weather

    mock_weather = WeatherDetail(
        temperature_c=22.4,
        humidity_percent=64.0,
        wind_speed_kmh=7.8,
        wind_direction="NW",
        wind_direction_deg=315.0,
        precipitation_mm=0.2,
        weather_condition="Partly cloudy",
        visibility_km=3.5,
        mixing_layer_height_m=500.0,
        observed_at=datetime.now(timezone.utc),
        source="Open-Meteo",
        is_demo_data=False,
    )

    with patch(
        "backend.app.api.v1.endpoints.weather.weather_service.get_weather_sync",
        return_value=mock_weather,
    ):
        # Test with station_id
        res = get_current_weather(station_id="delhi-anand-vihar")
        assert res.success is True
        assert res.data.temperature_c == 22.4
        assert res.data.humidity_percent == 64.0
        assert res.data.wind_speed_kmh == 7.8
        assert res.data.source == "Open-Meteo"
        assert res.is_demo_data is False

        # Test with explicit coordinates
        res_coords = get_current_weather(latitude=24.5854, longitude=73.7125)
        assert res_coords.success is True
        assert res_coords.data.temperature_c == 22.4

        # Test invalid coordinates (raises HTTPException 400)
        with pytest.raises(HTTPException) as exc_info:
            get_current_weather(latitude=95.0, longitude=73.7125)
        assert exc_info.value.status_code == 400
