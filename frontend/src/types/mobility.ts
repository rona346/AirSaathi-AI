import { SupportedLanguage } from './aqi';

export type TransportMode =
  | 'petrol_car'
  | 'diesel_car'
  | 'two_wheeler'
  | 'electric_car'
  | 'electric_two_wheeler'
  | 'cng_auto'
  | 'public_bus'
  | 'electric_bus'
  | 'metro'
  | 'carpool'
  | 'walking'
  | 'cycling';

export type CommutePurpose =
  | 'office'
  | 'school_college'
  | 'errands'
  | 'healthcare'
  | 'leisure';

export type CommuteFrequency =
  | 'daily_round_trip'
  | 'one_way'
  | 'weekdays_only'
  | 'occasional';

export type AccessibilityNeed =
  | 'none'
  | 'wheelchair'
  | 'low_walking'
  | 'senior_friendly'
  | 'child_friendly';

export interface ModeEmissionDetail {
  mode: TransportMode;
  label: string;
  direct_emissions_g: number;
  grid_indirect_emissions_g: number;
  total_emissions_g: number;
  per_passenger_emissions_g: number;
  co2e_savings_vs_baseline_g: number;
  co2e_savings_pct: number;
  suitability_score: string;
  aqi_safety_verdict: string;
  exposure_level: string;
  precautions: string[];
}

export interface CarpoolEstimate {
  solo_trip_emissions_g: number;
  shared_2_person_emissions_g: number;
  shared_3_person_emissions_g: number;
  shared_4_person_emissions_g: number;
  daily_savings_kg: number;
  annual_savings_kg: number;
}

export interface MobilityRequest {
  station_id?: string;
  language?: SupportedLanguage | string;
  distance_km: number;
  starting_area?: string;
  destination_area?: string;
  current_mode?: TransportMode;
  frequency?: CommuteFrequency;
  purpose?: CommutePurpose;
  accessibility?: AccessibilityNeed;
  occupancy?: number;
}

export interface MobilityPlanResponse {
  station_id: string;
  station_name: string;
  city: string;
  aqi: number;
  category: string;
  prominent_pollutant: string;
  is_demo_data: boolean;
  data_source: string;
  observed_at: string;
  language: string;
  distance_km: number;
  frequency: string;
  current_mode: TransportMode;
  current_trip_emissions_g: number;
  current_daily_emissions_g: number;
  mode_comparisons: ModeEmissionDetail[];
  recommended_mode: TransportMode;
  recommended_mode_label: string;
  recommended_mode_reason: string;
  active_mobility_advisory: string;
  carpool_potential: CarpoolEstimate;
  ai_recommendation: string;
  ai_provider: string;
  ai_generated: boolean;
  methodology_notes: string[];
  disclaimer: string;
  generated_at: string;
}
