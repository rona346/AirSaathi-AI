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
  CalculationMethodologyDetail,
  ImpactLogCreate,
  ImpactLogRecord,
  ImpactSummaryResponse,
  PaginatedImpactLogs,
  TimeframeFilter,
} from '../types/impact';
import {
  MOCK_IMPACT_METHODOLOGY,
  MOCK_STATIONS,
  getMockChatResponse,
  getMockCurrentAqi,
  getMockForecast,
  getMockImpactLogs,
  getMockImpactSummary,
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

// Module 6: Environmental Impact Tracker APIs

export async function fetchImpactSummary(
  token?: string | null,
  timeframe: TimeframeFilter = 'week'
): Promise<{ data: ImpactSummaryResponse; isDemo: boolean }> {
  const headers: Record<string, string> = { Accept: 'application/json' };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  try {
    const res = await fetch(`${API_BASE}/impact/summary?timeframe=${encodeURIComponent(timeframe)}`, {
      headers,
    });
    if (!res.ok) {
      const errJson = await res.json().catch(() => ({}));
      const errorMsg =
        errJson.detail ||
        `Server error (${res.status}): Failed to retrieve impact summary.`;
      throw new Error(errorMsg);
    }
    const json = await res.json();
    return { data: json.data, isDemo: json.is_demo_data };
  } catch (err: any) {
    // For authenticated users, propagate error so UI displays genuine error state
    if (token) {
      console.warn('Authenticated impact summary request failed:', err);
      throw err;
    }
    // Only unauthenticated guests fall back to offline demonstration data
    console.info('Backend unreachable for guest user, serving offline simulated summary baseline:', err);
    return { data: getMockImpactSummary(timeframe) as unknown as ImpactSummaryResponse, isDemo: true };
  }
}

export async function fetchImpactLogs(
  token?: string | null,
  timeframe?: TimeframeFilter,
  limit: number = 20,
  offset: number = 0
): Promise<{ data: PaginatedImpactLogs; isDemo: boolean }> {
  const headers: Record<string, string> = { Accept: 'application/json' };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  let url = `${API_BASE}/impact/logs?limit=${limit}&offset=${offset}`;
  if (timeframe) url += `&timeframe=${encodeURIComponent(timeframe)}`;

  try {
    const res = await fetch(url, { headers });
    if (!res.ok) {
      const errJson = await res.json().catch(() => ({}));
      const errorMsg =
        errJson.detail ||
        `Server error (${res.status}): Failed to retrieve impact logs.`;
      throw new Error(errorMsg);
    }
    const json = await res.json();
    return { data: json.data, isDemo: json.is_demo_data };
  } catch (err: any) {
    if (token) {
      console.warn('Authenticated impact logs request failed:', err);
      throw err;
    }
    console.info('Backend unreachable for guest user, serving offline simulated logs baseline:', err);
    return { data: getMockImpactLogs(limit, offset) as unknown as PaginatedImpactLogs, isDemo: true };
  }
}

export async function createImpactLog(
  token: string,
  payload: ImpactLogCreate
): Promise<{ data: ImpactLogRecord; error?: string }> {
  try {
    const res = await fetch(`${API_BASE}/impact/logs`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const errJson = await res.json().catch(() => ({}));
      throw new Error(errJson.detail || `HTTP error ${res.status}`);
    }
    const json = await res.json();
    return { data: json.data };
  } catch (err: any) {
    console.warn('Failed to record impact activity:', err);
    throw err;
  }
}

export async function deleteImpactLog(
  token: string,
  logId: string
): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE}/impact/logs/${encodeURIComponent(logId)}`, {
      method: 'DELETE',
      headers: {
        Accept: 'application/json',
        Authorization: `Bearer ${token}`,
      },
    });
    if (!res.ok) {
      const errJson = await res.json().catch(() => ({}));
      throw new Error(errJson.detail || `HTTP error ${res.status}`);
    }
    return true;
  } catch (err) {
    console.warn(`Failed to delete impact log ${logId}:`, err);
    throw err;
  }
}

export async function fetchImpactMethodology(): Promise<CalculationMethodologyDetail> {
  try {
    const res = await fetch(`${API_BASE}/impact/methodology`, {
      headers: { Accept: 'application/json' },
    });
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    const json = await res.json();
    return json.data;
  } catch (err) {
    console.info('Using offline fallback methodology details:', err);
    return MOCK_IMPACT_METHODOLOGY as CalculationMethodologyDetail;
  }
}
