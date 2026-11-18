import React, { createContext, useContext, useState, useEffect, useCallback, useRef } from 'react';
import { CurrentAqiData, FamilyProfile, ForecastData, StationInfo, SupportedLanguage } from '../types/aqi';
import { RoutinePlan, RoutinePreferences } from '../types/routine';
import { HouseholdInput, IndoorAssessmentResponse } from '../types/indoor';
import { MobilityPlanResponse, MobilityRequest } from '../types/mobility';
import { AuthUser, UserProfile } from '../types/user';
import {
  fetchAuthServiceStatus,
  fetchCurrentAqi,
  fetchForecast,
  fetchIndoorAssessment,
  fetchMobilityPlan,
  fetchRoutinePlan,
  fetchStations,
  fetchUserProfile,
  saveUserRoutine,
  saveUserRoute,
  updateUserProfile,
} from '../services/api';
import {
  getCurrentIdToken,
  isFirebaseConfigured,
  loginWithEmailPassword,
  logoutUser,
  onAuthStateListener,
  registerWithEmailPassword,
} from '../services/firebase';

export type AppTab = 'dashboard' | 'planner' | 'indoor' | 'chat' | 'mobility';

export type PersistenceStatus = 'saved' | 'saving' | 'guest' | 'error';

interface AppContextType {
  activeTab: AppTab;
  setActiveTab: (tab: AppTab) => void;
  selectedStationId: string;
  setSelectedStationId: (id: string) => void;
  stations: StationInfo[];
  currentAqi: CurrentAqiData | null;
  forecast: ForecastData | null;
  loading: boolean;
  error: string | null;
  language: SupportedLanguage;
  setLanguage: (lang: SupportedLanguage) => void;
  familyProfile: FamilyProfile;
  updateFamilyProfile: (partial: Partial<FamilyProfile>) => void;
  refreshData: () => Promise<void>;
  isDemoData: boolean;

  // Module 2 Routine Planner state
  routinePlan: RoutinePlan | null;
  routineLoading: boolean;
  routinePreferences: RoutinePreferences;
  updateRoutinePreferences: (partial: Partial<RoutinePreferences>) => void;
  refreshRoutinePlan: () => Promise<void>;
  saveCurrentRoutinePlan: () => Promise<string | null>;

  // Module 3 Indoor Assistant state
  indoorAssessment: IndoorAssessmentResponse | null;
  indoorLoading: boolean;
  householdInput: HouseholdInput;
  updateHouseholdInput: (partial: Partial<HouseholdInput>) => void;
  refreshIndoorAssessment: () => Promise<void>;

  // Module 5 Sustainable Mobility state
  mobilityPlan: MobilityPlanResponse | null;
  mobilityLoading: boolean;
  mobilityRequest: MobilityRequest;
  updateMobilityRequest: (partial: Partial<MobilityRequest>) => void;
  refreshMobilityPlan: () => Promise<void>;
  saveCurrentMobilityRoute: (title?: string) => Promise<string | null>;

  // Firebase Authentication & Cloud Firestore Persistence
  user: AuthUser | null;
  authLoading: boolean;
  isGuestMode: boolean;
  isFirebaseAvailable: boolean;
  persistenceStatus: PersistenceStatus;
  login: (email: string, pass: string) => Promise<void>;
  register: (email: string, pass: string, displayName?: string) => Promise<void>;
  logout: () => Promise<void>;
  authModalOpen: boolean;
  setAuthModalOpen: (open: boolean) => void;
}

const defaultFamilyProfile: FamilyProfile = {
  hasChildren: true,
  hasSeniors: true,
  hasRespiratoryCondition: false,
  isPregnant: false,
};

const defaultRoutinePreferences: RoutinePreferences = {
  wakes_up_early: true,
  commutes_to_office: true,
  school_going_kids: true,
  exercises_daily: true,
  preferred_exercise_type: 'walk',
};

const defaultHouseholdInput: HouseholdInput = {
  room_type: 'living_room',
  room_area_sqft: 150.0,
  ceiling_height_ft: 10.0,
  cooking_fuel: 'lpg',
  heavy_frying_or_tadka: true,
  has_kitchen_chimney: true,
  has_kitchen_exhaust: true,
  ventilation_status: 'mostly_closed',
  cleaning_method: 'wet_mopping',
  burns_agarbatti_or_dhoop: true,
  has_pets: false,
  indoor_smoking: false,
  has_air_purifier: false,
  purifier_has_hepa: true,
};

const defaultMobilityRequest: MobilityRequest = {
  distance_km: 12.0,
  current_mode: 'petrol_car',
  frequency: 'daily_round_trip',
  purpose: 'office',
  accessibility: 'none',
  occupancy: 1,
};

const AppContext = createContext<AppContextType | undefined>(undefined);

export const AppProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [activeTab, setActiveTab] = useState<AppTab>('dashboard');
  const [selectedStationId, setSelectedStationId] = useState<string>('delhi-anand-vihar');
  const [stations, setStations] = useState<StationInfo[]>([]);
  const [currentAqi, setCurrentAqi] = useState<CurrentAqiData | null>(null);
  const [forecast, setForecast] = useState<ForecastData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [language, setLanguage] = useState<SupportedLanguage>('en');
  const [familyProfile, setFamilyProfile] = useState<FamilyProfile>(defaultFamilyProfile);
  const [isDemoData, setIsDemoData] = useState<boolean>(true);

  // Module 2 routine planner state
  const [routinePlan, setRoutinePlan] = useState<RoutinePlan | null>(null);
  const [routineLoading, setRoutineLoading] = useState<boolean>(false);
  const [routinePreferences, setRoutinePreferences] = useState<RoutinePreferences>(defaultRoutinePreferences);

  // Module 3 indoor assistant state
  const [indoorAssessment, setIndoorAssessment] = useState<IndoorAssessmentResponse | null>(null);
  const [indoorLoading, setIndoorLoading] = useState<boolean>(false);
  const [householdInput, setHouseholdInput] = useState<HouseholdInput>(defaultHouseholdInput);

  // Module 5 sustainable mobility state
  const [mobilityPlan, setMobilityPlan] = useState<MobilityPlanResponse | null>(null);
  const [mobilityLoading, setMobilityLoading] = useState<boolean>(false);
  const [mobilityRequest, setMobilityRequest] = useState<MobilityRequest>(defaultMobilityRequest);

  // Authentication & Persistence state
  const [user, setUser] = useState<AuthUser | null>(null);
  const [authLoading, setAuthLoading] = useState<boolean>(true);
  const [isFirebaseAvailable, setIsFirebaseAvailable] = useState<boolean>(isFirebaseConfigured());
  const [persistenceStatus, setPersistenceStatus] = useState<PersistenceStatus>('guest');
  const [authModalOpen, setAuthModalOpen] = useState<boolean>(false);

  const tokenRef = useRef<string | null>(null);

  // Check backend Firebase status on startup
  useEffect(() => {
    async function checkStatus() {
      const status = await fetchAuthServiceStatus();
      if (status.firebase_available && isFirebaseConfigured()) {
        setIsFirebaseAvailable(true);
      } else {
        setIsFirebaseAvailable(false);
        setPersistenceStatus('guest');
      }
    }
    checkStatus();
  }, []);

  // Listen for Firebase Auth state changes
  useEffect(() => {
    const unsubscribe = onAuthStateListener(async (firebaseUser) => {
      setAuthLoading(true);
      if (firebaseUser) {
        try {
          const token = await firebaseUser.getIdToken();
          tokenRef.current = token;
          const authUser: AuthUser = {
            uid: firebaseUser.uid,
            email: firebaseUser.email,
            displayName: firebaseUser.displayName,
            token,
          };
          setUser(authUser);

          // Fetch cloud profile from Firestore
          const profile = await fetchUserProfile(token);
          if (profile) {
            if (profile.preferred_language) {
              setLanguage(profile.preferred_language);
            }
            if (profile.location?.default_station_id) {
              setSelectedStationId(profile.location.default_station_id);
            }
            if (profile.family?.vulnerability) {
              setFamilyProfile(profile.family.vulnerability);
            }
            if (profile.routine?.preferences) {
              setRoutinePreferences(profile.routine.preferences);
            }
            if (profile.household) {
              setHouseholdInput(profile.household);
            }
            if (profile.mobility) {
              setMobilityRequest(profile.mobility);
            }
            setPersistenceStatus('saved');
          } else {
            setPersistenceStatus('saved');
          }
        } catch (err) {
          console.warn('Error loading user profile after sign-in:', err);
          setPersistenceStatus('error');
        }
      } else {
        // Logged out / guest mode
        tokenRef.current = null;
        setUser(null);
        setPersistenceStatus('guest');
        // Reset preferences to default
        setFamilyProfile(defaultFamilyProfile);
        setRoutinePreferences(defaultRoutinePreferences);
        setHouseholdInput(defaultHouseholdInput);
        setMobilityRequest(defaultMobilityRequest);
      }
      setAuthLoading(false);
    });

    return () => unsubscribe();
  }, []);

  // Load stations once
  useEffect(() => {
    async function initStations() {
      try {
        const { data } = await fetchStations();
        setStations(data);
        if (data.length > 0 && !data.some((s) => s.id === selectedStationId)) {
          setSelectedStationId(data[0].id);
        }
      } catch (err) {
        console.error('Error fetching stations:', err);
      }
    }
    initStations();
  }, []);

  // Load AQI and Forecast when selectedStationId changes
  const loadStationData = async (stationId: string) => {
    setLoading(true);
    setError(null);
    try {
      const [aqiRes, forecastRes] = await Promise.all([
        fetchCurrentAqi(stationId),
        fetchForecast(stationId),
      ]);
      setCurrentAqi(aqiRes.data);
      setForecast(forecastRes.data);
      setIsDemoData(aqiRes.isDemo || forecastRes.isDemo);
    } catch (err: any) {
      setError(err?.message || 'Failed to fetch air quality data');
    } finally {
      setLoading(false);
    }
  };

  // Load routine plan
  const loadRoutinePlan = useCallback(
    async (stationId: string, lang: SupportedLanguage, fam: FamilyProfile, prefs: RoutinePreferences) => {
      setRoutineLoading(true);
      try {
        const { data } = await fetchRoutinePlan(stationId, lang, fam, prefs);
        setRoutinePlan(data);
      } catch (err) {
        console.error('Failed to load routine plan:', err);
      } finally {
        setRoutineLoading(false);
      }
    },
    []
  );

  // Load indoor assessment
  const loadIndoorAssessment = useCallback(
    async (stationId: string, lang: SupportedLanguage, hh: HouseholdInput) => {
      setIndoorLoading(true);
      try {
        const { data } = await fetchIndoorAssessment(stationId, lang, hh);
        setIndoorAssessment(data);
      } catch (err) {
        console.error('Failed to load indoor assessment:', err);
      } finally {
        setIndoorLoading(false);
      }
    },
    []
  );

  // Load mobility plan
  const loadMobilityPlan = useCallback(
    async (stationId: string, lang: SupportedLanguage, req: MobilityRequest) => {
      setMobilityLoading(true);
      try {
        const { data } = await fetchMobilityPlan({
          ...req,
          station_id: stationId,
          language: lang,
        });
        setMobilityPlan(data);
      } catch (err) {
        console.error('Failed to load mobility plan:', err);
      } finally {
        setMobilityLoading(false);
      }
    },
    []
  );

  useEffect(() => {
    if (selectedStationId) {
      loadStationData(selectedStationId);
      loadRoutinePlan(selectedStationId, language, familyProfile, routinePreferences);
      loadIndoorAssessment(selectedStationId, language, householdInput);
      loadMobilityPlan(selectedStationId, language, mobilityRequest);
    }
  }, [
    selectedStationId,
    language,
    familyProfile,
    routinePreferences,
    householdInput,
    mobilityRequest,
    loadRoutinePlan,
    loadIndoorAssessment,
    loadMobilityPlan,
  ]);

  const refreshData = async () => {
    await loadStationData(selectedStationId);
    await loadRoutinePlan(selectedStationId, language, familyProfile, routinePreferences);
    await loadIndoorAssessment(selectedStationId, language, householdInput);
    await loadMobilityPlan(selectedStationId, language, mobilityRequest);
  };

  const refreshRoutinePlan = async () => {
    await loadRoutinePlan(selectedStationId, language, familyProfile, routinePreferences);
  };

  const refreshIndoorAssessment = async () => {
    await loadIndoorAssessment(selectedStationId, language, householdInput);
  };

  const refreshMobilityPlan = async () => {
    await loadMobilityPlan(selectedStationId, language, mobilityRequest);
  };

  // Helper to persist updates to Cloud Firestore if authenticated
  const syncProfileToCloud = async (update: Partial<UserProfile>) => {
    const token = tokenRef.current || (await getCurrentIdToken());
    if (!token) {
      setPersistenceStatus('guest');
      return;
    }
    setPersistenceStatus('saving');
    try {
      const res = await updateUserProfile(token, update);
      if (res) {
        setPersistenceStatus('saved');
      } else {
        setPersistenceStatus('error');
      }
    } catch {
      setPersistenceStatus('error');
    }
  };

  const updateFamilyProfile = (partial: Partial<FamilyProfile>) => {
    setFamilyProfile((prev) => {
      const updated = { ...prev, ...partial };
      syncProfileToCloud({
        family: {
          vulnerability: updated,
          members: [],
          configured_precautions: [],
        },
      });
      return updated;
    });
  };

  const updateRoutinePreferences = (partial: Partial<RoutinePreferences>) => {
    setRoutinePreferences((prev) => {
      const updated = { ...prev, ...partial };
      syncProfileToCloud({
        routine: {
          preferences: updated,
          indoor_alternatives_enabled: true,
        },
      });
      return updated;
    });
  };

  const updateHouseholdInput = (partial: Partial<HouseholdInput>) => {
    setHouseholdInput((prev) => {
      const updated = { ...prev, ...partial };
      syncProfileToCloud({ household: updated });
      return updated;
    });
  };

  const updateMobilityRequest = (partial: Partial<MobilityRequest>) => {
    setMobilityRequest((prev) => {
      const updated = { ...prev, ...partial };
      syncProfileToCloud({ mobility: updated });
      return updated;
    });
  };

  const handleSetLanguage = (lang: SupportedLanguage) => {
    setLanguage(lang);
    syncProfileToCloud({ preferred_language: lang });
  };

  const handleSetSelectedStationId = (id: string) => {
    setSelectedStationId(id);
    const station = stations.find((s) => s.id === id);
    syncProfileToCloud({
      location: {
        default_station_id: id,
        default_city: station?.city || 'Delhi',
      },
    });
  };

  const saveCurrentRoutinePlan = async (): Promise<string | null> => {
    if (!routinePlan) return null;
    const token = tokenRef.current || (await getCurrentIdToken());
    if (!token) {
      setAuthModalOpen(true);
      return null;
    }
    const routineId = `routine_${Date.now()}`;
    return await saveUserRoutine(token, {
      routine_id: routineId,
      station_id: selectedStationId,
      date_str: new Date().toISOString().split('T')[0],
      plan: routinePlan,
    });
  };

  const saveCurrentMobilityRoute = async (title: string = 'Daily Commute'): Promise<string | null> => {
    if (!mobilityPlan) return null;
    const token = tokenRef.current || (await getCurrentIdToken());
    if (!token) {
      setAuthModalOpen(true);
      return null;
    }
    const routeId = `route_${Date.now()}`;
    return await saveUserRoute(token, {
      route_id: routeId,
      title,
      origin: mobilityRequest.starting_area,
      destination: mobilityRequest.destination_area,
      distance_km: mobilityRequest.distance_km,
      current_mode: mobilityRequest.current_mode || 'petrol_car',
      recommended_option: mobilityPlan.mode_comparisons?.[0] || {
        mode: mobilityPlan.recommended_mode,
        label: mobilityPlan.recommended_mode_label,
      },
    });
  };

  const login = async (email: string, pass: string) => {
    setAuthLoading(true);
    try {
      await loginWithEmailPassword(email, pass);
    } finally {
      setAuthLoading(false);
    }
  };

  const register = async (email: string, pass: string, displayName?: string) => {
    setAuthLoading(true);
    try {
      await registerWithEmailPassword(email, pass, displayName);
    } finally {
      setAuthLoading(false);
    }
  };

  const logout = async () => {
    setAuthLoading(true);
    try {
      await logoutUser();
    } finally {
      setAuthLoading(false);
    }
  };

  return (
    <AppContext.Provider
      value={{
        activeTab,
        setActiveTab,
        selectedStationId,
        setSelectedStationId: handleSetSelectedStationId,
        stations,
        currentAqi,
        forecast,
        loading,
        error,
        language,
        setLanguage: handleSetLanguage,
        familyProfile,
        updateFamilyProfile,
        refreshData,
        isDemoData,
        routinePlan,
        routineLoading,
        routinePreferences,
        updateRoutinePreferences,
        refreshRoutinePlan,
        saveCurrentRoutinePlan,
        indoorAssessment,
        indoorLoading,
        householdInput,
        updateHouseholdInput,
        refreshIndoorAssessment,
        mobilityPlan,
        mobilityLoading,
        mobilityRequest,
        updateMobilityRequest,
        refreshMobilityPlan,
        saveCurrentMobilityRoute,
        user,
        authLoading,
        isGuestMode: !user,
        isFirebaseAvailable,
        persistenceStatus,
        login,
        register,
        logout,
        authModalOpen,
        setAuthModalOpen,
      }}
    >
      {children}
    </AppContext.Provider>
  );
};

export const useApp = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
};
