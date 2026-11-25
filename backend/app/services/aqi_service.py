from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional
from backend.app.models.aqi import (
    AqiCategory,
    CurrentAqiResponse,
    ForecastResponse,
    HealthAdvisory,
    HourlyAqiPoint,
    PollutantDetail,
    StationInfo,
)
from backend.app.services.cpcb_calculator import (
    calculate_concentration_for_subindex,
    calculate_subindex,
    get_aqi_category_from_value,
)
from backend.app.services.grap_service import evaluate_grap
from backend.app.services.weather_service import weather_service

STATIONS: List[StationInfo] = [
    StationInfo(
        id="delhi-anand-vihar",
        name="Anand Vihar",
        city="Delhi",
        state="Delhi",
        latitude=28.6508,
        longitude=77.3152,
        is_hotspot=True,
    ),
    StationInfo(
        id="delhi-punjabi-bagh",
        name="Punjabi Bagh",
        city="Delhi",
        state="Delhi",
        latitude=28.6740,
        longitude=77.1310,
        is_hotspot=True,
    ),
    StationInfo(
        id="delhi-rk-puram",
        name="RK Puram",
        city="Delhi",
        state="Delhi",
        latitude=28.5660,
        longitude=77.1767,
        is_hotspot=False,
    ),
    StationInfo(
        id="delhi-lodhi-road",
        name="Lodhi Road",
        city="Delhi",
        state="Delhi",
        latitude=28.5918,
        longitude=77.2273,
        is_hotspot=False,
    ),
    StationInfo(
        id="delhi-igi-airport",
        name="IGI Airport (T3)",
        city="Delhi",
        state="Delhi",
        latitude=28.5562,
        longitude=77.1000,
        is_hotspot=False,
    ),
    StationInfo(
        id="noida-sector-62",
        name="Sector 62",
        city="Noida",
        state="Uttar Pradesh",
        latitude=28.6278,
        longitude=77.3653,
        is_hotspot=True,
    ),
    StationInfo(
        id="gurugram-vikas-sadan",
        name="Vikas Sadan",
        city="Gurugram",
        state="Haryana",
        latitude=28.4595,
        longitude=77.0266,
        is_hotspot=False,
    ),
    StationInfo(
        id="mumbai-bandra-kurla",
        name="Bandra Kurla Complex",
        city="Mumbai",
        state="Maharashtra",
        latitude=19.0657,
        longitude=72.8687,
        is_hotspot=False,
    ),
    StationInfo(
        id="bengaluru-btm-layout",
        name="BTM Layout",
        city="Bengaluru",
        state="Karnataka",
        latitude=12.9166,
        longitude=77.6101,
        is_hotspot=False,
    ),
    StationInfo(
        id="udaipur-ashok-nagar",
        name="Ashok Nagar",
        city="Udaipur",
        state="Rajasthan",
        latitude=24.5854,
        longitude=73.7125,
        is_hotspot=False,
    ),
]


def get_aqi_category(aqi: int) -> AqiCategory:
    """Convenience wrapper for CPCB NAQI category lookup."""
    return get_aqi_category_from_value(aqi)


def get_health_advisory(category: AqiCategory, aqi: int) -> HealthAdvisory:
    if category in [AqiCategory.GOOD, AqiCategory.SATISFACTORY]:
        return HealthAdvisory(
            general_advice="Air quality is acceptable. Minimal health impact.",
            children_and_seniors="Safe for regular outdoor activities and play.",
            patients_with_respiratory_issues="Normal activities permitted. Keep prescribed rescue inhaler accessible.",
            outdoor_activity="Excellent time for morning walks, jogging, and sports.",
            mask_recommendation="No mask required.",
            purifier_recommendation="Indoor air purifiers not required under current ambient conditions.",
            ventilation_window="Good ventilation window: 11:00 AM - 4:00 PM.",
        )
    elif category == AqiCategory.MODERATE:
        return HealthAdvisory(
            general_advice="Breathing discomfort possible for people with lung disease, asthma, and heart conditions.",
            children_and_seniors="Take more breaks during prolonged outdoor exertion.",
            patients_with_respiratory_issues="Reduce intense outdoor physical activities; keep reliever medication handy.",
            outdoor_activity="Moderate outdoor activities. Prefer afternoon hours over early morning.",
            mask_recommendation="Consider standard masks in dense traffic corridors.",
            purifier_recommendation="Run purifiers in bedrooms during sleep hours.",
            ventilation_window="Brief ventilation recommended between 12:00 PM and 3:00 PM.",
        )
    elif category == AqiCategory.POOR:
        return HealthAdvisory(
            general_advice="Breathing discomfort to most people on prolonged exposure.",
            children_and_seniors="Limit prolonged outdoor activities; avoid vigorous play during peak morning hours.",
            patients_with_respiratory_issues="Avoid outdoor exertion. High likelihood of wheezing or irritation.",
            outdoor_activity="Shift workouts indoors. Avoid early morning jogging.",
            mask_recommendation="Wear N95/FFP2 mask when stepping outside.",
            purifier_recommendation="Run HEPA purifiers continuously in living and sleeping zones.",
            ventilation_window="Keep windows closed. Aerate briefly only around 2:00 PM if sunlight is strong.",
        )
    elif category == AqiCategory.VERY_POOR:
        return HealthAdvisory(
            general_advice="Respiratory illness on prolonged exposure. Significant haze and burning sensation in eyes.",
            children_and_seniors="Stay indoors. Suspend all outdoor physical education and play.",
            patients_with_respiratory_issues="Strict indoor stay. Keep emergency medication and nebulizer ready.",
            outdoor_activity="Strictly avoid all outdoor exercise, cycling, and walks.",
            mask_recommendation="Strict N95/N99 mask requirement with airtight seal for any unavoidable outdoor transit.",
            purifier_recommendation="Run HEPA filtration on medium-high mode. Seal window cracks with weatherstrips.",
            ventilation_window="Strictly do not open windows; boundary layer inversion traps toxic particulates.",
        )
    else:  # SEVERE or SEVERE_PLUS
        return HealthAdvisory(
            general_advice="Emergency public health warning. Severe respiratory and cardiovascular stress across all demographics.",
            children_and_seniors="Complete indoor confinement required. Avoid any physical exertion.",
            patients_with_respiratory_issues="Immediate medical attention if breathlessness occurs. Run HEPA filtration 24/7.",
            outdoor_activity="Hazardous! Do not step out. Cancel commutes where work-from-home is possible.",
            mask_recommendation="N95/N99 mask mandatory even for brief outdoor transitions.",
            purifier_recommendation="Continuous maximum filtration. Create a sealed clean room inside the home.",
            ventilation_window="Zero ventilation. Keep all doors, vents, and balconies sealed.",
        )


class AqiService:
    @staticmethod
    def get_stations() -> List[StationInfo]:
        return STATIONS

    @staticmethod
    def get_station_by_id(station_id: str) -> Optional[StationInfo]:
        for s in STATIONS:
            if s.id.lower() == station_id.lower():
                return s
        return None

    @classmethod
    def get_station_by_id_or_city(cls, identifier: str) -> Optional[StationInfo]:
        """Resolves a station matching either exact station ID or matching city name."""
        if not identifier:
            return None
        clean = identifier.strip().lower()
        for s in STATIONS:
            if s.id.lower() == clean or s.city.lower() == clean:
                return s
        for s in STATIONS:
            if clean in s.id.lower() or clean in s.city.lower():
                return s
        return None

    @classmethod
    def get_current_aqi(cls, station_id: str = "delhi-anand-vihar") -> CurrentAqiResponse:
        matched_station = cls.get_station_by_id_or_city(station_id)
        is_unverified = False

        if matched_station:
            station = matched_station
        else:
            is_unverified = True
            clean_city = (
                station_id.replace("station-", "")
                .replace("-station", "")
                .replace("-", " ")
                .strip()
                .title()
            )
            station = StationInfo(
                id=station_id,
                name=f"Monitoring Station ({clean_city})",
                city=clean_city,
                state="India",
                latitude=20.5937,
                longitude=78.9629,
                is_hotspot=False,
            )

        # Station-specific realistic baseline
        base_aqi_map = {
            "delhi-anand-vihar": 368,
            "delhi-punjabi-bagh": 342,
            "delhi-rk-puram": 310,
            "delhi-lodhi-road": 275,
            "delhi-igi-airport": 295,
            "noida-sector-62": 352,
            "gurugram-vikas-sadan": 305,
            "mumbai-bandra-kurla": 164,
            "bengaluru-btm-layout": 88,
            "udaipur-ashok-nagar": 135,
        }

        default_aqi = 145 if is_unverified else 320
        aqi = base_aqi_map.get(station.id, default_aqi)
        category = get_aqi_category_from_value(aqi)

        # Compute concentrations derived from official CPCB breakpoint formulas
        pm25_conc = calculate_concentration_for_subindex("PM2.5", aqi)
        pm10_sub = min(500, int(aqi * 0.88))
        pm10_conc = calculate_concentration_for_subindex("PM10", pm10_sub)
        no2_sub = min(300, int(50 + (aqi * 0.2)))
        no2_conc = calculate_concentration_for_subindex("NO2", no2_sub)
        so2_sub = min(150, int(20 + (aqi * 0.08)))
        so2_conc = calculate_concentration_for_subindex("SO2", so2_sub)
        co_sub = min(200, int(35 + (aqi * 0.12)))
        co_conc = calculate_concentration_for_subindex("CO", co_sub)
        o3_sub = min(150, int(30 + (aqi * 0.1)))
        o3_conc = calculate_concentration_for_subindex("O3", o3_sub)

        # Calculate exact sub-indices via CPCB formula
        pm25_sub = calculate_subindex("PM2.5", pm25_conc)
        pm10_sub_actual = calculate_subindex("PM10", pm10_conc)
        no2_sub_actual = calculate_subindex("NO2", no2_conc)
        so2_sub_actual = calculate_subindex("SO2", so2_conc)
        co_sub_actual = calculate_subindex("CO", co_conc)
        o3_sub_actual = calculate_subindex("O3", o3_conc)

        pollutants: Dict[str, PollutantDetail] = {
            "PM2.5": PollutantDetail(
                name="PM2.5",
                value=pm25_conc,
                unit="µg/m³",
                sub_index=pm25_sub,
                category=get_aqi_category_from_value(pm25_sub),
                standard_limit=60.0,
                who_limit=15.0,
            ),
            "PM10": PollutantDetail(
                name="PM10",
                value=pm10_conc,
                unit="µg/m³",
                sub_index=pm10_sub_actual,
                category=get_aqi_category_from_value(pm10_sub_actual),
                standard_limit=100.0,
                who_limit=45.0,
            ),
            "NO2": PollutantDetail(
                name="NO2",
                value=no2_conc,
                unit="µg/m³",
                sub_index=no2_sub_actual,
                category=get_aqi_category_from_value(no2_sub_actual),
                standard_limit=80.0,
                who_limit=25.0,
            ),
            "SO2": PollutantDetail(
                name="SO2",
                value=so2_conc,
                unit="µg/m³",
                sub_index=so2_sub_actual,
                category=get_aqi_category_from_value(so2_sub_actual),
                standard_limit=80.0,
                who_limit=40.0,
            ),
            "CO": PollutantDetail(
                name="CO",
                value=co_conc,
                unit="mg/m³",
                sub_index=co_sub_actual,
                category=get_aqi_category_from_value(co_sub_actual),
                standard_limit=2.0,
                who_limit=4.0,
            ),
            "O3": PollutantDetail(
                name="O3",
                value=o3_conc,
                unit="µg/m³",
                sub_index=o3_sub_actual,
                category=get_aqi_category_from_value(o3_sub_actual),
                standard_limit=100.0,
                who_limit=100.0,
            ),
        }

        health_adv = get_health_advisory(category, aqi)

        weather_detail = weather_service.get_weather_sync(
            latitude=station.latitude,
            longitude=station.longitude,
            station_id=station.id,
            station_name=station.name,
        )

        source_label = (
            "Demonstration Baseline (Unverified Station)"
            if is_unverified
            else "Central Pollution Control Board (CPCB) - CAAQMS Mock Baseline"
        )

        grap_status = evaluate_grap(
            aqi=aqi,
            city=station.city,
            state=station.state,
        )

        return CurrentAqiResponse(
            station=station,
            aqi=aqi,
            category=category,
            prominent_pollutant="PM2.5",
            pollutants=pollutants,
            health_advisory=health_adv,
            weather=weather_detail,
            data_source=source_label,
            last_updated=datetime.now(timezone.utc),
            is_demo_data=True,
            grap_status=grap_status,
        )

    @classmethod
    def get_forecast(cls, station_id: str = "delhi-anand-vihar") -> ForecastResponse:
        station = cls.get_station_by_id(station_id) or STATIONS[0]
        current_data = cls.get_current_aqi(station_id)
        base_aqi = current_data.aqi

        # Diurnal multipliers reflecting winter nocturnal boundary layer inversion
        hour_multipliers = [
            0.98, 0.95, 0.92, 0.90, 0.95, 1.05, 1.18, 1.24, 1.20, 1.10, 0.98, 0.85,
            0.76, 0.72, 0.74, 0.80, 0.88, 0.98, 1.08, 1.15, 1.20, 1.18, 1.10, 1.02,
        ]

        now = datetime.now(timezone.utc)
        points: List[HourlyAqiPoint] = []

        for i in range(24):
            t = now + timedelta(hours=i)
            hour_idx = t.hour
            multiplier = hour_multipliers[hour_idx]
            calculated_aqi = max(35, min(495, int(base_aqi * multiplier)))
            point_category = get_aqi_category_from_value(calculated_aqi)
            pm25 = calculate_concentration_for_subindex("PM2.5", calculated_aqi)
            pm10_sub = min(500, int(calculated_aqi * 0.88))
            pm10 = calculate_concentration_for_subindex("PM10", pm10_sub)

            points.append(
                HourlyAqiPoint(
                    hour=f"{t.strftime('%I %p')}",
                    time=t,
                    aqi=calculated_aqi,
                    category=point_category,
                    pm25=pm25,
                    pm10=pm10,
                )
            )

        return ForecastResponse(
            station_id=station.id,
            station_name=station.name,
            forecast_24h=points,
            peak_aqi_window="06:00 AM - 09:30 AM (Inversion Peak)",
            safest_outdoor_window="01:30 PM - 04:00 PM (Higher Atmospheric Dispersion)",
            is_demo_data=True,
        )
