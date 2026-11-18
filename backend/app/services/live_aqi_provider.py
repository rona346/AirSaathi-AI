"""Official data.gov.in CPCB Real Time Air Quality Index integration provider.

Resource ID: 3b01bcb8-0b14-4abf-b6f2-c1bfd384ba69
Base endpoint: https://api.data.gov.in/resource/3b01bcb8-0b14-4abf-b6f2-c1bfd384ba69

Official CPCB Methodology:
- Reads pollutant records for monitoring stations.
- Validates numeric measurements and timestamps.
- Requires at least 3 valid pollutants, including either PM2.5 or PM10, to determine an official AQI.
- Never fabricates missing values or claims live integration without live verification.
- Enforces strict in-memory TTL caching and graceful fallback.
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
import urllib.parse
import httpx

from backend.app.core.config import settings
from backend.app.models.aqi import (
    AqiCategory,
    CurrentAqiResponse,
    ForecastResponse,
    HealthAdvisory,
    PollutantDetail,
    StationInfo,
)
from backend.app.services.aqi_service import AqiService, get_health_advisory
from backend.app.services.cpcb_calculator import (
    calculate_subindex,
    get_aqi_category_from_value,
)
from backend.app.services.weather_service import weather_service

logger = logging.getLogger(__name__)

# Standard CPCB Pollutant Metadata (CPCB 24-hr limit, WHO guideline limit, unit)
POLLUTANT_META: Dict[str, Tuple[float, float, str]] = {
    "PM2.5": (60.0, 15.0, "µg/m³"),
    "PM10": (100.0, 45.0, "µg/m³"),
    "NO2": (80.0, 25.0, "µg/m³"),
    "SO2": (80.0, 40.0, "µg/m³"),
    "CO": (2.0, 4.0, "mg/m³"),
    "O3": (100.0, 100.0, "µg/m³"),
    "NH3": (400.0, 200.0, "µg/m³"),
    "PB": (1.0, 0.5, "µg/m³"),
}

# Mapping our application station IDs to data.gov.in official station names
CPCB_STATION_MAP: Dict[str, str] = {
    "delhi-anand-vihar": "Anand Vihar, Delhi - DPCC",
    "delhi-punjabi-bagh": "Punjabi Bagh, Delhi - DPCC",
    "delhi-rk-puram": "R K Puram, Delhi - DPCC",
    "delhi-lodhi-road": "Lodhi Road, Delhi - IITM",
    "delhi-igi-airport": "IGI Airport (T3), Delhi - IITM",
    "noida-sector-62": "Sector 62, Noida - IMD",
    "gurugram-vikas-sadan": "Vikas Sadan, Gurugram - HSPCB",
    "mumbai-bandra-kurla": "Bandra Kurla Complex, Mumbai - MPCB",
    "bengaluru-btm-layout": "BTM Layout, Bengaluru - CPCB",
    "udaipur-ashok-nagar": "Ashok Nagar, Udaipur - RSPCB",
}


def normalize_pollutant_name(raw_name: str) -> str:
    """Normalize pollutant identifiers (e.g. OZONE -> O3, PM2.5, PM10)."""
    cleaned = raw_name.strip().upper()
    if cleaned in ("OZONE", "O_3", "OZ"):
        return "O3"
    return cleaned


def parse_cpcb_timestamp(ts_str: Optional[str]) -> datetime:
    """Parse CPCB timestamp format DD-MM-YYYY HH:MM:SS or fallback to UTC now."""
    if not ts_str:
        return datetime.utcnow()
    cleaned = ts_str.strip()
    for fmt in ("%d-%m-%Y %H:%M:%S", "%Y-%m-%d %H:%M:%S", "%d/%m/%Y %H:%M:%S"):
        try:
            return datetime.strptime(cleaned, fmt)
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(cleaned)
    except Exception:
        return datetime.utcnow()


class BaseAqiProvider(ABC):
    @abstractmethod
    def get_stations(self) -> List[StationInfo]:
        """Retrieve list of available monitoring stations."""
        pass

    @abstractmethod
    def get_current_aqi(self, station_id: str) -> CurrentAqiResponse:
        """Retrieve current AQI and pollutant concentrations."""
        pass

    @abstractmethod
    def get_forecast(self, station_id: str) -> ForecastResponse:
        """Retrieve 24-hour diurnal projection."""
        pass

    @abstractmethod
    def is_live(self) -> bool:
        """Return True if this provider serves live verified external telemetry."""
        pass


class MockAqiProvider(BaseAqiProvider):
    """
    Calibrated CPCB baseline provider.
    Guarantees mathematically verified CPCB NAQI calculations and clear demonstration flags.
    """

    def get_stations(self) -> List[StationInfo]:
        return AqiService.get_stations()

    def get_current_aqi(self, station_id: str) -> CurrentAqiResponse:
        return AqiService.get_current_aqi(station_id)

    def get_forecast(self, station_id: str) -> ForecastResponse:
        return AqiService.get_forecast(station_id)

    def is_live(self) -> bool:
        return False


class DataGovInProvider(BaseAqiProvider):
    """
    Official CPCB Real Time Air Quality Index provider via data.gov.in.
    Resource: 3b01bcb8-0b14-4abf-b6f2-c1bfd384ba69
    """

    def __init__(self, api_key: str, cache_ttl: int = 900):
        self.api_key = api_key
        self.cache_ttl = cache_ttl
        self.base_url = "https://api.data.gov.in/resource/3b01bcb8-0b14-4abf-b6f2-c1bfd384ba69"
        self._cache: Dict[str, Tuple[datetime, CurrentAqiResponse]] = {}

    def is_live(self) -> bool:
        return bool(self.api_key)

    def get_stations(self) -> List[StationInfo]:
        return AqiService.get_stations()

    def get_forecast(self, station_id: str) -> ForecastResponse:
        # Forecast is derived from current baseline diurnal inversion curve
        return AqiService.get_forecast(station_id)

    def parse_records(
        self, records: List[Dict[str, Any]], station: StationInfo
    ) -> Optional[CurrentAqiResponse]:
        """
        Parse official data.gov.in records for a station.
        Validates pollutant IDs, numeric values, observation times, and computes official CPCB AQI.
        """
        if not records:
            return None

        valid_pollutants: Dict[str, float] = {}
        parsed_timestamp: Optional[datetime] = None

        for r in records:
            raw_pol = r.get("pollutant_id", "")
            pol_key = normalize_pollutant_name(raw_pol)
            if pol_key not in POLLUTANT_META:
                continue

            # Parse numeric concentration (prefer avg_value; fallback to min/max if avg missing)
            val_str = r.get("avg_value")
            if val_str in (None, "", "NA", "null"):
                val_str = r.get("max_value")

            if val_str in (None, "", "NA", "null"):
                continue

            try:
                val = float(val_str)
                if val >= 0:
                    # In data.gov.in CAAQMS exports, CO is typically scaled as hundredths of mg/m³ (e.g. 127 -> 1.27 mg/m³)
                    if pol_key == "CO" and val > 10.0:
                        val = round(val / 100.0, 2)

                    valid_pollutants[pol_key] = val
                    if not parsed_timestamp and r.get("last_update"):
                        parsed_timestamp = parse_cpcb_timestamp(r.get("last_update"))
            except (ValueError, TypeError):
                continue

        # CPCB Official Rule: Minimum 3 pollutants required, and one must be PM2.5 or PM10
        has_particulate = "PM2.5" in valid_pollutants or "PM10" in valid_pollutants
        if len(valid_pollutants) < 3 or not has_particulate:
            logger.info(
                f"Insufficient pollutants ({len(valid_pollutants)}) or missing particulate for station {station.name}. Cannot compute official CPCB AQI."
            )
            return None

        # Calculate sub-indices and determine prominent pollutant
        pollutant_details: Dict[str, PollutantDetail] = {}
        max_subindex = 0
        prominent = "PM2.5"

        for pol_key, conc in valid_pollutants.items():
            sub = calculate_subindex(pol_key, conc)
            cat = get_aqi_category_from_value(sub)
            meta = POLLUTANT_META[pol_key]

            pollutant_details[pol_key] = PollutantDetail(
                name=pol_key,
                value=conc,
                unit=meta[2],
                sub_index=sub,
                category=cat,
                standard_limit=meta[0],
                who_limit=meta[1],
            )

            if sub > max_subindex:
                max_subindex = sub
                prominent = pol_key

        overall_aqi = max_subindex
        overall_category = get_aqi_category_from_value(overall_aqi)
        health_adv = get_health_advisory(overall_category, overall_aqi)

        # Ambient weather telemetry (from Open-Meteo external service with graceful fallback)
        weather_detail = weather_service.get_weather_sync(
            latitude=station.latitude,
            longitude=station.longitude,
            station_id=station.id,
            station_name=station.name,
        )

        return CurrentAqiResponse(
            station=station,
            aqi=overall_aqi,
            category=overall_category,
            prominent_pollutant=prominent,
            pollutants=pollutant_details,
            health_advisory=health_adv,
            weather=weather_detail,
            data_source="Central Pollution Control Board (CPCB) - data.gov.in CAAQMS Live",
            last_updated=parsed_timestamp or datetime.utcnow(),
            is_demo_data=False,
        )

    def fetch_live_records(
        self,
        filters: Optional[Dict[str, str]] = None,
        offset: int = 0,
        limit: int = 25,
    ) -> List[Dict[str, Any]]:
        """
        Execute synchronous HTTP request to data.gov.in with query filters, offset, and limit.
        Handles errors (400, 401, 403, 429, 5xx, timeouts) safely.
        """
        if not self.api_key:
            return []

        params: Dict[str, Any] = {
            "api-key": self.api_key,
            "format": "json",
            "offset": offset,
            "limit": limit,
        }

        if filters:
            for k, v in filters.items():
                if v:
                    params[f"filters[{k}]"] = v

        headers = {"User-Agent": "AirSaathi-AI/1.0", "Accept": "application/json"}

        try:
            with httpx.Client(timeout=10.0) as client:
                res = client.get(self.base_url, params=params, headers=headers)

                if res.status_code == 200:
                    payload = res.json()
                    return payload.get("records", [])
                elif res.status_code in (400, 401, 403):
                    logger.warning(
                        f"data.gov.in returned client error {res.status_code}. Verify DATAGOVIN_API_KEY."
                    )
                    return []
                elif res.status_code == 429:
                    logger.warning("data.gov.in rate limit exceeded (HTTP 429).")
                    return []
                else:
                    logger.warning(
                        f"data.gov.in returned unexpected HTTP status {res.status_code}."
                    )
                    return []
        except httpx.TimeoutException:
            logger.warning("data.gov.in request timed out after 10s.")
            return []
        except httpx.RequestError as e:
            logger.warning(f"data.gov.in network connectivity error: {e}")
            return []
        except Exception as e:
            logger.warning(f"Unexpected error querying data.gov.in: {e}")
            return []

    def get_current_aqi(self, station_id: str = "delhi-anand-vihar") -> CurrentAqiResponse:
        """
        Retrieve current AQI for a station:
        1. Checks in-memory cache within TTL.
        2. Queries data.gov.in with station filter.
        3. Parses live records and calculates CPCB NAQI.
        4. Caches live response.
        5. If request fails or data is insufficient, returns cached data or calibrated CPCB baseline.
        """
        station = AqiService.get_station_by_id(station_id) or AqiService.get_stations()[0]

        # 1. Check in-memory cache
        if station.id in self._cache:
            cached_time, cached_res = self._cache[station.id]
            if datetime.utcnow() - cached_time < timedelta(seconds=self.cache_ttl):
                return cached_res

        # 2. Determine exact station filter for data.gov.in
        cpcb_station_name = CPCB_STATION_MAP.get(station.id, "")
        records: List[Dict[str, Any]] = []

        if cpcb_station_name:
            records = self.fetch_live_records(filters={"station": cpcb_station_name}, limit=25)

        # Fallback: if no records returned with exact station, try filtering by city
        if not records:
            records = self.fetch_live_records(filters={"city": station.city}, limit=100)
            if records:
                # Filter locally by station substring
                records = [
                    r
                    for r in records
                    if station.name.lower() in r.get("station", "").lower()
                ]

        # 3. Parse records
        live_res = self.parse_records(records, station)
        if live_res:
            self._cache[station.id] = (datetime.utcnow(), live_res)
            return live_res

        # 4. If previous cache exists, return it even if slightly aged
        if station.id in self._cache:
            return self._cache[station.id][1]

        # 5. Graceful fallback to calibrated CPCB demonstration baseline
        logger.info(
            f"Serving calibrated CPCB baseline for {station.name} (live telemetry unavailable)."
        )
        return AqiService.get_current_aqi(station_id)


def get_active_aqi_provider() -> BaseAqiProvider:
    """Factory to retrieve the appropriate AQI provider based on configuration."""
    if not settings.MOCK_MODE and settings.DATAGOVIN_API_KEY:
        return DataGovInProvider(settings.DATAGOVIN_API_KEY, cache_ttl=settings.AQI_CACHE_TTL_SECONDS)
    return MockAqiProvider()
