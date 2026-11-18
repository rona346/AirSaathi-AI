"""Real external Weather Service integration using Open-Meteo API.

Provider: Open-Meteo (https://open-meteo.com)
Usage: Free for non-commercial atmospheric telemetry; no API key required.
Attribution: Weather data by Open-Meteo.com

Features:
- Asynchronous and synchronous HTTP clients using httpx with configurable timeouts.
- Dynamic latitude & longitude lookup per monitoring station or user coordinates.
- Pydantic response normalization (WeatherDetail).
- In-memory TTL caching by coordinate grid (rounded to 2 decimal places ~1.1km).
- Graceful fallback to calibrated baseline weather data when network/provider fails.
- Explicit data provenance (source & is_demo_data).
- Separate weather observation timestamp from AQI timestamps.
"""

from datetime import datetime, timezone
import logging
from typing import Any, Dict, Optional, Tuple
import httpx

from backend.app.core.config import settings
from backend.app.models.weather import WeatherDetail

logger = logging.getLogger(__name__)

# WMO Weather interpretation codes (WW)
WMO_CODE_MAP: Dict[int, str] = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snowfall",
    73: "Moderate snowfall",
    75: "Heavy snowfall",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}

CARDINALS = [
    "N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
    "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"
]


def degrees_to_cardinal(deg: Optional[float]) -> str:
    """Convert meteorological wind direction in degrees (0-360) to 16-point cardinal string."""
    if deg is None:
        return "N/A"
    normalized = float(deg) % 360.0
    idx = int((normalized + 11.25) / 22.5) % 16
    return CARDINALS[idx]


def wmo_code_to_condition(code: Optional[int]) -> str:
    """Map WMO numeric weather code to descriptive condition string."""
    if code is None:
        return "Clear"
    return WMO_CODE_MAP.get(int(code), "Clear")


def parse_weather_timestamp(ts_val: Any) -> datetime:
    """Safely parse Open-Meteo ISO timestamp or return current UTC datetime."""
    if not ts_val:
        return datetime.now(timezone.utc)
    if isinstance(ts_val, datetime):
        return ts_val
    try:
        # Open-Meteo returns format like "2026-11-18T16:00"
        dt = datetime.fromisoformat(str(ts_val))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        return datetime.now(timezone.utc)


class WeatherService:
    BASE_URL = "https://api.open-meteo.com/v1/forecast"

    def __init__(self, cache_ttl: Optional[int] = None, timeout_seconds: Optional[float] = None):
        self.cache_ttl = cache_ttl or settings.WEATHER_CACHE_TTL_SECONDS
        self.timeout = timeout_seconds or settings.WEATHER_REQUEST_TIMEOUT_SECONDS
        # Cache key: (round(lat, 2), round(lon, 2)) -> (timestamp, WeatherDetail)
        self._cache: Dict[Tuple[float, float], Tuple[datetime, WeatherDetail]] = {}

    def _get_cache_key(self, latitude: float, longitude: float) -> Tuple[float, float]:
        return (round(latitude, 2), round(longitude, 2))

    def clear_cache(self) -> None:
        """Clear the in-memory weather cache."""
        self._cache.clear()

    def get_cached(self, latitude: float, longitude: float) -> Optional[WeatherDetail]:
        """Return cached WeatherDetail if present and not expired."""
        key = self._get_cache_key(latitude, longitude)
        if key in self._cache:
            cached_at, data = self._cache[key]
            now = datetime.now(timezone.utc)
            if cached_at.tzinfo is None:
                cached_at = cached_at.replace(tzinfo=timezone.utc)
            if (now - cached_at).total_seconds() < self.cache_ttl:
                return data
        return None

    def _set_cache(self, latitude: float, longitude: float, data: WeatherDetail) -> None:
        key = self._get_cache_key(latitude, longitude)
        self._cache[key] = (datetime.now(timezone.utc), data)

    def _estimate_boundary_layer_height(self, hour_utc: int) -> float:
        """
        Estimate atmospheric boundary layer height (in meters) based on diurnal cycle in India.
        Night/early morning nocturnal inversion: ~350 - 450m.
        Mid-afternoon solar convection: ~800 - 1200m.
        """
        ist_hour = (hour_utc + 5) % 24  # UTC to approximate IST
        if 6 <= ist_hour < 10:
            return 380.0
        elif 10 <= ist_hour < 16:
            return 850.0
        elif 16 <= ist_hour < 19:
            return 600.0
        else:
            return 420.0

    def _estimate_visibility(self, condition: str, humidity: float, precip: float) -> float:
        """Estimate visibility in km based on humidity, weather condition and rain."""
        if precip > 5.0 or "fog" in condition.lower():
            return 1.2
        elif humidity > 85.0:
            return 1.8
        elif humidity > 70.0:
            return 2.5
        elif humidity < 40.0:
            return 5.5
        return 3.5

    def get_calibrated_demo_weather(
        self,
        latitude: float,
        longitude: float,
        station_id: Optional[str] = None,
        station_name: Optional[str] = None,
        reason: str = "Simulated Baseline",
    ) -> WeatherDetail:
        """
        Produce a calibrated demo weather baseline specific to location coordinates.
        Always tagged with is_demo_data=True and clear source provenance.
        """
        now = datetime.now(timezone.utc)
        sid = (station_id or "").lower()

        # Regional micro-climates for major Indian monitoring corridors
        if "delhi" in sid or "noida" in sid or "gurugram" in sid or (27.5 <= latitude <= 29.5 and 76.5 <= longitude <= 78.0):
            temp = 19.5
            humidity = 74.0
            wind_speed = 4.2
            wind_deg = 315.0
            condition = "Hazy"
            visibility = 1.4
            mixing_layer = 420.0
        elif "udaipur" in sid or (24.0 <= latitude <= 25.5 and 73.0 <= longitude <= 74.5):
            temp = 24.5
            humidity = 42.0
            wind_speed = 6.8
            wind_deg = 290.0
            condition = "Dry & Sunny"
            visibility = 4.2
            mixing_layer = 650.0
        elif "mumbai" in sid or (18.5 <= latitude <= 19.5 and 72.5 <= longitude <= 73.5):
            temp = 28.5
            humidity = 78.0
            wind_speed = 11.2
            wind_deg = 245.0
            condition = "Humid"
            visibility = 3.2
            mixing_layer = 780.0
        elif "bengaluru" in sid or (12.5 <= latitude <= 13.5 and 77.0 <= longitude <= 78.0):
            temp = 22.0
            humidity = 58.0
            wind_speed = 8.4
            wind_deg = 90.0
            condition = "Pleasant"
            visibility = 5.0
            mixing_layer = 720.0
        else:
            temp = 22.5
            humidity = 60.0
            wind_speed = 5.0
            wind_deg = 315.0
            condition = "Clear"
            visibility = 3.0
            mixing_layer = 500.0

        return WeatherDetail(
            temperature_c=temp,
            humidity_percent=humidity,
            wind_speed_kmh=wind_speed,
            wind_direction=degrees_to_cardinal(wind_deg),
            wind_direction_deg=wind_deg,
            precipitation_mm=0.0,
            weather_condition=condition,
            visibility_km=visibility,
            mixing_layer_height_m=mixing_layer,
            observed_at=now,
            source=f"Demonstration Baseline ({reason})",
            is_demo_data=True,
        )

    def normalize_provider_response(
        self,
        raw_json: Dict[str, Any],
        latitude: float,
        longitude: float,
    ) -> WeatherDetail:
        """Parse and validate Open-Meteo response into WeatherDetail."""
        current = raw_json.get("current", {})
        if not current:
            raise ValueError("Open-Meteo payload missing 'current' block")

        # Parse required numerical fields with safe defaults for missing optional attributes
        temp_val = current.get("temperature_2m")
        humidity_val = current.get("relative_humidity_2m")
        wind_speed_val = current.get("wind_speed_10m")

        if temp_val is None or humidity_val is None or wind_speed_val is None:
            raise ValueError("Open-Meteo payload missing fundamental telemetry (temp, humidity, or wind speed)")

        temp_c = float(temp_val)
        humidity_pct = float(humidity_val)
        wind_spd = float(wind_speed_val)

        wind_deg_val = current.get("wind_direction_10m")
        wind_deg = float(wind_deg_val) if wind_deg_val is not None else None
        wind_cardinal = degrees_to_cardinal(wind_deg)

        precip_val = current.get("precipitation")
        precip_mm = float(precip_val) if precip_val is not None else 0.0

        weather_code = current.get("weather_code")
        condition = wmo_code_to_condition(weather_code)

        observed_at = parse_weather_timestamp(current.get("time"))

        # Estimated dispersion metrics for ambient air quality context
        visibility = self._estimate_visibility(condition, humidity_pct, precip_mm)
        mixing_layer = self._estimate_boundary_layer_height(observed_at.hour)

        return WeatherDetail(
            temperature_c=temp_c,
            humidity_percent=humidity_pct,
            wind_speed_kmh=wind_spd,
            wind_direction=wind_cardinal,
            wind_direction_deg=wind_deg,
            precipitation_mm=precip_mm,
            weather_condition=condition,
            visibility_km=visibility,
            mixing_layer_height_m=mixing_layer,
            observed_at=observed_at,
            source="Open-Meteo",
            is_demo_data=False,
        )

    def _build_request_params(self, latitude: float, longitude: float) -> Dict[str, Any]:
        return {
            "latitude": round(latitude, 4),
            "longitude": round(longitude, 4),
            "current": "temperature_2m,relative_humidity_2m,precipitation,weather_code,wind_speed_10m,wind_direction_10m",
            "wind_speed_unit": "kmh",
            "timezone": "auto",
        }

    async def get_weather(
        self,
        latitude: float,
        longitude: float,
        station_id: Optional[str] = None,
        station_name: Optional[str] = None,
    ) -> WeatherDetail:
        """
        Asynchronously retrieve weather telemetry for given coordinates.
        1. Checks TTL cache.
        2. Queries Open-Meteo API with asynchronous httpx client.
        3. On error or timeout, gracefully falls back to calibrated demo baseline.
        """
        cached = self.get_cached(latitude, longitude)
        if cached:
            return cached

        if settings.MOCK_MODE:
            demo_data = self.get_calibrated_demo_weather(
                latitude, longitude, station_id, station_name, reason="Mock Mode Active"
            )
            self._set_cache(latitude, longitude, demo_data)
            return demo_data

        params = self._build_request_params(latitude, longitude)
        headers = {"User-Agent": "AirSaathi-AI/1.0", "Accept": "application/json"}

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                res = await client.get(self.BASE_URL, params=params, headers=headers)
                if res.status_code == 200:
                    payload = res.json()
                    weather = self.normalize_provider_response(payload, latitude, longitude)
                    self._set_cache(latitude, longitude, weather)
                    return weather
                else:
                    logger.warning(
                        f"Open-Meteo returned HTTP {res.status_code} for ({latitude}, {longitude}). Falling back to calibrated baseline."
                    )
        except httpx.TimeoutException:
            logger.warning(
                f"Open-Meteo API request timed out after {self.timeout}s for ({latitude}, {longitude}). Falling back to calibrated baseline."
            )
        except httpx.RequestError as exc:
            logger.warning(
                f"Open-Meteo network connectivity error for ({latitude}, {longitude}): {exc}. Falling back to calibrated baseline."
            )
        except Exception as exc:
            logger.warning(
                f"Unexpected error processing Open-Meteo response for ({latitude}, {longitude}): {exc}. Falling back to calibrated baseline."
            )

        demo_weather = self.get_calibrated_demo_weather(
            latitude, longitude, station_id, station_name, reason="Open-Meteo Offline"
        )
        self._set_cache(latitude, longitude, demo_weather)
        return demo_weather

    def get_weather_sync(
        self,
        latitude: float,
        longitude: float,
        station_id: Optional[str] = None,
        station_name: Optional[str] = None,
    ) -> WeatherDetail:
        """
        Synchronous counterpart to get_weather for synchronous contexts.
        Uses synchronous httpx.Client with exact same caching and graceful fallback.
        """
        cached = self.get_cached(latitude, longitude)
        if cached:
            return cached

        if settings.MOCK_MODE:
            demo_data = self.get_calibrated_demo_weather(
                latitude, longitude, station_id, station_name, reason="Mock Mode Active"
            )
            self._set_cache(latitude, longitude, demo_data)
            return demo_data

        params = self._build_request_params(latitude, longitude)
        headers = {"User-Agent": "AirSaathi-AI/1.0", "Accept": "application/json"}

        try:
            with httpx.Client(timeout=self.timeout) as client:
                res = client.get(self.BASE_URL, params=params, headers=headers)
                if res.status_code == 200:
                    payload = res.json()
                    weather = self.normalize_provider_response(payload, latitude, longitude)
                    self._set_cache(latitude, longitude, weather)
                    return weather
                else:
                    logger.warning(
                        f"Open-Meteo sync returned HTTP {res.status_code} for ({latitude}, {longitude}). Falling back to calibrated baseline."
                    )
        except httpx.TimeoutException:
            logger.warning(
                f"Open-Meteo sync API request timed out after {self.timeout}s for ({latitude}, {longitude}). Falling back to calibrated baseline."
            )
        except httpx.RequestError as exc:
            logger.warning(
                f"Open-Meteo sync network connectivity error for ({latitude}, {longitude}): {exc}. Falling back to calibrated baseline."
            )
        except Exception as exc:
            logger.warning(
                f"Unexpected error processing Open-Meteo sync response for ({latitude}, {longitude}): {exc}. Falling back to calibrated baseline."
            )

        demo_weather = self.get_calibrated_demo_weather(
            latitude, longitude, station_id, station_name, reason="Open-Meteo Offline"
        )
        self._set_cache(latitude, longitude, demo_weather)
        return demo_weather


# Global default instance
weather_service = WeatherService()
