import { SupportedLanguage } from './aqi';

export type RoomType = 'bedroom' | 'kitchen' | 'living_room' | 'childrens_room' | 'study_room';
export type QualitativeRiskLevel = 'Low' | 'Moderate' | 'High' | 'Severe';
export type CookingFuel = 'lpg' | 'induction' | 'png' | 'traditional_biomass';
export type CleaningMethod = 'wet_mopping' | 'dry_broom' | 'vacuum_cleaner';
export type VentilationStatus = 'mostly_closed' | 'regular_cross_vent' | 'continuous_open';

export interface HouseholdInput {
  room_type: RoomType;
  room_area_sqft: number;
  ceiling_height_ft: number;
  cooking_fuel: CookingFuel;
  heavy_frying_or_tadka: boolean;
  has_kitchen_chimney: boolean;
  has_kitchen_exhaust: boolean;
  ventilation_status: VentilationStatus;
  cleaning_method: CleaningMethod;
  burns_agarbatti_or_dhoop: boolean;
  has_pets: boolean;
  indoor_smoking: boolean;
  has_air_purifier: boolean;
  purifier_has_hepa: boolean;
}

export interface VentilationAdvice {
  action: string;
  optimal_window: string;
  duration_minutes: number;
  rationale: string;
  precautions: string[];
}

export interface CadrRecommendation {
  room_area_sqft: number;
  recommended_min_cadr_m3h: number;
  recommended_min_cadr_cfm: number;
  target_ach: number;
  filter_type_guidance: string;
  placement_tips: string[];
  maintenance_schedule: string;
}

export interface KitchenGuidance {
  risk_summary: string;
  chimney_exhaust_guidance: string;
  cooking_habits_advice: string[];
  combustion_safety: string;
}

export interface RoomSpecificRecommendation {
  room_name: string;
  primary_threats: string[];
  immediate_actions: string[];
  night_protocol?: string | null;
  lifestyle_adjustments: string[];
}

export interface IndoorAssessmentResponse {
  station_id: string;
  station_name: string;
  city: string;
  outdoor_aqi: number;
  outdoor_category: string;
  outdoor_is_demo: boolean;
  outdoor_data_source: string;
  outdoor_observed_at: string;
  language: SupportedLanguage;
  ai_provider: string;
  ai_generated: boolean;
  has_connected_indoor_sensor: boolean;
  qualitative_risk: QualitativeRiskLevel;
  risk_score_numeric: number;
  risk_summary: string;
  sensor_notice: string;
  ventilation: VentilationAdvice;
  purifier_guidance: CadrRecommendation;
  kitchen_guidance: KitchenGuidance;
  room_recommendations: Record<string, RoomSpecificRecommendation>;
  actionable_checklist: string[];
  plant_myth_clarification: string;
  disclaimer: string;
  generated_at: string;
}
