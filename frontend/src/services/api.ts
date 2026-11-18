import { CurrentAqiData, FamilyProfile, ForecastData, StationInfo, SupportedLanguage } from '../types/aqi';
import { RoutinePlan, RoutinePreferences } from '../types/routine';
import { HouseholdInput, IndoorAssessmentResponse } from '../types/indoor';
import { ChatRequest, ChatResponse } from '../types/chat';
import { MobilityPlanResponse, MobilityRequest } from '../types/mobility';
import {
  PersistedChatSession,
  PersistedRoutineRecord,
  PersistedSavedRoute,
  UserProfile,
  UserProfileUpdate,
} from '../types/user';
import {
  MOCK_STATIONS,
  getMockChatResponse,
  getMockCurrentAqi,
  getMockForecast,
  getMockIndoorAssessment,
  getMockMobilityPlan,
  getMockRoutinePlan,
} from './mockData';

const API_BASE = '/api/v1';

export async function fetchStations(): Promise<{ data: StationInfo[]; isDemo: boolean }> {
  try {
    const res = await fetch(`${API_BASE}/aqi/stations`, {
      headers: { 'Accept': 'application/json' },
    });
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    const json = await res.json();
    return { data: json.data, isDemo: json.is_demo_data };
  } catch (err) {
    console.info('Backend unreachable or in demo mode, serving offline baseline stations.', err);
    return { data: MOCK_STATIONS, isDemo: true };
  }
}

export async function fetchCurrentAqi(stationId: string): Promise<{ data: CurrentAqiData; isDemo: boolean }> {
  try {
    const res = await fetch(`${API_BASE}/aqi/current?station_id=${encodeURIComponent(stationId)}`, {
      headers: { 'Accept': 'application/json' },
    });
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    const json = await res.json();
    return { data: json.data, isDemo: json.is_demo_data };
  } catch (err) {
    console.info(`Backend unreachable, serving demonstration benchmark for station: ${stationId}`);
    return { data: getMockCurrentAqi(stationId), isDemo: true };
  }
}

export async function fetchForecast(stationId: string): Promise<{ data: ForecastData; isDemo: boolean }> {
  try {
    const res = await fetch(`${API_BASE}/aqi/forecast?station_id=${encodeURIComponent(stationId)}`, {
      headers: { 'Accept': 'application/json' },
    });
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    const json = await res.json();
    return { data: json.data, isDemo: json.is_demo_data };
  } catch (err) {
    console.info(`Backend unreachable, serving diurnal forecast for station: ${stationId}`);
    return { data: getMockForecast(stationId), isDemo: true };
  }
}

export async function fetchRoutinePlan(
  stationId: string,
  language: SupportedLanguage,
  familyProfile: FamilyProfile,
  preferences?: RoutinePreferences
): Promise<{ data: RoutinePlan; isDemo: boolean }> {
  try {
    const payload = {
      station_id: stationId,
      language,
      family_profile: {
        has_children: familyProfile.hasChildren,
        has_seniors: familyProfile.hasSeniors,
        has_respiratory_condition: familyProfile.hasRespiratoryCondition,
        is_pregnant: familyProfile.isPregnant,
      },
      preferences: preferences || {
        wakes_up_early: true,
        commutes_to_office: true,
        school_going_kids: familyProfile.hasChildren,
        exercises_daily: true,
        preferred_exercise_type: 'walk',
      },
    };

    const res = await fetch(`${API_BASE}/routine/plan`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    const json = await res.json();
    return { data: json.data, isDemo: json.is_demo_data };
  } catch (err) {
    console.info(`Backend unreachable, serving offline fallback daily routine plan for station: ${stationId}`);
    return { data: getMockRoutinePlan(stationId, language), isDemo: true };
  }
}

export async function fetchIndoorAssessment(
  stationId: string,
  language: SupportedLanguage,
  household: HouseholdInput
): Promise<{ data: IndoorAssessmentResponse; isDemo: boolean }> {
  try {
    const payload = {
      station_id: stationId,
      language,
      household,
    };

    const res = await fetch(`${API_BASE}/indoor/assess`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    const json = await res.json();
    return { data: json.data, isDemo: json.is_demo_data };
  } catch (err) {
    console.info(`Backend unreachable, serving offline fallback indoor assessment for station: ${stationId}`);
    return { data: getMockIndoorAssessment(stationId, language, household), isDemo: true };
  }
}

export async function fetchChatMessage(
  request: ChatRequest
): Promise<{ data: ChatResponse; isDemo: boolean }> {
  try {
    const res = await fetch(`${API_BASE}/chat/message`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    const json = await res.json();
    return { data: json.data, isDemo: json.is_demo_data };
  } catch (err) {
    console.info('Backend unreachable, serving offline rule-based chat fallback response.', err);
    return {
      data: getMockChatResponse(request.message, request.station_id, request.language),
      isDemo: true,
    };
  }
}

export async function fetchMobilityPlan(
  request: MobilityRequest
): Promise<{ data: MobilityPlanResponse; isDemo: boolean }> {
  try {
    const res = await fetch(`${API_BASE}/mobility/plan`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    const json = await res.json();
    return { data: json.data, isDemo: json.is_demo_data };
  } catch (err) {
    console.info('Backend unreachable, serving offline sustainable mobility fallback plan.', err);
    return {
      data: getMockMobilityPlan(request),
      isDemo: true,
    };
  }
}

// ==========================================
// Authenticated User & Cloud Persistence APIs
// ==========================================

export async function fetchAuthServiceStatus(): Promise<{
  firebase_available: boolean;
  mode: string;
  persistence_active: boolean;
}> {
  try {
    const res = await fetch(`${API_BASE}/user/status`, {
      headers: { Accept: 'application/json' },
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const json = await res.json();
    return json.data;
  } catch (err) {
    return {
      firebase_available: false,
      mode: 'guest_demonstration',
      persistence_active: false,
    };
  }
}

export async function fetchUserProfile(token: string): Promise<UserProfile | null> {
  try {
    const res = await fetch(`${API_BASE}/user/me`, {
      headers: {
        Accept: 'application/json',
        Authorization: `Bearer ${token}`,
      },
    });
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    const json = await res.json();
    return json.data;
  } catch (err) {
    console.warn('Failed to fetch user profile:', err);
    return null;
  }
}

export async function updateUserProfile(
  token: string,
  update: UserProfileUpdate
): Promise<UserProfile | null> {
  try {
    const res = await fetch(`${API_BASE}/user/me`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(update),
    });
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    const json = await res.json();
    return json.data;
  } catch (err) {
    console.warn('Failed to update user profile in Cloud Firestore:', err);
    return null;
  }
}

export async function fetchUserRoutines(token: string): Promise<PersistedRoutineRecord[]> {
  try {
    const res = await fetch(`${API_BASE}/user/me/routines`, {
      headers: {
        Accept: 'application/json',
        Authorization: `Bearer ${token}`,
      },
    });
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    const json = await res.json();
    return json.data || [];
  } catch (err) {
    console.warn('Failed to fetch user routines:', err);
    return [];
  }
}

export async function saveUserRoutine(
  token: string,
  record: PersistedRoutineRecord
): Promise<string | null> {
  try {
    const res = await fetch(`${API_BASE}/user/me/routines`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(record),
    });
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    const json = await res.json();
    return json.data?.routine_id || null;
  } catch (err) {
    console.warn('Failed to save user routine:', err);
    return null;
  }
}

export async function fetchUserRoutes(token: string): Promise<PersistedSavedRoute[]> {
  try {
    const res = await fetch(`${API_BASE}/user/me/routes`, {
      headers: {
        Accept: 'application/json',
        Authorization: `Bearer ${token}`,
      },
    });
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    const json = await res.json();
    return json.data || [];
  } catch (err) {
    console.warn('Failed to fetch user routes:', err);
    return [];
  }
}

export async function saveUserRoute(
  token: string,
  route: PersistedSavedRoute
): Promise<string | null> {
  try {
    const res = await fetch(`${API_BASE}/user/me/routes`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(route),
    });
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    const json = await res.json();
    return json.data?.route_id || null;
  } catch (err) {
    console.warn('Failed to save user route:', err);
    return null;
  }
}

export async function fetchUserChatSessions(token: string): Promise<PersistedChatSession[]> {
  try {
    const res = await fetch(`${API_BASE}/user/me/chat-sessions`, {
      headers: {
        Accept: 'application/json',
        Authorization: `Bearer ${token}`,
      },
    });
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    const json = await res.json();
    return json.data || [];
  } catch (err) {
    console.warn('Failed to fetch user chat sessions:', err);
    return [];
  }
}

export async function saveUserChatSession(
  token: string,
  session: PersistedChatSession
): Promise<string | null> {
  try {
    const res = await fetch(`${API_BASE}/user/me/chat-sessions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(session),
    });
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    const json = await res.json();
    return json.data?.session_id || null;
  } catch (err) {
    console.warn('Failed to save user chat session:', err);
    return null;
  }
}
