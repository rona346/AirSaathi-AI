import { CurrentAqiData, ForecastData, StationInfo } from '../types/aqi';
import { MOCK_STATIONS, getMockCurrentAqi, getMockForecast } from './mockData';

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
