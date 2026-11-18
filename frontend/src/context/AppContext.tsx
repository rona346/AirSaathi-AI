import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { CurrentAqiData, FamilyProfile, ForecastData, StationInfo, SupportedLanguage } from '../types/aqi';
import { RoutinePlan, RoutinePreferences } from '../types/routine';
import { fetchCurrentAqi, fetchForecast, fetchRoutinePlan, fetchStations } from '../services/api';

export type AppTab = 'dashboard' | 'planner';

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

  useEffect(() => {
    if (selectedStationId) {
      loadStationData(selectedStationId);
      loadRoutinePlan(selectedStationId, language, familyProfile, routinePreferences);
    }
  }, [selectedStationId, language, familyProfile, routinePreferences, loadRoutinePlan]);

  const refreshData = async () => {
    await loadStationData(selectedStationId);
    await loadRoutinePlan(selectedStationId, language, familyProfile, routinePreferences);
  };

  const refreshRoutinePlan = async () => {
    await loadRoutinePlan(selectedStationId, language, familyProfile, routinePreferences);
  };

  const updateFamilyProfile = (partial: Partial<FamilyProfile>) => {
    setFamilyProfile((prev) => ({ ...prev, ...partial }));
  };

  const updateRoutinePreferences = (partial: Partial<RoutinePreferences>) => {
    setRoutinePreferences((prev) => ({ ...prev, ...partial }));
  };

  return (
    <AppContext.Provider
      value={{
        activeTab,
        setActiveTab,
        selectedStationId,
        setSelectedStationId,
        stations,
        currentAqi,
        forecast,
        loading,
        error,
        language,
        setLanguage,
        familyProfile,
        updateFamilyProfile,
        refreshData,
        isDemoData,
        routinePlan,
        routineLoading,
        routinePreferences,
        updateRoutinePreferences,
        refreshRoutinePlan,
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
