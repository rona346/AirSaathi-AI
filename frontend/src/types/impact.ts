/**
 * TypeScript Interfaces for Module 6: Environmental Impact Tracker.
 * Matches backend schemas from backend/app/models/impact.py.
 */

export type ImpactActivityType =
  | 'commute'
  | 'carpool'
  | 'active_travel'
  | 'public_transit'
  | 'ev_transit'
  | 'purifier_optimized'
  | 'ventilation_timed';

export type TimeframeFilter = 'day' | 'week' | 'month' | 'all_time';

export type TransportMode =
  | 'petrol_car'
  | 'diesel_car'
  | 'cng_car'
  | 'electric_car'
  | 'two_wheeler_petrol'
  | 'two_wheeler'
  | 'electric_two_wheeler'
  | 'cng_auto'
  | 'public_bus'
  | 'electric_bus'
  | 'metro'
  | 'walking'
  | 'cycling'
  | 'carpool';

export interface ImpactLogCreate {
  activity_type: ImpactActivityType;
  mode?: TransportMode | null;
  distance_km?: number | null;
  passengers?: number;
  baseline_mode?: TransportMode;
  activity_date?: string | null;
  notes?: string | null;
  exposure_avoided_score?: number;
}

export interface ImpactLogRecord {
  log_id: string;
  user_id?: string | null;
  activity_type: ImpactActivityType;
  mode?: TransportMode | null;
  distance_km: number;
  passengers: number;
  vehicle_emissions_kg_co2e: number;
  per_passenger_emissions_kg_co2e: number;
  baseline_emissions_kg_co2e: number;
  emission_saved_kg_co2e: number;
  exposure_avoided_score: number;
  activity_date: string;
  notes?: string | null;
  recorded_at: string;
  data_provenance: string; // 'modeled_estimate' | 'simulated_demo'
  methodology_notes?: string | null;
}

export interface DailyTrendItem {
  date_str: string;
  day_label: string;
  emissions_kg: number;
  savings_kg: number;
  clean_distance_km: number;
  activity_count: number;
}

export interface ModeBreakdownItem {
  mode: string;
  label_en: string;
  label_hi: string;
  trip_count: number;
  distance_km: number;
  emissions_kg: number;
  savings_kg: number;
  distance_share_pct: number;
}

export interface CalculationMethodologyDetail {
  grid_emission_factor_g_per_kwh: number;
  grid_factor_source: string;
  petrol_car_baseline_factor_g_per_km: number;
  baseline_source: string;
  metro_factor_g_per_pax_km: number;
  metro_source: string;
  tree_monthly_absorption_kg: number;
  tree_source: string;
  indoor_action_disclaimer: string;
}

export interface SustainabilitySuggestion {
  id: string;
  title_en: string;
  title_hi: string;
  description_en: string;
  description_hi: string;
  potential_monthly_savings_kg: number;
  difficulty: 'easy' | 'moderate' | 'high';
  category: 'commute' | 'carpool' | 'indoor' | 'transit';
}

export interface ImpactSummaryResponse {
  timeframe: TimeframeFilter;
  total_activities_logged: number;
  total_distance_km: number;
  total_emissions_kg_co2e: number;
  total_savings_kg_co2e: number;
  tree_months_equivalent: number | null;
  daily_trends: DailyTrendItem[];
  mode_breakdown: ModeBreakdownItem[];
  suggestions: SustainabilitySuggestion[];
  methodology: CalculationMethodologyDetail;
  is_demo_data: boolean;
}

export interface PaginatedImpactLogs {
  items: ImpactLogRecord[];
  total_count: number;
  limit: number;
  offset: number;
  has_more: boolean;
}
