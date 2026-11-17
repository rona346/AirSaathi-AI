from datetime import datetime, timedelta
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
]


def get_aqi_category(aqi: int) -> AqiCategory:
    if aqi <= 50:
        return AqiCategory.GOOD
    elif aqi <= 100:
        return AqiCategory.SATISFACTORY
    elif aqi <= 200:
        return AqiCategory.MODERATE
    elif aqi <= 300:
        return AqiCategory.POOR
    elif aqi <= 400:
        return AqiCategory.VERY_POOR
    elif aqi <= 500:
        return AqiCategory.SEVERE
    else:
        return AqiCategory.SEVERE_PLUS


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
    def get_current_aqi(cls, station_id: str = "delhi-anand-vihar") -> CurrentAqiResponse:
        station = cls.get_station_by_id(station_id) or STATIONS[0]

        # Station-specific realistic baseline (Winter smog simulation for Delhi NCR)
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
        }

        aqi = base_aqi_map.get(station.id, 320)
        category = get_aqi_category(aqi)

        # Compute proportionate pollutant breakdown
        pm25_val = round(aqi * 0.72, 1)
        pm10_val = round(aqi * 1.25, 1)
        no2_val = round(55.0 + (aqi * 0.12), 1)
        so2_val = round(16.5 + (aqi * 0.02), 1)
        co_val = round(1.2 + (aqi * 0.005), 2)
        o3_val = round(38.0 + (aqi * 0.04), 1)

        pollutants: Dict[str, PollutantDetail] = {
            "PM2.5": PollutantDetail(
                name="PM2.5",
                value=pm25_val,
                unit="µg/m³",
                sub_index=aqi,
                category=category,
                standard_limit=60.0,
                who_limit=15.0,
            ),
            "PM10": PollutantDetail(
                name="PM10",
                value=pm10_val,
                unit="µg/m³",
                sub_index=min(500, int(aqi * 0.9)),
                category=get_aqi_category(int(aqi * 0.9)),
                standard_limit=100.0,
                who_limit=45.0,
            ),
            "NO2": PollutantDetail(
                name="NO2",
                value=no2_val,
                unit="µg/m³",
                sub_index=int(no2_val * 1.1),
                category=get_aqi_category(int(no2_val * 1.1)),
                standard_limit=80.0,
                who_limit=25.0,
            ),
            "SO2": PollutantDetail(
                name="SO2",
                value=so2_val,
                unit="µg/m³",
                sub_index=int(so2_val * 1.2),
                category=get_aqi_category(int(so2_val * 1.2)),
                standard_limit=80.0,
                who_limit=40.0,
            ),
            "CO": PollutantDetail(
                name="CO",
                value=co_val,
                unit="mg/m³",
                sub_index=int(co_val * 35),
                category=get_aqi_category(int(co_val * 35)),
                standard_limit=2.0,
                who_limit=4.0,
            ),
            "O3": PollutantDetail(
                name="O3",
                value=o3_val,
                unit="µg/m³",
                sub_index=int(o3_val * 0.8),
                category=get_aqi_category(int(o3_val * 0.8)),
                standard_limit=100.0,
                who_limit=100.0,
            ),
        }

        health_adv = get_health_advisory(category, aqi)

        weather = {
            "temperature_c": 19.5,
            "humidity_percent": 74.0,
            "wind_speed_kmh": 4.2,
            "wind_direction": "NW",
            "visibility_km": 1.4,
            "mixing_layer_height_m": 420.0,
        }

        return CurrentAqiResponse(
            station=station,
            aqi=aqi,
            category=category,
            prominent_pollutant="PM2.5",
            pollutants=pollutants,
            health_advisory=health_adv,
            weather=weather,
            data_source="Central Pollution Control Board (CPCB) - CAAQMS Mock Baseline",
            last_updated=datetime.utcnow(),
            is_demo_data=True,
        )

    @classmethod
    def get_forecast(cls, station_id: str = "delhi-anand-vihar") -> ForecastResponse:
        station = cls.get_station_by_id(station_id) or STATIONS[0]
        current_data = cls.get_current_aqi(station_id)
        base_aqi = current_data.aqi

        # Realistic diurnal pattern multipliers for winter in Northern India
        # Midnight: high; 6 AM - 9 AM: severe peak; 1 PM - 4 PM: trough; 9 PM: rises again
        hour_multipliers = [
            0.98, 0.95, 0.92, 0.90, 0.95, 1.05, 1.18, 1.24, 1.20, 1.10, 0.98, 0.85,
            0.76, 0.72, 0.74, 0.80, 0.88, 0.98, 1.08, 1.15, 1.20, 1.18, 1.10, 1.02,
        ]

        now = datetime.utcnow()
        points: List[HourlyAqiPoint] = []

        for i in range(24):
            t = now + timedelta(hours=i)
            hour_idx = t.hour
            multiplier = hour_multipliers[hour_idx]
            calculated_aqi = max(35, min(495, int(base_aqi * multiplier)))
            point_category = get_aqi_category(calculated_aqi)

            points.append(
                HourlyAqiPoint(
                    hour=f"{t.strftime('%I %p')}",
                    time=t,
                    aqi=calculated_aqi,
                    category=point_category,
                    pm25=round(calculated_aqi * 0.72, 1),
                    pm10=round(calculated_aqi * 1.25, 1),
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
