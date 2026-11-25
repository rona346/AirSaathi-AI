import React from 'react';
import {
  Users,
  Shield,
  HeartPulse,
  Wind,
  AlertTriangle,
  AlertCircle,
  CheckCircle2,
  Sparkles,
  RefreshCw,
  Info,
  Sliders,
  Baby,
  Smile,
  User,
  UserCheck,
  Flame,
  Fan,
  Gauge,
  Bus,
  Clock,
  Radio,
  Cloud,
  ChevronRight,
  Plus,
  Minus,
} from 'lucide-react';
import { useApp } from '../../context/AppContext';
import { translations } from '../../utils/translations';
import { getAqiBadgeClasses } from '../../utils/aqiUtils';
import { AlertThresholdPreference, PersonalizedActionItem } from '../../types/user';

export const FamilyProfileAssistant: React.FC = () => {
  const {
    householdSize,
    demographics,
    cleanAirPreferences,
    personalizedAdvisory,
    advisoryLoading,
    advisoryError,
    updateHouseholdSize,
    updateDemographics,
    updateCleanAirPreferences,
    refreshPersonalizedAdvisory,
    selectedStationId,
    setSelectedStationId,
    stations,
    language,
    user,
    persistenceStatus,
    setAuthModalOpen,
  } = useApp();

  const t = translations[language];

  // Helper for Priority Badges
  const getPriorityBadge = (priority: string) => {
    switch (priority?.toLowerCase()) {
      case 'urgent':
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-rose-500/15 text-rose-400 border border-rose-500/30">
            <AlertTriangle className="w-3.5 h-3.5" />
            {t.priorityUrgent}
          </span>
        );
      case 'caution':
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-amber-500/15 text-amber-400 border border-amber-500/30">
            <AlertCircle className="w-3.5 h-3.5" />
            {t.priorityCaution}
          </span>
        );
      case 'good':
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
            <CheckCircle2 className="w-3.5 h-3.5" />
            {t.priorityGood}
          </span>
        );
      case 'advisory':
      default:
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-sky-500/15 text-sky-400 border border-sky-500/30">
            <Info className="w-3.5 h-3.5" />
            {t.priorityAdvisory}
          </span>
        );
    }
  };

  const getTargetGroupBadge = (target?: string | null) => {
    if (!target) return null;
    let label = target.toUpperCase();
    if (target === 'infants') label = language === 'hi' ? 'शिशु (0–2 वर्ष)' : 'Infants (0–2 yrs)';
    else if (target === 'children') label = language === 'hi' ? 'बच्चे (3–11 वर्ष)' : 'Children (3–11 yrs)';
    else if (target === 'seniors') label = language === 'hi' ? 'वरिष्ठ नागरिक (60+ वर्ष)' : 'Seniors (60+ yrs)';
    else if (target === 'adults') label = language === 'hi' ? 'वयस्क (18–59 वर्ष)' : 'Adults (18–59 yrs)';
    else if (target === 'all') label = language === 'hi' ? 'समस्त परिवार' : 'All Household';

    return (
      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-md text-xs font-medium bg-slate-800 text-slate-300 border border-slate-700">
        <Users className="w-3 h-3 text-cyan-400" />
        {label}
      </span>
    );
  };

  const handleHouseholdSizeChange = (delta: number) => {
    const next = Math.max(1, Math.min(20, householdSize + delta));
    updateHouseholdSize(next);
  };

  const handleThresholdChange = (threshold: AlertThresholdPreference) => {
    updateCleanAirPreferences({ alert_threshold: threshold });
  };

  const handleTransitModeChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    updateCleanAirPreferences({ preferred_transit_mode: e.target.value });
  };

  return (
    <div className="space-y-6 animate-fade-in pb-12">
      {/* 1. Module Header */}
      <div className="glass-panel rounded-2xl p-6 border border-white/10 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl -z-10 pointer-events-none" />

        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          <div className="space-y-1.5">
            <div className="flex items-center gap-2.5">
              <div className="p-2.5 rounded-xl bg-cyan-500/20 text-cyan-400 border border-cyan-500/30">
                <Users className="w-6 h-6" />
              </div>
              <div>
                <h1 className="text-2xl font-extrabold text-white tracking-tight flex items-center gap-2">
                  {t.familyTabTitle}
                  <span className="text-xs px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-300 font-mono font-medium border border-cyan-500/30">
                    Module 7
                  </span>
                </h1>
                <p className="text-sm text-slate-400">{t.familyHeaderSubtitle}</p>
              </div>
            </div>
          </div>

          {/* Right Controls: Station Selector, Provenance, Refresh */}
          <div className="flex flex-wrap items-center gap-3">
            {/* Station dropdown */}
            <div className="relative">
              <select
                aria-label="Select Monitoring Station"
                value={selectedStationId}
                onChange={(e) => setSelectedStationId(e.target.value)}
                className="appearance-none bg-slate-900/90 text-sm text-slate-200 border border-slate-700/80 rounded-xl px-4 py-2 pr-9 font-medium focus:outline-none focus:ring-2 focus:ring-cyan-500/50"
              >
                {stations.map((st) => (
                  <option key={st.id} value={st.id} className="bg-slate-900 text-slate-200">
                    {st.name} ({st.city})
                  </option>
                ))}
              </select>
              <ChevronRight className="w-4 h-4 text-slate-400 absolute right-3 top-1/2 -translate-y-1/2 rotate-90 pointer-events-none" />
            </div>

            {/* Telemetry provenance badge */}
            {personalizedAdvisory?.status === 'unavailable' ? (
              <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold bg-amber-500/15 text-amber-400 border border-amber-500/30">
                <AlertTriangle className="w-3.5 h-3.5" />
                {t.telemetryUnavailable}
              </span>
            ) : personalizedAdvisory?.is_demo_data ? (
              <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold bg-indigo-500/15 text-indigo-300 border border-indigo-500/30">
                <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
                {t.telemetryDemo}
              </span>
            ) : (
              <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold bg-emerald-500/15 text-emerald-300 border border-emerald-500/30">
                <Radio className="w-3.5 h-3.5 text-emerald-400 animate-pulse" />
                {t.telemetryActive}
              </span>
            )}

            {/* Cloud Sync / Guest status */}
            {user ? (
              <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-medium bg-slate-800/80 text-emerald-400 border border-emerald-500/20">
                <Cloud className="w-3.5 h-3.5" />
                {persistenceStatus === 'saving' ? t.cloudSaving : t.cloudSynced}
              </span>
            ) : (
              <button
                type="button"
                onClick={() => setAuthModalOpen(true)}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-medium bg-slate-800/80 text-slate-300 hover:text-white border border-slate-700 transition-colors"
                title={t.preferencesGuestNotice}
              >
                <Users className="w-3.5 h-3.5 text-cyan-400" />
                {t.guestModeLabel}
              </button>
            )}

            {/* Refresh Button */}
            <button
              type="button"
              onClick={() => refreshPersonalizedAdvisory()}
              disabled={advisoryLoading}
              aria-label={t.refreshBtn}
              className="p-2 rounded-xl bg-slate-800 text-slate-300 hover:text-white hover:bg-slate-700/80 border border-slate-700/80 transition-all disabled:opacity-50"
              title={t.refreshBtn}
            >
              <RefreshCw className={`w-4 h-4 ${advisoryLoading ? 'animate-spin text-cyan-400' : ''}`} />
            </button>
          </div>
        </div>
      </div>

      {/* 2. Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Household Configuration (5 cols) */}
        <div className="lg:col-span-5 space-y-6">
          {/* Card 1: Household Structure & Size Stepper */}
          <div className="glass-card rounded-2xl p-5 border border-white/10 space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Users className="w-5 h-5 text-cyan-400" />
                <h2 className="text-base font-bold text-white">{t.householdSectionTitle}</h2>
              </div>
              <span className="text-xs text-slate-400">{t.householdSizeLabel}</span>
            </div>

            <div className="flex items-center justify-between p-4 rounded-xl bg-slate-900/60 border border-slate-800">
              <div>
                <p className="text-sm font-medium text-slate-200">{t.householdSizeLabel}</p>
                <p className="text-xs text-slate-400">{t.householdSizeDesc}</p>
              </div>
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={() => handleHouseholdSizeChange(-1)}
                  disabled={householdSize <= 1}
                  className="w-8 h-8 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 flex items-center justify-center transition-colors disabled:opacity-40 disabled:cursor-not-allowed border border-slate-700"
                  aria-label="Decrease household size"
                >
                  <Minus className="w-4 h-4" />
                </button>
                <span className="w-10 text-center font-bold text-lg text-white font-mono">
                  {householdSize}
                </span>
                <button
                  type="button"
                  onClick={() => handleHouseholdSizeChange(1)}
                  disabled={householdSize >= 20}
                  className="w-8 h-8 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 flex items-center justify-center transition-colors disabled:opacity-40 disabled:cursor-not-allowed border border-slate-700"
                  aria-label="Increase household size"
                >
                  <Plus className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* Zero Personal Data Privacy Guarantee */}
            <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800/80 text-xs text-slate-400 flex items-start gap-2.5">
              <Shield className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
              <span>
                <strong>Zero Personal Data Guarantee:</strong> AirSaathi uses broad demographic vulnerability flags only. No individual personal records, names, or clinical records are collected.
              </span>
            </div>
          </div>

          {/* Card 2: Age-Group Demographics Toggles */}
          <div className="glass-card rounded-2xl p-5 border border-white/10 space-y-4">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <HeartPulse className="w-5 h-5 text-rose-400" />
                <h2 className="text-base font-bold text-white">{t.demographicsTitle}</h2>
              </div>
              <p className="text-xs text-slate-400">{t.demographicsDesc}</p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
              {/* Infants */}
              <button
                type="button"
                aria-pressed={!!demographics.has_infants}
                onClick={() => updateDemographics({ has_infants: !demographics.has_infants })}
                className={`p-3.5 rounded-xl border text-left transition-all flex items-center justify-between ${
                  demographics.has_infants
                    ? 'bg-rose-500/15 border-rose-500/40 text-rose-200 shadow-sm shadow-rose-900/20'
                    : 'bg-slate-900/50 border-slate-800 text-slate-400 hover:border-slate-700'
                }`}
              >
                <div className="flex items-center gap-3">
                  <Baby className={`w-5 h-5 ${demographics.has_infants ? 'text-rose-400' : 'text-slate-500'}`} />
                  <div>
                    <p className="text-sm font-semibold">{t.hasInfantsLabel}</p>
                    <p className="text-xs text-slate-400">0 – 2 yrs</p>
                  </div>
                </div>
                {demographics.has_infants && <CheckCircle2 className="w-4 h-4 text-rose-400" />}
              </button>

              {/* Children */}
              <button
                type="button"
                aria-pressed={!!demographics.has_children}
                onClick={() => updateDemographics({ has_children: !demographics.has_children })}
                className={`p-3.5 rounded-xl border text-left transition-all flex items-center justify-between ${
                  demographics.has_children
                    ? 'bg-amber-500/15 border-amber-500/40 text-amber-200 shadow-sm shadow-amber-900/20'
                    : 'bg-slate-900/50 border-slate-800 text-slate-400 hover:border-slate-700'
                }`}
              >
                <div className="flex items-center gap-3">
                  <Smile className={`w-5 h-5 ${demographics.has_children ? 'text-amber-400' : 'text-slate-500'}`} />
                  <div>
                    <p className="text-sm font-semibold">{t.hasChildrenLabel}</p>
                    <p className="text-xs text-slate-400">3 – 11 yrs</p>
                  </div>
                </div>
                {demographics.has_children && <CheckCircle2 className="w-4 h-4 text-amber-400" />}
              </button>

              {/* Teens */}
              <button
                type="button"
                aria-pressed={!!demographics.has_teens}
                onClick={() => updateDemographics({ has_teens: !demographics.has_teens })}
                className={`p-3.5 rounded-xl border text-left transition-all flex items-center justify-between ${
                  demographics.has_teens
                    ? 'bg-cyan-500/15 border-cyan-500/40 text-cyan-200 shadow-sm shadow-cyan-900/20'
                    : 'bg-slate-900/50 border-slate-800 text-slate-400 hover:border-slate-700'
                }`}
              >
                <div className="flex items-center gap-3">
                  <User className={`w-5 h-5 ${demographics.has_teens ? 'text-cyan-400' : 'text-slate-500'}`} />
                  <div>
                    <p className="text-sm font-semibold">{t.hasTeensLabel}</p>
                    <p className="text-xs text-slate-400">12 – 17 yrs</p>
                  </div>
                </div>
                {demographics.has_teens && <CheckCircle2 className="w-4 h-4 text-cyan-400" />}
              </button>

              {/* Adults */}
              <button
                type="button"
                aria-pressed={!!demographics.has_adults}
                onClick={() => updateDemographics({ has_adults: !demographics.has_adults })}
                className={`p-3.5 rounded-xl border text-left transition-all flex items-center justify-between ${
                  demographics.has_adults
                    ? 'bg-indigo-500/15 border-indigo-500/40 text-indigo-200 shadow-sm shadow-indigo-900/20'
                    : 'bg-slate-900/50 border-slate-800 text-slate-400 hover:border-slate-700'
                }`}
              >
                <div className="flex items-center gap-3">
                  <UserCheck className={`w-5 h-5 ${demographics.has_adults ? 'text-indigo-400' : 'text-slate-500'}`} />
                  <div>
                    <p className="text-sm font-semibold">{t.hasAdultsLabel}</p>
                    <p className="text-xs text-slate-400">18 – 59 yrs</p>
                  </div>
                </div>
                {demographics.has_adults && <CheckCircle2 className="w-4 h-4 text-indigo-400" />}
              </button>

              {/* Seniors */}
              <button
                type="button"
                aria-pressed={!!demographics.has_seniors}
                onClick={() => updateDemographics({ has_seniors: !demographics.has_seniors })}
                className={`p-3.5 rounded-xl border text-left transition-all flex items-center justify-between sm:col-span-2 ${
                  demographics.has_seniors
                    ? 'bg-purple-500/15 border-purple-500/40 text-purple-200 shadow-sm shadow-purple-900/20'
                    : 'bg-slate-900/50 border-slate-800 text-slate-400 hover:border-slate-700'
                }`}
              >
                <div className="flex items-center gap-3">
                  <HeartPulse className={`w-5 h-5 ${demographics.has_seniors ? 'text-purple-400' : 'text-slate-500'}`} />
                  <div>
                    <p className="text-sm font-semibold">{t.hasSeniorsLabel}</p>
                    <p className="text-xs text-slate-400">60+ yrs (Cardiorespiratory vulnerability)</p>
                  </div>
                </div>
                {demographics.has_seniors && <CheckCircle2 className="w-4 h-4 text-purple-400" />}
              </button>
            </div>
          </div>

          {/* Card 3: AQI Alert Sensitivity Threshold */}
          <div className="glass-card rounded-2xl p-5 border border-white/10 space-y-4">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <Sliders className="w-5 h-5 text-amber-400" />
                <h2 className="text-base font-bold text-white">{t.alertThresholdTitle}</h2>
              </div>
              <p className="text-xs text-slate-400">{t.alertThresholdDesc}</p>
            </div>

            <div role="radiogroup" aria-label={t.alertThresholdTitle} className="grid grid-cols-1 gap-2.5">
              {/* Sensitive */}
              <button
                type="button"
                role="radio"
                aria-checked={cleanAirPreferences.alert_threshold === 'sensitive'}
                onClick={() => handleThresholdChange('sensitive')}
                className={`p-3.5 rounded-xl border text-left transition-all flex items-start justify-between ${
                  cleanAirPreferences.alert_threshold === 'sensitive'
                    ? 'bg-rose-500/15 border-rose-500/50 text-white ring-1 ring-rose-500/50'
                    : 'bg-slate-900/50 border-slate-800 text-slate-300 hover:border-slate-700'
                }`}
              >
                <div>
                  <p className="text-sm font-bold flex items-center gap-2">
                    {t.thresholdSensitive}
                    <span className="text-xs px-2 py-0.5 rounded bg-rose-500/20 text-rose-300 font-normal">
                      &gt; 100 AQI
                    </span>
                  </p>
                  <p className="text-xs text-slate-400 mt-1">
                    Precautionary alerts trigger early at Moderate AQI. Recommended for households with infants, respiratory conditions, or seniors.
                  </p>
                </div>
                {cleanAirPreferences.alert_threshold === 'sensitive' && (
                  <CheckCircle2 className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
                )}
              </button>

              {/* Standard */}
              <button
                type="button"
                role="radio"
                aria-checked={cleanAirPreferences.alert_threshold === 'standard' || !cleanAirPreferences.alert_threshold}
                onClick={() => handleThresholdChange('standard')}
                className={`p-3.5 rounded-xl border text-left transition-all flex items-start justify-between ${
                  cleanAirPreferences.alert_threshold === 'standard' || !cleanAirPreferences.alert_threshold
                    ? 'bg-amber-500/15 border-amber-500/50 text-white ring-1 ring-amber-500/50'
                    : 'bg-slate-900/50 border-slate-800 text-slate-300 hover:border-slate-700'
                }`}
              >
                <div>
                  <p className="text-sm font-bold flex items-center gap-2">
                    {t.thresholdStandard}
                    <span className="text-xs px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 font-normal">
                      &gt; 200 AQI
                    </span>
                  </p>
                  <p className="text-xs text-slate-400 mt-1">
                    Alerts trigger at CPCB Poor category. Aligned with national public health guidelines.
                  </p>
                </div>
                {(cleanAirPreferences.alert_threshold === 'standard' || !cleanAirPreferences.alert_threshold) && (
                  <CheckCircle2 className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
                )}
              </button>

              {/* High Tolerance */}
              <button
                type="button"
                role="radio"
                aria-checked={cleanAirPreferences.alert_threshold === 'high_tolerance'}
                onClick={() => handleThresholdChange('high_tolerance')}
                className={`p-3.5 rounded-xl border text-left transition-all flex items-start justify-between ${
                  cleanAirPreferences.alert_threshold === 'high_tolerance'
                    ? 'bg-indigo-500/15 border-indigo-500/50 text-white ring-1 ring-indigo-500/50'
                    : 'bg-slate-900/50 border-slate-800 text-slate-300 hover:border-slate-700'
                }`}
              >
                <div>
                  <p className="text-sm font-bold flex items-center gap-2">
                    {t.thresholdHighTolerance}
                    <span className="text-xs px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300 font-normal">
                      &gt; 300 AQI
                    </span>
                  </p>
                  <p className="text-xs text-slate-400 mt-1">
                    Elevated protocols activate only during Very Poor or Severe smog events.
                  </p>
                </div>
                {cleanAirPreferences.alert_threshold === 'high_tolerance' && (
                  <CheckCircle2 className="w-4 h-4 text-indigo-400 shrink-0 mt-0.5" />
                )}
              </button>
            </div>
          </div>

          {/* Card 4: Clean-Air Equipment Assets */}
          <div className="glass-card rounded-2xl p-5 border border-white/10 space-y-4">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <Wind className="w-5 h-5 text-emerald-400" />
                <h2 className="text-base font-bold text-white">{t.equipmentTitle}</h2>
              </div>
              <p className="text-xs text-slate-400">{t.equipmentDesc}</p>
            </div>

            <div className="space-y-2.5">
              {/* True HEPA Purifier */}
              <button
                type="button"
                aria-pressed={!!cleanAirPreferences.has_hepa_purifier}
                onClick={() =>
                  updateCleanAirPreferences({ has_hepa_purifier: !cleanAirPreferences.has_hepa_purifier })
                }
                className={`w-full p-3.5 rounded-xl border text-left transition-all flex items-center justify-between ${
                  cleanAirPreferences.has_hepa_purifier
                    ? 'bg-emerald-500/15 border-emerald-500/40 text-emerald-200'
                    : 'bg-slate-900/50 border-slate-800 text-slate-400 hover:border-slate-700'
                }`}
              >
                <div className="flex items-center gap-3">
                  <Fan className={`w-5 h-5 ${cleanAirPreferences.has_hepa_purifier ? 'text-emerald-400' : 'text-slate-500'}`} />
                  <div>
                    <p className="text-sm font-semibold">{t.hasHepaLabel}</p>
                    <p className="text-xs text-slate-400">99.97% particulate capture down to 0.3 µm</p>
                  </div>
                </div>
                {cleanAirPreferences.has_hepa_purifier && <CheckCircle2 className="w-4 h-4 text-emerald-400" />}
              </button>

              {/* Kitchen Chimney / Exhaust */}
              <button
                type="button"
                aria-pressed={!!cleanAirPreferences.has_kitchen_exhaust}
                onClick={() =>
                  updateCleanAirPreferences({ has_kitchen_exhaust: !cleanAirPreferences.has_kitchen_exhaust })
                }
                className={`w-full p-3.5 rounded-xl border text-left transition-all flex items-center justify-between ${
                  cleanAirPreferences.has_kitchen_exhaust
                    ? 'bg-amber-500/15 border-amber-500/40 text-amber-200'
                    : 'bg-slate-900/50 border-slate-800 text-slate-400 hover:border-slate-700'
                }`}
              >
                <div className="flex items-center gap-3">
                  <Flame className={`w-5 h-5 ${cleanAirPreferences.has_kitchen_exhaust ? 'text-amber-400' : 'text-slate-500'}`} />
                  <div>
                    <p className="text-sm font-semibold">{t.hasKitchenExhaustLabel}</p>
                    <p className="text-xs text-slate-400">Tadka and frying emissions extraction</p>
                  </div>
                </div>
                {cleanAirPreferences.has_kitchen_exhaust && <CheckCircle2 className="w-4 h-4 text-amber-400" />}
              </button>

              {/* Indoor Monitor */}
              <button
                type="button"
                aria-pressed={!!cleanAirPreferences.has_indoor_monitor}
                onClick={() =>
                  updateCleanAirPreferences({ has_indoor_monitor: !cleanAirPreferences.has_indoor_monitor })
                }
                className={`w-full p-3.5 rounded-xl border text-left transition-all flex items-center justify-between ${
                  cleanAirPreferences.has_indoor_monitor
                    ? 'bg-cyan-500/15 border-cyan-500/40 text-cyan-200'
                    : 'bg-slate-900/50 border-slate-800 text-slate-400 hover:border-slate-700'
                }`}
              >
                <div className="flex items-center gap-3">
                  <Gauge className={`w-5 h-5 ${cleanAirPreferences.has_indoor_monitor ? 'text-cyan-400' : 'text-slate-500'}`} />
                  <div>
                    <p className="text-sm font-semibold">{t.hasIndoorMonitorLabel}</p>
                    <p className="text-xs text-slate-400">Laser particulate verification</p>
                  </div>
                </div>
                {cleanAirPreferences.has_indoor_monitor && <CheckCircle2 className="w-4 h-4 text-cyan-400" />}
              </button>
            </div>
          </div>

          {/* Card 5: Commute Mode & Daily Activity Windows */}
          <div className="glass-card rounded-2xl p-5 border border-white/10 space-y-4">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <Bus className="w-5 h-5 text-indigo-400" />
                <h2 className="text-base font-bold text-white">{t.preferredTransitTitle}</h2>
              </div>
            </div>

            <div>
              <select
                id="preferred-transit-mode"
                aria-label={t.preferredTransitTitle}
                value={cleanAirPreferences.preferred_transit_mode || 'public_transit'}
                onChange={handleTransitModeChange}
                className="w-full bg-slate-900/80 text-sm text-slate-200 border border-slate-700 rounded-xl px-4 py-2.5 font-medium focus:outline-none focus:ring-2 focus:ring-cyan-500/50"
              >
                <option value="public_transit">Public Transit / City Bus</option>
                <option value="metro">Metro Rail</option>
                <option value="electric_bus">Electric City Feeder Bus</option>
                <option value="carpool">Shared Carpool / Rideshare</option>
                <option value="walking">Walking / Pedestrian</option>
                <option value="cycling">Bicycle Commute</option>
              </select>
            </div>

            <div className="pt-2 border-t border-slate-800">
              <div className="flex items-center gap-2 mb-3">
                <Clock className="w-4 h-4 text-slate-400" />
                <h3 className="text-sm font-semibold text-slate-200">{t.activityWindowsTitle}</h3>
              </div>

              <div className="grid grid-cols-2 gap-2 text-xs">
                <button
                  type="button"
                  aria-pressed={!!cleanAirPreferences.morning_outdoor_window}
                  onClick={() =>
                    updateCleanAirPreferences({
                      morning_outdoor_window: !cleanAirPreferences.morning_outdoor_window,
                    })
                  }
                  className={`p-2.5 rounded-lg border text-left transition-all ${
                    cleanAirPreferences.morning_outdoor_window
                      ? 'bg-cyan-500/15 border-cyan-500/40 text-cyan-300'
                      : 'bg-slate-900/60 border-slate-800 text-slate-400'
                  }`}
                >
                  <p className="font-semibold">{t.morningWindowLabel}</p>
                  <p className="text-[11px] text-slate-400">06:00 – 08:30</p>
                </button>

                <button
                  type="button"
                  aria-pressed={!!cleanAirPreferences.school_commute_active}
                  onClick={() =>
                    updateCleanAirPreferences({
                      school_commute_active: !cleanAirPreferences.school_commute_active,
                    })
                  }
                  className={`p-2.5 rounded-lg border text-left transition-all ${
                    cleanAirPreferences.school_commute_active
                      ? 'bg-cyan-500/15 border-cyan-500/40 text-cyan-300'
                      : 'bg-slate-900/60 border-slate-800 text-slate-400'
                  }`}
                >
                  <p className="font-semibold">{t.schoolCommuteLabel}</p>
                  <p className="text-[11px] text-slate-400">07:30 – 14:30</p>
                </button>

                <button
                  type="button"
                  aria-pressed={!!cleanAirPreferences.office_commute_active}
                  onClick={() =>
                    updateCleanAirPreferences({
                      office_commute_active: !cleanAirPreferences.office_commute_active,
                    })
                  }
                  className={`p-2.5 rounded-lg border text-left transition-all ${
                    cleanAirPreferences.office_commute_active
                      ? 'bg-cyan-500/15 border-cyan-500/40 text-cyan-300'
                      : 'bg-slate-900/60 border-slate-800 text-slate-400'
                  }`}
                >
                  <p className="font-semibold">{t.officeCommuteLabel}</p>
                  <p className="text-[11px] text-slate-400">08:30 – 18:30</p>
                </button>

                <button
                  type="button"
                  aria-pressed={!!cleanAirPreferences.evening_outdoor_window}
                  onClick={() =>
                    updateCleanAirPreferences({
                      evening_outdoor_window: !cleanAirPreferences.evening_outdoor_window,
                    })
                  }
                  className={`p-2.5 rounded-lg border text-left transition-all ${
                    cleanAirPreferences.evening_outdoor_window
                      ? 'bg-cyan-500/15 border-cyan-500/40 text-cyan-300'
                      : 'bg-slate-900/60 border-slate-800 text-slate-400'
                  }`}
                >
                  <p className="font-semibold">{t.eveningWindowLabel}</p>
                  <p className="text-[11px] text-slate-400">17:30 – 20:00</p>
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Personalized Smog Advisory & Safeguards (7 cols) */}
        <div className="lg:col-span-7 space-y-6">
          {/* Telemetry & Provenance Context Bar */}
          <div className="glass-card rounded-2xl p-5 border border-white/10 space-y-4">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <h2 className="text-lg font-extrabold text-white">{t.advisorySectionTitle}</h2>
                <p className="text-xs text-slate-400">{t.advisorySectionDesc}</p>
              </div>

              {personalizedAdvisory?.aqi != null && (() => {
                const badge = getAqiBadgeClasses(
                  ((personalizedAdvisory.category as any) || 'Moderate')
                );
                return (
                  <div className="flex items-center gap-2">
                    <div
                      className={`px-3 py-1.5 rounded-xl border text-sm font-extrabold font-mono flex items-center gap-1.5 ${badge.bg} ${badge.text} ${badge.border}`}
                    >
                      <span>AQI {personalizedAdvisory.aqi}</span>
                      <span className="text-xs font-sans font-medium px-1.5 py-0.5 rounded bg-black/20">
                        {personalizedAdvisory.category}
                      </span>
                    </div>
                  </div>
                );
              })()}
            </div>

            {/* Context details: Station, city, prominent pollutant, timestamp */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs">
              <div className="p-2.5 rounded-xl bg-slate-900/60 border border-slate-800">
                <span className="text-slate-400 block text-[11px]">Location</span>
                <span className="font-semibold text-slate-200 truncate block">
                  {personalizedAdvisory?.station_name || 'Anand Vihar'}
                </span>
              </div>
              <div className="p-2.5 rounded-xl bg-slate-900/60 border border-slate-800">
                <span className="text-slate-400 block text-[11px]">Pollutant</span>
                <span className="font-semibold text-slate-200">
                  {personalizedAdvisory?.prominent_pollutant || 'PM2.5'}
                </span>
              </div>
              <div className="p-2.5 rounded-xl bg-slate-900/60 border border-slate-800">
                <span className="text-slate-400 block text-[11px]">Sensitivity</span>
                <span className="font-semibold text-cyan-300 capitalize">
                  {cleanAirPreferences.alert_threshold || 'Standard'}
                </span>
              </div>
              <div className="p-2.5 rounded-xl bg-slate-900/60 border border-slate-800">
                <span className="text-slate-400 block text-[11px]">Data Source</span>
                <span className="font-semibold text-slate-200 truncate block">
                  {personalizedAdvisory?.data_source || 'Calibrated CPCB'}
                </span>
              </div>
            </div>

            {/* Active Household Safeguards Badges */}
            {personalizedAdvisory?.active_safeguards && personalizedAdvisory.active_safeguards.length > 0 && (
              <div className="pt-2 border-t border-slate-800">
                <p className="text-xs font-semibold text-slate-400 mb-2">{t.activeSafeguardsTitle}:</p>
                <div className="flex flex-wrap gap-1.5">
                  {personalizedAdvisory.active_safeguards.map((safeguard, idx) => (
                    <span
                      key={idx}
                      className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium bg-slate-800/90 text-slate-300 border border-slate-700/80"
                    >
                      <CheckCircle2 className="w-3 h-3 text-emerald-400" />
                      {safeguard}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Error State */}
          {advisoryError && (
            <div className="p-4 rounded-2xl bg-rose-500/10 border border-rose-500/30 text-rose-300 flex items-start gap-3">
              <AlertTriangle className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" />
              <div className="space-y-2">
                <p className="text-sm font-semibold">{advisoryError}</p>
                <button
                  type="button"
                  onClick={() => refreshPersonalizedAdvisory()}
                  className="px-3 py-1 rounded-lg text-xs font-semibold bg-rose-500/20 hover:bg-rose-500/30 border border-rose-500/40 text-rose-200 transition-colors"
                >
                  {t.retryBtn}
                </button>
              </div>
            </div>
          )}

          {/* Loading Skeletons */}
          {advisoryLoading && (
            <div className="space-y-4 animate-pulse">
              {[1, 2, 3].map((n) => (
                <div key={n} className="glass-card rounded-2xl p-5 border border-white/5 space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="h-4 w-28 bg-slate-800 rounded" />
                    <div className="h-4 w-20 bg-slate-800 rounded" />
                  </div>
                  <div className="h-5 w-3/4 bg-slate-800 rounded" />
                  <div className="h-12 w-full bg-slate-800 rounded" />
                  <div className="h-16 w-full bg-slate-900 rounded-xl" />
                </div>
              ))}
            </div>
          )}

          {/* Unavailable Telemetry Banner */}
          {!advisoryLoading && personalizedAdvisory?.status === 'unavailable' && (
            <div className="p-6 rounded-2xl bg-amber-500/10 border border-amber-500/30 text-amber-200 space-y-3">
              <div className="flex items-center gap-2">
                <AlertTriangle className="w-5 h-5 text-amber-400" />
                <h3 className="text-base font-bold text-white">{t.telemetryUnavailable}</h3>
              </div>
              <p className="text-sm text-slate-300 leading-relaxed">
                Reliable ambient air quality telemetry could not be resolved for this monitoring station. AirSaathi adheres strictly to zero-hallucination protocols: exposure-reduction advice is never synthesized without verified ambient readings.
              </p>
              <button
                type="button"
                onClick={() => refreshPersonalizedAdvisory()}
                className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-semibold bg-amber-500/20 hover:bg-amber-500/30 border border-amber-500/40 text-amber-100 transition-colors"
              >
                <RefreshCw className="w-3.5 h-3.5" />
                {t.retryBtn}
              </button>
            </div>
          )}

          {/* Personalized Action Cards */}
          {!advisoryLoading &&
            personalizedAdvisory?.status !== 'unavailable' &&
            personalizedAdvisory?.actions &&
            personalizedAdvisory.actions.length > 0 && (
              <div className="space-y-4">
                {personalizedAdvisory.actions.map((action: PersonalizedActionItem, idx: number) => (
                  <div
                    key={idx}
                    className="glass-card rounded-2xl p-5 border border-white/10 hover:border-slate-600 transition-all space-y-3"
                  >
                    {/* Header: Priority Badge + Target Group Badge */}
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <div className="flex items-center gap-2">
                        {getPriorityBadge(action.priority)}
                        {getTargetGroupBadge(action.target_group)}
                      </div>
                      <span className="text-xs uppercase font-mono tracking-wider text-slate-400">
                        {action.category}
                      </span>
                    </div>

                    {/* Action Title */}
                    <h3 className="text-base font-bold text-white leading-snug">{action.title}</h3>

                    {/* Action Description */}
                    <p className="text-sm text-slate-300 leading-relaxed">{action.description}</p>

                    {/* Scientific Rationale Box */}
                    {action.rationale && (
                      <div className="p-3.5 rounded-xl bg-slate-950/70 border border-slate-800/80 space-y-1">
                        <div className="flex items-center gap-1.5 text-xs font-semibold text-cyan-400">
                          <Sparkles className="w-3.5 h-3.5" />
                          <span>{t.scientificRationaleLabel}</span>
                        </div>
                        <p className="text-xs text-slate-400 leading-relaxed">{action.rationale}</p>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}

          {/* Non-Medical Scientific Disclaimer Banner */}
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800 text-xs text-slate-400 flex items-start gap-3">
            <Shield className="w-5 h-5 text-cyan-400 shrink-0 mt-0.5" />
            <div className="space-y-1">
              <p className="font-semibold text-slate-300">{t.disclaimerLabel}</p>
              <p className="leading-relaxed">
                {personalizedAdvisory?.disclaimer ||
                  'AirSaathi provides atmospheric exposure-mitigation guidance based on ambient air quality. This is not medical diagnosis, clinical treatment, or a health guarantee.'}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
