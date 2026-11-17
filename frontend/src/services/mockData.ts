import { CurrentAqiData, ForecastData, StationInfo } from '../types/aqi';
import { getAqiCategory } from '../utils/aqiUtils';

export const MOCK_STATIONS: StationInfo[] = [
  {
    id: 'delhi-anand-vihar',
    name: 'Anand Vihar',
    city: 'Delhi',
    state: 'Delhi',
    latitude: 28.6508,
    longitude: 77.3152,
    is_hotspot: true,
  },
  {
    id: 'delhi-punjabi-bagh',
    name: 'Punjabi Bagh',
    city: 'Delhi',
    state: 'Delhi',
    latitude: 28.6740,
    longitude: 77.1310,
    is_hotspot: true,
  },
  {
    id: 'delhi-rk-puram',
    name: 'RK Puram',
    city: 'Delhi',
    state: 'Delhi',
    latitude: 28.5660,
    longitude: 77.1767,
    is_hotspot: false,
  },
  {
    id: 'delhi-lodhi-road',
    name: 'Lodhi Road',
    city: 'Delhi',
    state: 'Delhi',
    latitude: 28.5918,
    longitude: 77.2273,
    is_hotspot: false,
  },
  {
    id: 'delhi-igi-airport',
    name: 'IGI Airport (T3)',
    city: 'Delhi',
    state: 'Delhi',
    latitude: 28.5562,
    longitude: 77.1000,
    is_hotspot: false,
  },
  {
    id: 'noida-sector-62',
    name: 'Sector 62',
    city: 'Noida',
    state: 'Uttar Pradesh',
    latitude: 28.6278,
    longitude: 77.3653,
    is_hotspot: true,
  },
  {
    id: 'gurugram-vikas-sadan',
    name: 'Vikas Sadan',
    city: 'Gurugram',
    state: 'Haryana',
    latitude: 28.4595,
    longitude: 77.0266,
    is_hotspot: false,
  },
  {
    id: 'mumbai-bandra-kurla',
    name: 'Bandra Kurla Complex',
    city: 'Mumbai',
    state: 'Maharashtra',
    latitude: 19.0657,
    longitude: 72.8687,
    is_hotspot: false,
  },
  {
    id: 'bengaluru-btm-layout',
    name: 'BTM Layout',
    city: 'Bengaluru',
    state: 'Karnataka',
    latitude: 12.9166,
    longitude: 77.6101,
    is_hotspot: false,
  },
];

export const getMockCurrentAqi = (stationId: string = 'delhi-anand-vihar'): CurrentAqiData => {
  const station = MOCK_STATIONS.find((s) => s.id === stationId) || MOCK_STATIONS[0];
  const aqiMap: Record<string, number> = {
    'delhi-anand-vihar': 368,
    'delhi-punjabi-bagh': 342,
    'delhi-rk-puram': 310,
    'delhi-lodhi-road': 275,
    'delhi-igi-airport': 295,
    'noida-sector-62': 352,
    'gurugram-vikas-sadan': 305,
    'mumbai-bandra-kurla': 164,
    'bengaluru-btm-layout': 88,
  };

  const aqi = aqiMap[station.id] || 320;
  
  return {
    station,
    aqi,
    category: getAqiCategory(aqi),
    prominent_pollutant: 'PM2.5',
    pollutants: {
      'PM2.5': {
        name: 'PM2.5',
        value: Math.round(aqi * 0.72),
        unit: 'µg/m³',
        sub_index: aqi,
        category: 'Very Poor',
        standard_limit: 60.0,
        who_limit: 15.0,
      },
      'PM10': {
        name: 'PM10',
        value: Math.round(aqi * 1.25),
        unit: 'µg/m³',
        sub_index: Math.min(500, Math.round(aqi * 0.9)),
        category: 'Very Poor',
        standard_limit: 100.0,
        who_limit: 45.0,
      },
      'NO2': {
        name: 'NO2',
        value: Math.round(55 + aqi * 0.12),
        unit: 'µg/m³',
        sub_index: Math.round(55 + aqi * 0.12),
        category: 'Moderate',
        standard_limit: 80.0,
        who_limit: 25.0,
      },
      'SO2': {
        name: 'SO2',
        value: Math.round(16.5 + aqi * 0.02),
        unit: 'µg/m³',
        sub_index: Math.round(16.5 + aqi * 0.02),
        category: 'Good',
        standard_limit: 80.0,
        who_limit: 40.0,
      },
      'CO': {
        name: 'CO',
        value: Number((1.2 + aqi * 0.005).toFixed(2)),
        unit: 'mg/m³',
        sub_index: Math.round((1.2 + aqi * 0.005) * 35),
        category: 'Moderate',
        standard_limit: 2.0,
        who_limit: 4.0,
      },
      'O3': {
        name: 'O3',
        value: Math.round(38.0 + aqi * 0.04),
        unit: 'µg/m³',
        sub_index: Math.round(38.0 + aqi * 0.04),
        category: 'Good',
        standard_limit: 100.0,
        who_limit: 100.0,
      },
    },
    health_advisory: {
      general_advice: 'Respiratory illness on prolonged exposure. Severe smog haze with reduced ambient visibility.',
      children_and_seniors: 'Stay indoors. Suspend all outdoor physical education, morning walks, and park play.',
      patients_with_respiratory_issues: 'Strict indoor stay. Keep emergency medication and nebulizer ready.',
      outdoor_activity: 'Strictly avoid all outdoor exercise, cycling, and walks during morning and night hours.',
      mask_recommendation: 'Strict N95/N99 mask requirement with airtight seal for any outdoor transit.',
      purifier_recommendation: 'Run HEPA filtration on medium-high mode. Seal window cracks with weatherstrips.',
      ventilation_window: 'Strictly do not open windows during inversion hours (early morning & late night).',
    },
    weather: {
      temperature_c: 19.5,
      humidity_percent: 74,
      wind_speed_kmh: 4.2,
      wind_direction: 'NW',
      visibility_km: 1.4,
      mixing_layer_height_m: 420,
    },
    data_source: 'Central Pollution Control Board (CPCB) - CAAQMS Mock Baseline',
    last_updated: new Date().toISOString(),
    is_demo_data: true,
  };
};

export const getMockForecast = (stationId: string = 'delhi-anand-vihar'): ForecastData => {
  const station = MOCK_STATIONS.find((s) => s.id === stationId) || MOCK_STATIONS[0];
  const current = getMockCurrentAqi(stationId);
  const baseAqi = current.aqi;
  
  const hourMultipliers = [
    0.98, 0.95, 0.92, 0.90, 0.95, 1.05, 1.18, 1.24, 1.20, 1.10, 0.98, 0.85,
    0.76, 0.72, 0.74, 0.80, 0.88, 0.98, 1.08, 1.15, 1.20, 1.18, 1.10, 1.02,
  ];

  const now = new Date();

  const points = hourMultipliers.map((mult, idx) => {
    const aqiVal = Math.round(baseAqi * mult);
    const date = new Date(now.getTime() + idx * 3600000);
    const hourLabel = date.toLocaleTimeString([], { hour: 'numeric', hour12: true });

    return {
      hour: hourLabel,
      time: date.toISOString(),
      aqi: aqiVal,
      category: getAqiCategory(aqiVal),
      pm25: Math.round(aqiVal * 0.72),
      pm10: Math.round(aqiVal * 1.25),
    };
  });

  return {
    station_id: station.id,
    station_name: station.name,
    forecast_24h: points,
    peak_aqi_window: '06:00 AM - 09:30 AM (Inversion Peak)',
    safest_outdoor_window: '01:30 PM - 04:00 PM (Higher Atmospheric Dispersion)',
    is_demo_data: true,
  };
};
