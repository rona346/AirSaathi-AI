import React, { createContext, useContext, useState, useEffect } from 'react';
import { CurrentAqiData, FamilyProfile, ForecastData, StationInfo, SupportedLanguage } from '../types/aqi';
import { fetchCurrentAqi, fetchForecast, fetchStations } from '../services/api';

interface AppContextType {
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
}

const defaultFamilyProfile: FamilyProfile = {
  hasChildren: true,
  hasSeniors: true,
  hasRespiratoryCondition: false,
  isPregnant: false,
};

const AppContext = createContext<AppContextType | undefined>(undefined);

export const AppProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [selectedStationId, setSelectedStationId] = useState<string>('delhi-anand-vihar');
  const [stations, setStations] = useState<StationInfo[]>([]);
  const [currentAqi, setCurrentAqi] = useState<CurrentAqiData | null>(null);
  const [forecast, setForecast] = useState<ForecastData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [language, setLanguage] = useState<SupportedLanguage>('en');
  const [familyProfile, setFamilyProfile] = useState<FamilyProfile>(defaultFamilyProfile);
  const [isDemoData, setIsDemoData] = useState<boolean>(true);

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

  useEffect(() => {
    if (selectedStationId) {
      loadStationData(selectedStationId);
    }
  }, [selectedStationId]);

  const refreshData = async () => {
    await loadStationData(selectedStationId);
  };

  const updateFamilyProfile = (partial: Partial<FamilyProfile>) => {
    setFamilyProfile((prev) => ({ ...prev, ...partial }));
  };

  return (
    <AppContext.Provider
      value={{
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
