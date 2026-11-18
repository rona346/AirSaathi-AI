import React, { useState } from 'react';
import {
  Car,
  Bus,
  Train,
  Bike,
  Footprints,
  Leaf,
  Sparkles,
  ShieldAlert,
  ShieldCheck,
  AlertCircle,
  Info,
  Users,
  RefreshCw,
  CheckCircle2,
  MapPin,
  Activity,
  Zap,
  Navigation,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';
import { useApp } from '../../context/AppContext';
import {
  AccessibilityNeed,
  CommuteFrequency,
  CommutePurpose,
  TransportMode,
} from '../../types/mobility';
import { translations } from '../../utils/translations';
import { getAqiCategory, getAqiCategoryLabel } from '../../utils/aqiUtils';

export const MobilityAssistant: React.FC = () => {
  const {
    currentAqi,
    selectedStationId,
    stations,
    language,
    isDemoData,
    mobilityPlan,
    mobilityLoading,
    mobilityRequest,
    updateMobilityRequest,
    refreshMobilityPlan,
  } = useApp();

  const t = translations[language];
  const isHi = language === 'hi';
  const station = stations.find((s) => s.id === selectedStationId) || stations[0];
  const aqiCategory = currentAqi ? getAqiCategory(currentAqi.aqi) : null;

  const [showMethodology, setShowMethodology] = useState(false);

  const modeIcons: Record<TransportMode, React.ReactNode> = {
    metro: <Train className="w-5 h-5" />,
    electric_bus: <Bus className="w-5 h-5 text-emerald-400" />,
    public_bus: <Bus className="w-5 h-5 text-blue-400" />,
    carpool: <Users className="w-5 h-5 text-indigo-400" />,
    electric_car: <Zap className="w-5 h-5 text-emerald-400" />,
    electric_two_wheeler: <Zap className="w-5 h-5 text-teal-400" />,
    cng_auto: <Car className="w-5 h-5 text-amber-400" />,
    two_wheeler: <Bike className="w-5 h-5 text-sky-400" />,
    petrol_car: <Car className="w-5 h-5 text-rose-400" />,
    diesel_car: <Car className="w-5 h-5 text-rose-500" />,
    cycling: <Bike className="w-5 h-5 text-emerald-300" />,
    walking: <Footprints className="w-5 h-5 text-emerald-300" />,
  };

  const distancePresets = [2, 5, 12, 25];

  const handleDistanceChange = (val: number) => {
    updateMobilityRequest({ distance_km: Math.max(0.5, Math.min(150, val)) });
  };

  // Helper to format inline markdown bolding
  const renderFormattedText = (text: string) => {
    const lines = text.split('\n');
    return (
      <div className="space-y-2 text-sm leading-relaxed text-slate-200">
        {lines.map((line, idx) => {
          const trimmed = line.trim();
          if (!trimmed) return <div key={idx} className="h-1" />;
          if (trimmed.startsWith('### ')) {
            return (
              <h4 key={idx} className="text-sm font-bold text-white pt-1">
                {trimmed.slice(4)}
              </h4>
            );
          }
          if (trimmed.startsWith('- ') || trimmed.startsWith('* ')) {
            const content = trimmed.slice(2);
            return (
              <div key={idx} className="flex items-start gap-2 pl-2">
                <span className="text-emerald-400 mt-1 text-xs">•</span>
                <span className="flex-1">{renderInlineBolding(content)}</span>
              </div>
            );
          }
          return <p key={idx}>{renderInlineBolding(trimmed)}</p>;
        })}
      </div>
    );
  };

  const renderInlineBolding = (str: string) => {
    const parts = str.split(/(\*\*.*?\*\*)/g);
    return parts.map((part, i) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        return (
          <strong key={i} className="font-semibold text-white">
            {part.slice(2, -2)}
          </strong>
        );
      }
      return part;
    });
  };

  const plan = mobilityPlan;

  return (
    <div className="space-y-6">
      {/* 1. Module Header & Context Telemetry Banner */}
      <div className="glass-card rounded-2xl p-5 border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2.5">
            <div className="p-2.5 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-400">
              <Navigation className="w-5 h-5" />
            </div>
            <div>
              <h1 className="text-xl font-extrabold text-white flex items-center gap-2">
                <span>{t.mobilityTabTitle}</span>
                <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 flex items-center gap-1">
                  <Leaf className="w-3 h-3 text-emerald-400" />
                  Eco-Transit
                </span>
                {plan?.ai_generated ? (
                  <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-purple-500/20 text-purple-300 border border-purple-500/40 flex items-center gap-1">
                    <Sparkles className="w-3 h-3 text-purple-400" />
                    Gemini 2.5
                  </span>
                ) : (
                  <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-blue-500/20 text-blue-300 border border-blue-500/40 flex items-center gap-1">
                    <ShieldCheck className="w-3 h-3 text-blue-400" />
                    Domain Rules
                  </span>
                )}
              </h1>
              <p className="text-xs text-slate-400 mt-0.5">{t.mobilitySubtitle}</p>
            </div>
          </div>
        </div>

        {/* Ambient Telemetry Chip */}
        <div className="flex items-center flex-wrap gap-2">
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-xs">
            <MapPin className="w-3.5 h-3.5 text-emerald-400" />
            <span className="text-slate-300 font-medium">
              {station ? station.name : 'CPCB Station'}
            </span>
          </div>

          {currentAqi && (
            <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-xs">
              <Activity className="w-3.5 h-3.5 text-amber-400" />
              <span className="text-slate-400">AQI:</span>
              <strong className="text-white font-bold">{currentAqi.aqi}</strong>
              <span className="text-[10px] px-1.5 py-0.5 rounded font-medium bg-amber-500/20 text-amber-300 border border-amber-500/30">
                {aqiCategory ? getAqiCategoryLabel(aqiCategory, language) : 'CPCB'}
              </span>
            </div>
          )}

          <div className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-xs text-slate-400">
            <span
              className={`w-2 h-2 rounded-full ${
                isDemoData ? 'bg-amber-400' : 'bg-emerald-400'
              } animate-pulse`}
            />
            <span>{isDemoData ? 'Demo CPCB' : 'CPCB Live'}</span>
          </div>
        </div>
      </div>

      {/* 2. Interactive Commute Configuration Card */}
      <div className="glass-card rounded-2xl p-5 md:p-6 border border-slate-800 space-y-5">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <h2 className="text-base font-bold text-white flex items-center gap-2">
            <Navigation className="w-4 h-4 text-emerald-400" />
            <span>{t.commutePlannerTitle}</span>
          </h2>
          <button
            onClick={() => refreshMobilityPlan()}
            disabled={mobilityLoading}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-emerald-500 hover:bg-emerald-600 text-white font-semibold text-xs shadow-lg shadow-emerald-500/20 disabled:opacity-50 transition-all"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${mobilityLoading ? 'animate-spin' : ''}`} />
            <span>{mobilityLoading ? t.calculatingMobility : t.calculateMobilityBtn}</span>
          </button>
        </div>

        {/* Distance Controls & Presets */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <label className="text-xs font-semibold text-slate-300">
              {t.distanceKmLabel}
            </label>
            <div className="flex items-center gap-2">
              <span className="text-lg font-bold text-white font-mono">
                {mobilityRequest.distance_km} km
              </span>
              <span className="text-xs text-slate-400">
                ({mobilityRequest.distance_km * 2} km round-trip)
              </span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <input
              type="range"
              min="0.5"
              max="60"
              step="0.5"
              value={mobilityRequest.distance_km}
              onChange={(e) => handleDistanceChange(parseFloat(e.target.value))}
              className="flex-1 accent-emerald-500 cursor-pointer"
            />
            <div className="flex items-center gap-1.5 shrink-0">
              {distancePresets.map((km) => (
                <button
                  key={km}
                  onClick={() => handleDistanceChange(km)}
                  className={`text-xs px-2.5 py-1 rounded-lg border font-medium transition-all ${
                    mobilityRequest.distance_km === km
                      ? 'bg-emerald-500/20 border-emerald-500 text-emerald-300'
                      : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-white'
                  }`}
                >
                  {km} km
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Current Transport Mode Selection */}
        <div className="space-y-2 pt-2">
          <label className="text-xs font-semibold text-slate-300">
            {t.currentModeLabel}
          </label>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-2">
            {[
              { id: 'petrol_car', label: isHi ? 'पेट्रोल कार' : 'Petrol Car', icon: Car },
              { id: 'two_wheeler', label: isHi ? 'पेट्रोल बाइक' : '2-Wheeler', icon: Bike },
              { id: 'cng_auto', label: isHi ? 'सीएनजी ऑटो' : 'CNG Auto', icon: Car },
              { id: 'electric_car', label: isHi ? 'इलेक्ट्रिक कार' : 'Electric Car', icon: Zap },
              { id: 'public_bus', label: isHi ? 'पब्लिक बस' : 'Public Bus', icon: Bus },
              { id: 'metro', label: isHi ? 'मेट्रो रेल' : 'Metro Rail', icon: Train },
            ].map((m) => {
              const Icon = m.icon;
              const isSelected = mobilityRequest.current_mode === m.id;
              return (
                <button
                  key={m.id}
                  onClick={() =>
                    updateMobilityRequest({ current_mode: m.id as TransportMode })
                  }
                  className={`flex flex-col items-center justify-center gap-1.5 p-3 rounded-xl border transition-all ${
                    isSelected
                      ? 'bg-emerald-500/15 border-emerald-500/60 text-white shadow-md shadow-emerald-500/10'
                      : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-slate-200'
                  }`}
                >
                  <Icon
                    className={`w-5 h-5 ${
                      isSelected ? 'text-emerald-400' : 'text-slate-400'
                    }`}
                  />
                  <span className="text-xs font-medium text-center">{m.label}</span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Purpose, Frequency, Accessibility, Occupancy Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 pt-2">
          {/* Purpose */}
          <div className="space-y-1">
            <label className="text-[11px] font-semibold text-slate-400">
              {t.commutePurposeLabel}
            </label>
            <select
              value={mobilityRequest.purpose || 'office'}
              onChange={(e) =>
                updateMobilityRequest({ purpose: e.target.value as CommutePurpose })
              }
              className="w-full bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-500"
            >
              <option value="office">{isHi ? 'कार्यालय आवागमन (Office)' : 'Daily Office'}</option>
              <option value="school_college">
                {isHi ? 'स्कूल / कॉलेज (Education)' : 'School / College'}
              </option>
              <option value="errands">{isHi ? 'खरीदारी / आवश्यक कार्य' : 'Errands & Shopping'}</option>
              <option value="healthcare">{isHi ? 'चिकित्सा / अस्पताल' : 'Healthcare Visit'}</option>
              <option value="leisure">{isHi ? 'मनोरंजन / सामाजिक' : 'Leisure & Social'}</option>
            </select>
          </div>

          {/* Frequency */}
          <div className="space-y-1">
            <label className="text-[11px] font-semibold text-slate-400">
              {t.commuteFrequencyLabel}
            </label>
            <select
              value={mobilityRequest.frequency || 'daily_round_trip'}
              onChange={(e) =>
                updateMobilityRequest({ frequency: e.target.value as CommuteFrequency })
              }
              className="w-full bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-500"
            >
              <option value="daily_round_trip">
                {isHi ? 'दैनिक राउंड-ट्रिप (2 बार)' : 'Daily Round-Trip (2 trips)'}
              </option>
              <option value="weekdays_only">
                {isHi ? 'सोमवार से शुक्रवार (Weekdays)' : 'Weekdays Only (5 days)'}
              </option>
              <option value="one_way">{isHi ? 'एक तरफा यात्रा (One-Way)' : 'One-Way Trip'}</option>
              <option value="occasional">
                {isHi ? 'साप्ताहिक / कभी-कभार' : 'Occasional Travel'}
              </option>
            </select>
          </div>

          {/* Accessibility */}
          <div className="space-y-1">
            <label className="text-[11px] font-semibold text-slate-400">
              {t.accessibilityLabel}
            </label>
            <select
              value={mobilityRequest.accessibility || 'none'}
              onChange={(e) =>
                updateMobilityRequest({
                  accessibility: e.target.value as AccessibilityNeed,
                })
              }
              className="w-full bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-500"
            >
              <option value="none">{isHi ? 'कोई नहीं (मानक)' : 'None (Standard)'}</option>
              <option value="wheelchair">
                {isHi ? 'व्हीलचेयर सुलभ (Wheelchair)' : 'Wheelchair Accessible'}
              </option>
              <option value="low_walking">
                {isHi ? 'न्यूनतम पैदल चलना (Low Walking)' : 'Low Walking Tolerance'}
              </option>
              <option value="senior_friendly">
                {isHi ? 'वरिष्ठ नागरिक अनुकूल' : 'Senior-Friendly'}
              </option>
              <option value="child_friendly">
                {isHi ? 'बाल-सुलभ (Child-Friendly)' : 'Child-Friendly'}
              </option>
            </select>
          </div>

          {/* Occupancy */}
          <div className="space-y-1">
            <label className="text-[11px] font-semibold text-slate-400">
              {t.vehicleOccupancyLabel}
            </label>
            <select
              value={mobilityRequest.occupancy || 1}
              onChange={(e) =>
                updateMobilityRequest({ occupancy: parseInt(e.target.value, 10) })
              }
              className="w-full bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-500"
            >
              <option value={1}>{isHi ? '1 यात्री (अकेले चालक)' : '1 Person (Solo Driver)'}</option>
              <option value={2}>{isHi ? '2 यात्री (कार साझा)' : '2 Persons (Carpool)'}</option>
              <option value={3}>{isHi ? '3 यात्री (साझा सफर)' : '3 Persons'}</option>
              <option value={4}>{isHi ? '4 यात्री (पूर्ण कार)' : '4 Persons (Full Car)'}</option>
            </select>
          </div>
        </div>
      </div>

      {/* 3. Hero Recommended Mode Card */}
      {plan && (
        <div className="glass-card rounded-2xl p-5 border border-emerald-500/30 bg-gradient-to-br from-emerald-950/20 via-slate-900 to-slate-900 space-y-3">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div className="flex items-center gap-3">
              <div className="p-3 rounded-2xl bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                {modeIcons[plan.recommended_mode] || <Train className="w-6 h-6" />}
              </div>
              <div>
                <p className="text-[11px] font-semibold uppercase tracking-wider text-emerald-400">
                  {t.recommendedModeTitle}
                </p>
                <h3 className="text-lg font-bold text-white">
                  {plan.recommended_mode_label}
                </h3>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <div className="px-3 py-1.5 rounded-xl bg-slate-900/90 border border-slate-800 text-right">
                <p className="text-[10px] text-slate-400">
                  {isHi ? 'अनुमानित बचत' : 'Potential Reduction'}
                </p>
                <strong className="text-emerald-400 font-bold text-sm">
                  {plan.mode_comparisons.find((m) => m.mode === plan.recommended_mode)
                    ?.co2e_savings_pct || 85}
                  % vs Solo Car
                </strong>
              </div>
            </div>
          </div>

          <p className="text-xs text-slate-300 leading-relaxed bg-slate-900/60 p-3 rounded-xl border border-slate-800/80">
            {plan.recommended_mode_reason}
          </p>
        </div>
      )}

      {/* 4. Active Mobility & Inversion Smog Advisory Banner */}
      {plan && (
        <div
          className={`rounded-2xl p-4 border flex items-start gap-3 ${
            plan.aqi >= 301
              ? 'bg-rose-500/10 border-rose-500/30 text-rose-300'
              : plan.aqi >= 201
              ? 'bg-amber-500/10 border-amber-500/30 text-amber-300'
              : 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
          }`}
        >
          {plan.aqi >= 301 ? (
            <ShieldAlert className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" />
          ) : plan.aqi >= 201 ? (
            <AlertCircle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
          ) : (
            <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
          )}
          <div className="space-y-1">
            <h4 className="text-xs font-bold uppercase tracking-wider">
              {t.activeMobilityAlertTitle}
            </h4>
            <p className="text-xs leading-relaxed text-slate-200">
              {plan.active_mobility_advisory}
            </p>
          </div>
        </div>
      )}

      {/* 5. Carpooling Impact Widget */}
      {plan?.carpool_potential && (
        <div className="glass-card rounded-2xl p-5 border border-slate-800 space-y-4">
          <div>
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <Users className="w-4 h-4 text-indigo-400" />
              <span>{t.carpoolWidgetTitle}</span>
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">{t.carpoolWidgetSubtitle}</p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
            <div className="rounded-xl p-3 bg-slate-900 border border-slate-800 space-y-1">
              <span className="text-[10px] text-slate-400 uppercase tracking-wide">
                {t.soloBaselineLabel}
              </span>
              <p className="text-base font-bold text-rose-400 font-mono">
                {plan.carpool_potential.solo_trip_emissions_g} g CO2e
              </p>
              <span className="text-[10px] text-slate-400">100% emission load</span>
            </div>

            <div className="rounded-xl p-3 bg-slate-900 border border-slate-800 space-y-1">
              <span className="text-[10px] text-slate-400 uppercase tracking-wide">
                2-Person Pool:
              </span>
              <p className="text-base font-bold text-amber-400 font-mono">
                {plan.carpool_potential.shared_2_person_emissions_g} g / person
              </p>
              <span className="text-[10px] text-emerald-400 font-medium">50% reduction</span>
            </div>

            <div className="rounded-xl p-3 bg-slate-900 border border-indigo-500/30 space-y-1">
              <span className="text-[10px] text-indigo-300 uppercase tracking-wide">
                {t.shared3PersonLabel}
              </span>
              <p className="text-base font-bold text-indigo-400 font-mono">
                {plan.carpool_potential.shared_3_person_emissions_g} g / person
              </p>
              <span className="text-[10px] text-emerald-400 font-medium">67% reduction</span>
            </div>

            <div className="rounded-xl p-3 bg-slate-900 border border-slate-800 space-y-1">
              <span className="text-[10px] text-slate-400 uppercase tracking-wide">
                4-Person Pool:
              </span>
              <p className="text-base font-bold text-emerald-400 font-mono">
                {plan.carpool_potential.shared_4_person_emissions_g} g / person
              </p>
              <span className="text-[10px] text-emerald-400 font-medium">75% reduction</span>
            </div>
          </div>

          <div className="flex flex-wrap items-center justify-between gap-2 pt-2 border-t border-slate-800/80 text-xs">
            <span className="text-slate-300">
              {t.dailyAvoidedLabel}{' '}
              <strong className="text-emerald-400 font-bold">
                {plan.carpool_potential.daily_savings_kg} kg CO2e
              </strong>
            </span>
            <span className="text-slate-300">
              {t.annualAvoidedLabel}{' '}
              <strong className="text-emerald-400 font-bold">
                {plan.carpool_potential.annual_savings_kg} kg CO2e
              </strong>
            </span>
          </div>
        </div>
      )}

      {/* 6. Mode Carbon Emissions Comparison Grid */}
      {plan && (
        <div className="space-y-3">
          <div>
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <Leaf className="w-4 h-4 text-emerald-400" />
              <span>{t.modeComparisonTitle}</span>
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              {isHi
                ? 'सभी 12 साधनों के प्रति-यात्री कार्बन उत्सर्जन व AQI स्वास्थ्य सुरक्षा का तुलनात्मक विश्लेषण'
                : 'Per-passenger carbon footprint and AQI health suitability across 12 urban transit modes'}
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {plan.mode_comparisons.map((item) => {
              const isSelected = item.mode === plan.current_mode;
              const isRecommended = item.mode === plan.recommended_mode;

              return (
                <div
                  key={item.mode}
                  className={`glass-card rounded-2xl p-4 border transition-all flex flex-col justify-between space-y-3 ${
                    isRecommended
                      ? 'border-emerald-500/50 bg-emerald-950/10 shadow-lg shadow-emerald-500/5'
                      : isSelected
                      ? 'border-blue-500/40 bg-blue-950/10'
                      : 'border-slate-800'
                  }`}
                >
                  <div>
                    {/* Mode Header */}
                    <div className="flex items-start justify-between gap-2 mb-2">
                      <div className="flex items-center gap-2.5">
                        <div className="p-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-300">
                          {modeIcons[item.mode] || <Car className="w-4 h-4" />}
                        </div>
                        <div>
                          <h4 className="text-xs font-bold text-white">{item.label}</h4>
                          <span className="text-[10px] text-slate-400">
                            {item.mode === 'metro' || item.mode === 'electric_bus'
                              ? isHi
                                ? 'ग्रिड-संचालित (विद्युत)'
                                : 'Electric Grid Mass Transit'
                              : item.mode === 'walking' || item.mode === 'cycling'
                              ? isHi
                                ? 'शून्य टेलपाइप उत्सर्जन'
                                : 'Zero Tailpipe Active'
                              : isHi
                              ? 'सड़क परिवहन'
                              : 'Road Transit'}
                          </span>
                        </div>
                      </div>

                      <div className="flex flex-col items-end gap-1">
                        <span
                          className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${
                            item.suitability_score.includes('Optimal') ||
                            item.suitability_score.includes('सर्वोत्तम')
                              ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30'
                              : item.suitability_score.includes('Recommended') ||
                                item.suitability_score.includes('अनुशंसित')
                              ? 'bg-blue-500/20 text-blue-300 border-blue-500/30'
                              : item.suitability_score.includes('Caution') ||
                                item.suitability_score.includes('सावधानी')
                              ? 'bg-amber-500/20 text-amber-300 border-amber-500/30'
                              : 'bg-rose-500/20 text-rose-300 border-rose-500/30'
                          }`}
                        >
                          {item.suitability_score}
                        </span>
                        {isRecommended && (
                          <span className="text-[9px] font-bold text-emerald-400 uppercase tracking-wider">
                            ★ {isHi ? 'सर्वोत्तम' : 'Top Pick'}
                          </span>
                        )}
                      </div>
                    </div>

                    {/* Emissions Data */}
                    <div className="grid grid-cols-2 gap-2 bg-slate-900/70 p-2.5 rounded-xl border border-slate-800/80 my-2 text-center">
                      <div>
                        <span className="text-[10px] text-slate-400 block">
                          {t.perPassengerEmissionsLabel}
                        </span>
                        <strong className="text-xs font-bold text-white font-mono">
                          {item.per_passenger_emissions_g} g CO2e
                        </strong>
                      </div>
                      <div>
                        <span className="text-[10px] text-slate-400 block">
                          {t.co2eSavingsLabel}
                        </span>
                        <strong
                          className={`text-xs font-bold font-mono ${
                            item.co2e_savings_pct > 50
                              ? 'text-emerald-400'
                              : item.co2e_savings_pct > 0
                              ? 'text-blue-400'
                              : 'text-slate-400'
                          }`}
                        >
                          {item.co2e_savings_pct > 0 ? `-${item.co2e_savings_pct}%` : 'Baseline'}
                        </strong>
                      </div>
                    </div>

                    {/* AQI Safety Verdict */}
                    <p className="text-[11px] text-slate-300 leading-tight">
                      {item.aqi_safety_verdict}
                    </p>
                  </div>

                  {/* Precautions Chips */}
                  {item.precautions && item.precautions.length > 0 && (
                    <div className="pt-2 border-t border-slate-800/60 space-y-1">
                      {item.precautions.map((p, pIdx) => (
                        <div key={pIdx} className="flex items-center gap-1.5 text-[10px] text-slate-400">
                          <CheckCircle2 className="w-3 h-3 text-emerald-400 shrink-0" />
                          <span>{p}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* 7. AI Personalized Mobility Strategy Card */}
      {plan?.ai_recommendation && (
        <div className="glass-card rounded-2xl p-5 border border-slate-800 space-y-3">
          <div className="flex items-center justify-between border-b border-slate-800 pb-2">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-purple-400" />
              <span>
                {isHi
                  ? 'AI वैयक्तिकृत आवागमन रणनीति'
                  : 'AI Personalized Commute Strategy'}
              </span>
            </h3>
            <span className="text-[11px] text-slate-400 font-mono">
              CPCB: {plan.station_name} • AQI {plan.aqi} •{' '}
              {plan.is_demo_data ? 'Demo' : 'Live'}
            </span>
          </div>

          <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800/60">
            {renderFormattedText(plan.ai_recommendation)}
          </div>
        </div>
      )}

      {/* 8. Methodology & Emission Assumptions Accordion */}
      {plan?.methodology_notes && (
        <div className="glass-card rounded-2xl border border-slate-800 overflow-hidden">
          <button
            onClick={() => setShowMethodology(!showMethodology)}
            className="w-full flex items-center justify-between p-4 text-left text-xs font-semibold text-slate-300 hover:text-white transition-colors"
          >
            <div className="flex items-center gap-2">
              <Info className="w-4 h-4 text-emerald-400" />
              <span>{t.methodologyNotesTitle}</span>
            </div>
            {showMethodology ? (
              <ChevronUp className="w-4 h-4 text-slate-400" />
            ) : (
              <ChevronDown className="w-4 h-4 text-slate-400" />
            )}
          </button>

          {showMethodology && (
            <div className="p-4 pt-0 space-y-2 border-t border-slate-800/60 text-xs text-slate-400 leading-relaxed">
              <ul className="space-y-1.5 pl-4 list-disc marker:text-emerald-400">
                {plan.methodology_notes.map((note, idx) => (
                  <li key={idx}>{note}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* 9. Environmental & Health Disclaimer */}
      {plan?.disclaimer && (
        <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800 text-[11px] text-slate-400 flex items-start gap-2">
          <Info className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
          <p className="leading-relaxed">{plan.disclaimer}</p>
        </div>
      )}
    </div>
  );
};
