import { SupportedLanguage } from './aqi';

export interface ActivityTimeWindow {
  title: string;
  recommended_time: string;
  status: 'Recommended' | 'Caution' | 'Avoid' | 'Indoor Alternative' | string;
  risk_level: 'Low' | 'Moderate' | 'High' | 'Critical' | string;
  advice: string;
  rationale: string;
  indoor_alternative?: string | null;
  precautions: string[];
}

export interface RoutinePreferences {
  wakes_up_early: boolean;
  commutes_to_office: boolean;
  school_going_kids: boolean;
  exercises_daily: boolean;
  preferred_exercise_type: 'walk' | 'run' | 'gym' | 'yoga' | 'cycling' | string;
}

export interface RoutinePlan {
  station_id: string;
  station_name: string;
  city: string;
  aqi: number;
  category: string;
  prominent_pollutant: string;
  is_demo_data: boolean;
  data_source: string;
  observed_at: string;
  language: SupportedLanguage;
  ai_provider: 'google-gemini' | 'expert-rules-fallback' | string;
  ai_generated: boolean;
  morning: ActivityTimeWindow[];
  afternoon: ActivityTimeWindow[];
  evening: ActivityTimeWindow[];
  school_commute: ActivityTimeWindow;
  office_commute: ActivityTimeWindow;
  exercise_plan: ActivityTimeWindow;
  chores_plan: ActivityTimeWindow;
  family_precautions: string[];
  disclaimer: string;
  generated_at: string;
}
