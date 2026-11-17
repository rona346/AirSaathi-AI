export type AqiCategory =
  | 'Good'
  | 'Satisfactory'
  | 'Moderate'
  | 'Poor'
  | 'Very Poor'
  | 'Severe'
  | 'Severe+';

export interface PollutantDetail {
  name: string;
  value: number;
  unit: string;
  sub_index: number;
  category: AqiCategory;
  standard_limit: number;
  who_limit: number;
}

export interface StationInfo {
  id: string;
  name: string;
  city: string;
  state: string;
  latitude: number;
  longitude: number;
  is_hotspot?: boolean;
}

export interface HealthAdvisory {
  general_advice: string;
  children_and_seniors: string;
  patients_with_respiratory_issues: string;
  outdoor_activity: string;
  mask_recommendation: string;
  purifier_recommendation: string;
  ventilation_window: string;
}

export interface HourlyAqiPoint {
  hour: string;
  time: string;
  aqi: number;
  category: AqiCategory;
  pm25: number;
  pm10: number;
}

export interface CurrentAqiData {
  station: StationInfo;
  aqi: number;
  category: AqiCategory;
  prominent_pollutant: string;
  pollutants: Record<string, PollutantDetail>;
  health_advisory: HealthAdvisory;
  weather: {
    temperature_c: number;
    humidity_percent: number;
    wind_speed_kmh: number;
    wind_direction: string;
    visibility_km: number;
    mixing_layer_height_m: number;
  };
  data_source: string;
  last_updated: string;
  is_demo_data: boolean;
}

export interface ForecastData {
  station_id: string;
  station_name: string;
  forecast_24h: HourlyAqiPoint[];
  peak_aqi_window: string;
  safest_outdoor_window: string;
  is_demo_data: boolean;
}

export interface FamilyProfile {
  hasChildren: boolean;
  hasSeniors: boolean;
  hasRespiratoryCondition: boolean;
  isPregnant: boolean;
}

export type SupportedLanguage = 'en' | 'hi';
