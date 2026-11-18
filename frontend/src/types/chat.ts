import { SupportedLanguage } from './aqi';
import { HouseholdInput } from './indoor';

export type ChatRole = 'user' | 'assistant' | 'system';

export interface ChatMessage {
  role: ChatRole;
  content: string;
  timestamp?: string;
}

export interface ChatContextInfo {
  station_id: string;
  station_name: string;
  city: string;
  aqi: number;
  category: string;
  prominent_pollutant: string;
  is_demo_data: boolean;
  data_source: string;
  observed_at: string;
}

export interface ChatFamilyProfile {
  seniors_at_home: boolean;
  children_at_home: boolean;
  asthma_or_respiratory: boolean;
  pregnant_member: boolean;
  pets_at_home: boolean;
}

export interface ChatRequest {
  message: string;
  station_id?: string;
  language?: SupportedLanguage | string;
  history?: ChatMessage[];
  family_profile?: ChatFamilyProfile;
  household?: HouseholdInput;
}

export interface ChatResponse {
  message: string;
  language: SupportedLanguage | string;
  ai_provider: 'google-gemini' | 'expert-rules-fallback' | string;
  ai_generated: boolean;
  context_used: ChatContextInfo;
  suggested_followups: string[];
  disclaimer: string;
  timestamp: string;
}
