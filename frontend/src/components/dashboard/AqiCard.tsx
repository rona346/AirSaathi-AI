import React from 'react';
import { Thermometer, Droplets, Compass, Eye, Layers, AlertTriangle } from 'lucide-react';
import { useApp } from '../../context/AppContext';
import { formatTimestamp, getAqiBadgeClasses } from '../../utils/aqiUtils';

export const AqiCard: React.FC = () => {
  const { currentAqi, language } = useApp();

  if (!currentAqi) return null;

  const { aqi, category, prominent_pollutant, station, weather, last_updated } = currentAqi;
  const badgeClasses = getAqiBadgeClasses(category);

  // Calculate percentage along 0-500 scale for the indicator pointer (capped at 100%)
  const percentage = Math.min(100, Math.max(0, (aqi / 500) * 100));

  return (
    <div className="glass-panel rounded-3xl p-6 lg:p-8 relative overflow-hidden border border-slate-800 shadow-2xl">
      {/* Subtle ambient background glow */}
      <div
        className={`absolute -top-24 -right-24 w-80 h-80 rounded-full blur-3xl opacity-20 pointer-events-none ${
          aqi > 400
            ? 'bg-rose-900'
            : aqi > 300
            ? 'bg-red-600'
            : aqi > 200
            ? 'bg-orange-500'
            : aqi > 100
            ? 'bg-yellow-500'
            : 'bg-emerald-500'
        }`}
      />

      <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6">
        {/* Left Side: Station & Big AQI Score */}
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <span className="text-xs uppercase tracking-wider font-semibold text-slate-400">
              {station.city} • {station.state}
            </span>
            {station.is_hotspot && (
              <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-rose-400 bg-rose-500/10 border border-rose-500/30 px-2 py-0.5 rounded-full">
                <AlertTriangle className="w-3 h-3" />
                {language === 'hi' ? 'स्मॉग हॉटस्पॉट' : 'Pollution Hotspot'}
              </span>
            )}
          </div>

          <div>
            <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
              {station.name}
            </h1>
            <p className="text-xs text-slate-400 mt-1">
              {language === 'hi' ? 'अंतिम अपडेट:' : 'Last Updated:'}{' '}
              <span className="text-slate-300 font-medium">{formatTimestamp(last_updated)}</span>
            </p>
          </div>

          <div className="flex items-baseline gap-4 pt-1">
            <div className="flex items-baseline gap-2">
              <span className="text-6xl sm:text-7xl font-black tracking-tight text-white font-mono">
                {aqi}
              </span>
              <span className="text-sm font-semibold text-slate-400 uppercase tracking-widest">
                AQI
              </span>
            </div>

            <div className="flex flex-col gap-1.5">
              <span
                className={`text-sm sm:text-base font-bold px-3.5 py-1 rounded-xl border ${badgeClasses.bg} ${badgeClasses.text} ${badgeClasses.border} shadow-lg ${badgeClasses.glow}`}
              >
                {category}
              </span>
              <span className="text-xs text-slate-400 font-medium">
                {language === 'hi' ? 'प्रमुख प्रदूषक:' : 'Prominent:'}{' '}
                <strong className="text-slate-200">{prominent_pollutant}</strong>
              </span>
            </div>
          </div>
        </div>

        {/* Right Side: Micro-Meteorology & Atmospheric Dispersion */}
        <div className="w-full lg:w-auto bg-slate-900/80 rounded-2xl p-4 sm:p-5 border border-slate-800/90 shadow-inner">
          <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3 flex items-center justify-between">
            <span>{language === 'hi' ? 'मौसम व फैलाव स्थितियां' : 'Atmospheric Dispersion'}</span>
            <span className="text-[10px] text-slate-500 lowercase">CAAQMS telemetry</span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
            <div className="flex items-center gap-2.5 p-2 rounded-xl bg-slate-800/50 border border-slate-700/40">
              <div className="p-1.5 rounded-lg bg-sky-500/10 text-sky-400">
                <Thermometer className="w-4 h-4" />
              </div>
              <div>
                <span className="text-[11px] text-slate-400 block">Temperature</span>
                <span className="text-sm font-bold text-white">{weather.temperature_c}°C</span>
              </div>
            </div>

            <div className="flex items-center gap-2.5 p-2 rounded-xl bg-slate-800/50 border border-slate-700/40">
              <div className="p-1.5 rounded-lg bg-blue-500/10 text-blue-400">
                <Droplets className="w-4 h-4" />
              </div>
              <div>
                <span className="text-[11px] text-slate-400 block">Humidity</span>
                <span className="text-sm font-bold text-white">{weather.humidity_percent}%</span>
              </div>
            </div>

            <div className="flex items-center gap-2.5 p-2 rounded-xl bg-slate-800/50 border border-slate-700/40">
              <div className="p-1.5 rounded-lg bg-teal-500/10 text-teal-400">
                <Compass className="w-4 h-4" />
              </div>
              <div>
                <span className="text-[11px] text-slate-400 block">Wind</span>
                <span className="text-sm font-bold text-white">{weather.wind_speed_kmh} km/h {weather.wind_direction}</span>
              </div>
            </div>

            <div className="flex items-center gap-2.5 p-2 rounded-xl bg-slate-800/50 border border-slate-700/40">
              <div className="p-1.5 rounded-lg bg-amber-500/10 text-amber-400">
                <Eye className="w-4 h-4" />
              </div>
              <div>
                <span className="text-[11px] text-slate-400 block">Visibility</span>
                <span className="text-sm font-bold text-white">{weather.visibility_km} km</span>
              </div>
            </div>

            <div className="col-span-2 sm:col-span-2 flex items-center gap-2.5 p-2 rounded-xl bg-slate-800/50 border border-slate-700/40">
              <div className="p-1.5 rounded-lg bg-purple-500/10 text-purple-400">
                <Layers className="w-4 h-4" />
              </div>
              <div>
                <span className="text-[11px] text-slate-400 block">Boundary Layer (Inversion Height)</span>
                <span className="text-sm font-bold text-white">
                  {weather.mixing_layer_height_m} m{' '}
                  <span className="text-[10px] text-amber-400 font-normal">
                    (Trapping pollutants)
                  </span>
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* CPCB Scale Bar with Dynamic Needle */}
      <div className="mt-8 pt-6 border-t border-slate-800/80">
        <div className="flex items-center justify-between text-xs text-slate-400 mb-2 font-medium">
          <span>{language === 'hi' ? 'राष्ट्रीय वायु गुणवत्ता सूचकांक पैमाना (NAQI)' : 'National Air Quality Scale (NAQI)'}</span>
          <span className="font-semibold text-slate-300">
            {language === 'hi' ? `वर्तमान मान: ${aqi} (0-500)` : `Current: ${aqi} (Scale 0-500)`}
          </span>
        </div>

        {/* Visual Progress Gradient */}
        <div className="relative w-full h-3 rounded-full bg-slate-800 overflow-hidden flex">
          <div className="h-full bg-emerald-500" style={{ width: '10%' }} title="Good (0-50)" />
          <div className="h-full bg-lime-500" style={{ width: '10%' }} title="Satisfactory (51-100)" />
          <div className="h-full bg-yellow-400" style={{ width: '20%' }} title="Moderate (101-200)" />
          <div className="h-full bg-orange-500" style={{ width: '20%' }} title="Poor (201-300)" />
          <div className="h-full bg-red-500" style={{ width: '20%' }} title="Very Poor (301-400)" />
          <div className="h-full bg-rose-900" style={{ width: '20%' }} title="Severe (401-500)" />
        </div>

        {/* Indicator Marker */}
        <div className="relative w-full mt-1.5">
          <div
            className="absolute -top-3 transform -translate-x-1/2 flex flex-col items-center transition-all duration-500"
            style={{ left: `${percentage}%` }}
          >
            <div className="w-0 h-0 border-l-[6px] border-l-transparent border-r-[6px] border-r-transparent border-t-[8px] border-t-white" />
            <span className="text-[10px] font-bold text-white bg-slate-900 px-1.5 py-0.5 rounded border border-slate-700 shadow-md">
              {aqi}
            </span>
          </div>
        </div>

        {/* Band Legend */}
        <div className="grid grid-cols-6 gap-1 text-[10px] sm:text-xs text-center text-slate-400 mt-4 font-medium">
          <div className="truncate">Good (0-50)</div>
          <div className="truncate">Satisfactory (51-100)</div>
          <div className="truncate">Moderate (101-200)</div>
          <div className="truncate">Poor (201-300)</div>
          <div className="truncate text-red-400 font-semibold">Very Poor (301-400)</div>
          <div className="truncate text-rose-500 font-bold">Severe (401-500)</div>
        </div>
      </div>
    </div>
  );
};
