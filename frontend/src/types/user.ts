import { FamilyProfile, SupportedLanguage } from './aqi';
import { RoutinePreferences } from './routine';
import { HouseholdInput } from './indoor';
import { MobilityRequest } from './mobility';

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

export interface FamilyPreferencesData {
  vulnerability: FamilyProfile;
  members: FamilyMemberProfile[];
  configured_precautions: string[];
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
  family?: FamilyPreferencesData;
  routine?: RoutinePreferencesData;
  household?: HouseholdInput;
  mobility?: MobilityRequest;
}

export interface PersistedRoutineRecord {
  routine_id: string;
  station_id: string;
  date_str: string;
  plan: any;
  saved_at?: string;
}

export interface PersistedSavedRoute {
  route_id: string;
  title: string;
  origin?: string;
  destination?: string;
  distance_km: number;
  current_mode: string;
  recommended_option?: any;
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
