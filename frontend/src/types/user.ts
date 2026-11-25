import { FamilyProfile, SupportedLanguage } from './aqi';
import { RoutinePlan, RoutinePreferences } from './routine';
import { HouseholdInput } from './indoor';
import { MobilityRequest, ModeEmissionDetail } from './mobility';

export interface LocationPreferences {
  default_station_id: string;
  default_city: string;
  latitude?: number;
  longitude?: number;
}

export interface FamilyMemberProfile {
  name: string;
  age_group: 'infant' | 'child' | 'teen' | 'adult' | 'senior';
  vulnerabilities: string[];
  notes?: string;
}

export type AlertThresholdPreference = 'sensitive' | 'standard' | 'high_tolerance';

export interface HouseholdDemographics {
  has_infants?: boolean;
  has_children?: boolean;
  has_teens?: boolean;
  has_adults?: boolean;
  has_seniors?: boolean;
}

export interface HouseholdCleanAirPreferences {
  alert_threshold?: AlertThresholdPreference;
  preferred_transit_mode?: string;
  has_hepa_purifier?: boolean;
  has_kitchen_exhaust?: boolean;
  has_indoor_monitor?: boolean;
  morning_outdoor_window?: boolean;
  school_commute_active?: boolean;
  office_commute_active?: boolean;
  evening_outdoor_window?: boolean;
}

export interface FamilyPreferencesData {
  vulnerability: FamilyProfile;
  members?: FamilyMemberProfile[];
  configured_precautions?: string[];
  household_size?: number;
  demographics?: HouseholdDemographics;
  preferences?: HouseholdCleanAirPreferences;
}

export interface FamilyPreferencesUpdate {
  vulnerability?: Partial<FamilyProfile>;
  members?: FamilyMemberProfile[];
  configured_precautions?: string[];
  household_size?: number;
  demographics?: HouseholdDemographics;
  preferences?: HouseholdCleanAirPreferences;
}

export interface RoutinePreferencesData {
  preferences: RoutinePreferences;
  work_start_time?: string;
  work_end_time?: string;
  school_start_time?: string;
  school_end_time?: string;
  indoor_alternatives_enabled: boolean;
}

export interface UserProfile {
  uid: string;
  email?: string | null;
  display_name?: string | null;
  preferred_language: SupportedLanguage;
  location: LocationPreferences;
  family: FamilyPreferencesData;
  routine: RoutinePreferencesData;
  household?: HouseholdInput;
  mobility?: MobilityRequest;
  created_at?: string;
  updated_at?: string;
}

export interface UserProfileUpdate {
  display_name?: string | null;
  preferred_language?: SupportedLanguage;
  location?: LocationPreferences;
  family?: FamilyPreferencesUpdate | FamilyPreferencesData;
  routine?: RoutinePreferencesData;
  household?: HouseholdInput;
  mobility?: MobilityRequest;
}

export interface PersistedRoutineRecord {
  routine_id: string;
  station_id: string;
  date_str: string;
  plan: RoutinePlan;
  saved_at?: string;
}

export interface PersistedSavedRoute {
  route_id: string;
  title: string;
  origin?: string;
  destination?: string;
  distance_km: number;
  current_mode: string;
  recommended_option?: ModeEmissionDetail;
  created_at?: string;
}

export interface PersistedChatSession {
  session_id: string;
  title: string;
  messages: Array<{ role: 'user' | 'assistant'; text: string; timestamp?: string }>;
  station_id?: string;
  created_at?: string;
  updated_at?: string;
}

export interface AuthUser {
  uid: string;
  email: string | null;
  displayName: string | null;
  token?: string;
}

export interface PersonalizedActionItem {
  category: 'demographic' | 'indoor_asset' | 'commute' | 'general' | string;
  priority: 'urgent' | 'caution' | 'advisory' | 'good' | string;
  title: string;
  description: string;
  target_group?: string | null;
  rationale: string;
}

export interface PersonalizedAdvisoryResponse {
  status: 'active' | 'unavailable' | string;
  station_id?: string | null;
  station_name?: string | null;
  city?: string | null;
  aqi?: number | null;
  category?: string | null;
  prominent_pollutant?: string | null;
  data_source: string;
  is_demo_data: boolean;
  observed_at?: string | null;
  threshold_applied: AlertThresholdPreference;
  household_size: number;
  actions: PersonalizedActionItem[];
  active_safeguards: string[];
  equipment_status: {
    has_hepa_purifier?: boolean;
    has_kitchen_exhaust?: boolean;
    has_indoor_monitor?: boolean;
    preferred_transit_mode?: string;
    alert_threshold?: string;
    [key: string]: any;
  };
  disclaimer: string;
}
