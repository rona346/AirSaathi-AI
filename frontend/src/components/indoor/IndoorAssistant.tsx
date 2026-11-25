import React from 'react';
import {
  Home,
  Wind,
  ShieldAlert,
  AlertTriangle,
  CheckCircle2,
  Sparkles,
  RefreshCw,
  Info,
  Flame,
  Fan,
  Sliders,
  CheckSquare,
  Bed,
  Utensils,
  Armchair,
  Baby,
  BookOpen,
  ChevronRight,
  Leaf,
  Layers,
} from 'lucide-react';
import { useApp } from '../../context/AppContext';
import { RoomType } from '../../types/indoor';
import { translations } from '../../utils/translations';
import { getAqiBadgeClasses } from '../../utils/aqiUtils';

export const IndoorAssistant: React.FC = () => {
  const {
    indoorAssessment,
    indoorLoading,
    refreshIndoorAssessment,
    language,
    householdInput,
    updateHouseholdInput,
  } = useApp();

  const t = translations[language];

  const getRiskBadge = (risk: string) => {
    switch (risk?.toLowerCase()) {
      case 'severe':
        return {
          bg: 'bg-rose-500/15',
          text: 'text-rose-400',
          border: 'border-rose-500/30',
          icon: ShieldAlert,
        };
      case 'high':
        return {
          bg: 'bg-amber-500/15',
          text: 'text-amber-400',
          border: 'border-amber-500/30',
          icon: AlertTriangle,
        };
      case 'moderate':
        return {
          bg: 'bg-yellow-500/15',
          text: 'text-yellow-400',
          border: 'border-yellow-500/30',
          icon: Info,
        };
      case 'low':
      default:
        return {
          bg: 'bg-emerald-500/15',
          text: 'text-emerald-400',
          border: 'border-emerald-500/30',
          icon: CheckCircle2,
        };
    }
  };

  const roomIcons: Record<RoomType, React.ReactNode> = {
    bedroom: <Bed className="w-4 h-4" />,
    kitchen: <Utensils className="w-4 h-4" />,
    living_room: <Armchair className="w-4 h-4" />,
    childrens_room: <Baby className="w-4 h-4" />,
    study_room: <BookOpen className="w-4 h-4" />,
  };

  const riskBadge = indoorAssessment ? getRiskBadge(indoorAssessment.qualitative_risk) : null;
  const RiskIcon = riskBadge?.icon || AlertTriangle;

  return (
    <div className="space-y-8">
      {/* 1. Header Banner with Qualitative Assessment */}
      <div className="glass-panel rounded-3xl p-6 sm:p-8 border border-slate-800 relative overflow-hidden">
        <div className="relative z-10 flex flex-col lg:flex-row lg:items-center justify-between gap-6">
          <div className="space-y-2">
            <div className="flex items-center flex-wrap gap-2.5">
              <span className="p-2.5 rounded-2xl bg-gradient-to-br from-emerald-500/20 to-teal-500/10 text-emerald-400 border border-emerald-500/30">
                <Home className="w-6 h-6" />
              </span>
              <h2 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
                {t.indoorTabTitle}
              </h2>
              {indoorAssessment && (
                <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/15 text-emerald-300 border border-emerald-500/30">
                  <Sparkles className="w-3.5 h-3.5 text-emerald-400" />
                  {indoorAssessment.ai_generated ? t.aiEngineBadge : t.ruleEngineBadge}
                </span>
              )}
            </div>

            <p className="text-xs sm:text-sm text-slate-300 max-w-3xl leading-relaxed">
              {t.indoorSubtitle}
            </p>

            {/* Ambient CPCB Infiltration Snapshot */}
            {indoorAssessment && (
              <div className="flex items-center flex-wrap gap-3 pt-2 text-xs text-slate-400">
                <span>
                  Outdoor Reference:{' '}
                  <strong className="text-white">
                    {indoorAssessment.station_name} ({indoorAssessment.city})
                  </strong>
                </span>
                <span>•</span>
                <span>
                  CPCB AQI:{' '}
                  <strong
                    className={`px-2 py-0.5 rounded-md font-bold border ${
                      getAqiBadgeClasses(indoorAssessment.outdoor_category as any).bg
                    } ${getAqiBadgeClasses(indoorAssessment.outdoor_category as any).text} ${
                      getAqiBadgeClasses(indoorAssessment.outdoor_category as any).border
                    }`}
                  >
                    {indoorAssessment.outdoor_aqi} ({indoorAssessment.outdoor_category})
                  </strong>
                </span>
                <span>•</span>
                <span>
                  {indoorAssessment.outdoor_is_demo && (
                    <span className="text-[10px] font-semibold uppercase px-2 py-0.5 rounded-full bg-amber-500/15 text-amber-400 border border-amber-500/30">
                      {t.demoMode}
                    </span>
                  )}
                </span>
              </div>
            )}
          </div>

          {/* Recalculate Button */}
          <button
            onClick={refreshIndoorAssessment}
            disabled={indoorLoading}
            className="flex items-center justify-center gap-2 px-5 py-3 rounded-2xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-bold text-xs shadow-lg shadow-emerald-500/20 transition-all disabled:opacity-50 shrink-0"
          >
            <RefreshCw className={`w-4 h-4 ${indoorLoading ? 'animate-spin' : ''}`} />
            <span>{indoorLoading ? t.calculating : t.recalculateBtn}</span>
          </button>
        </div>
      </div>

      {/* 2. Qualitative Risk Index & Sensor Transparency Notice */}
      {indoorAssessment && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          {/* Qualitative Risk Gauge Card */}
          <div className="glass-card rounded-2xl p-5 border border-slate-800 flex flex-col justify-between space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                {t.qualitativeRiskBadge}
              </span>
              {riskBadge && (
                <span
                  className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold border ${riskBadge.bg} ${riskBadge.text} ${riskBadge.border}`}
                >
                  <RiskIcon className="w-3.5 h-3.5" />
                  {indoorAssessment.qualitative_risk} {language === 'hi' ? 'जोखिम' : 'Risk'}
                </span>
              )}
            </div>

            <div>
              <div className="flex items-baseline gap-2 mb-2">
                <span className="text-3xl font-extrabold text-white">
                  {indoorAssessment.risk_score_numeric}
                </span>
                <span className="text-xs text-slate-400">/ 100</span>
                <span className="text-xs text-slate-400 ml-auto">{t.riskScoreLabel}</span>
              </div>

              {/* Visual Meter Bar */}
              <div className="w-full h-2 rounded-full bg-slate-900 border border-slate-800 overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all duration-500 ${
                    indoorAssessment.risk_score_numeric >= 75
                      ? 'bg-rose-500'
                      : indoorAssessment.risk_score_numeric >= 50
                      ? 'bg-amber-500'
                      : indoorAssessment.risk_score_numeric >= 25
                      ? 'bg-yellow-500'
                      : 'bg-emerald-500'
                  }`}
                  style={{ width: `${indoorAssessment.risk_score_numeric}%` }}
                />
              </div>
            </div>

            <p className="text-xs text-slate-300 leading-relaxed font-medium bg-slate-900/60 p-3 rounded-xl border border-slate-800/80">
              {indoorAssessment.risk_summary}
            </p>
          </div>

          {/* Sensor Transparency & Zero Synthetic Hallucination Disclosure */}
          <div className="lg:col-span-2 glass-card rounded-2xl p-5 border border-indigo-900/40 bg-indigo-950/20 flex flex-col justify-between space-y-3">
            <div className="flex items-center gap-2 text-indigo-400">
              <Info className="w-5 h-5 shrink-0" />
              <h4 className="text-sm font-bold uppercase tracking-wider">{t.sensorNoticeTitle}</h4>
            </div>

            <p className="text-xs text-slate-200 leading-relaxed bg-slate-900/80 p-3.5 rounded-xl border border-indigo-900/30">
              {indoorAssessment.sensor_notice}
            </p>

            <div className="flex items-center gap-2 text-[11px] text-indigo-300">
              <span className="w-2 h-2 rounded-full bg-indigo-400 animate-pulse" />
              <span>
                Connected Sensor Hardware:{' '}
                <strong>{indoorAssessment.has_connected_indoor_sensor ? 'Online' : 'None (Modeled Qualitative)'}</strong>
              </span>
            </div>
          </div>
        </div>
      )}

      {/* 3. Interactive Household & Room Configuration Toolbar */}
      <div className="glass-card rounded-2xl p-6 border border-slate-800 space-y-5">
        <div className="flex items-center gap-2 pb-2 border-b border-slate-800">
          <Sliders className="w-4 h-4 text-emerald-400" />
          <h3 className="text-sm font-bold text-white uppercase tracking-wider">
            {t.householdConfigTitle}
          </h3>
        </div>

        {/* Room Type Selector */}
        <div className="space-y-2">
          <label className="text-xs font-semibold text-slate-300 block">{t.roomTypeLabel}</label>
          <div role="radiogroup" aria-label={t.roomTypeLabel} className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-2">
            {[
              { id: 'bedroom', label: t.roomBedroom },
              { id: 'kitchen', label: t.roomKitchen },
              { id: 'living_room', label: t.roomLiving },
              { id: 'childrens_room', label: t.roomChildren },
              { id: 'study_room', label: t.roomStudy },
            ].map((rm) => (
              <button
                key={rm.id}
                role="radio"
                aria-checked={householdInput.room_type === rm.id}
                onClick={() => updateHouseholdInput({ room_type: rm.id as RoomType })}
                className={`flex items-center gap-2 px-3 py-2 rounded-xl text-xs font-semibold transition-all border ${
                  householdInput.room_type === rm.id
                    ? 'bg-emerald-600 text-white border-emerald-500 shadow-md shadow-emerald-500/20'
                    : 'bg-slate-900/80 hover:bg-slate-800 text-slate-300 border-slate-800'
                }`}
              >
                {roomIcons[rm.id as RoomType]}
                <span className="truncate">{rm.label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Room Area Selector */}
        <div className="space-y-2">
          <label className="text-xs font-semibold text-slate-300 block">
            {t.roomAreaLabel} <strong className="text-emerald-400">{householdInput.room_area_sqft} sq ft</strong>
          </label>
          <div role="radiogroup" aria-label={t.roomAreaLabel} className="flex items-center flex-wrap gap-2">
            {[100, 150, 200, 300, 500].map((sqft) => (
              <button
                key={sqft}
                role="radio"
                aria-checked={householdInput.room_area_sqft === sqft}
                onClick={() => updateHouseholdInput({ room_area_sqft: sqft })}
                className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition-all border ${
                  householdInput.room_area_sqft === sqft
                    ? 'bg-emerald-600 text-white border-emerald-500'
                    : 'bg-slate-900/80 text-slate-400 hover:text-white border-slate-800'
                }`}
              >
                {sqft} sq ft
              </button>
            ))}
          </div>
        </div>

        {/* Household Risk Factor Toggles */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 pt-2">
          {/* Heavy Tadka / Frying */}
          <button
            aria-pressed={householdInput.heavy_frying_or_tadka}
            onClick={() => updateHouseholdInput({ heavy_frying_or_tadka: !householdInput.heavy_frying_or_tadka })}
            className={`p-3 rounded-xl border text-left flex items-start justify-between gap-2 transition-all ${
              householdInput.heavy_frying_or_tadka
                ? 'bg-amber-500/15 text-amber-300 border-amber-500/30'
                : 'bg-slate-900/60 text-slate-400 border-slate-800'
            }`}
          >
            <div>
              <span className="text-xs font-bold block">{t.heavyFryingLabel}</span>
              <span className="text-[11px] opacity-80">Tempering & deep frying</span>
            </div>
            <Flame className="w-4 h-4 shrink-0 mt-0.5" />
          </button>

          {/* Kitchen Chimney */}
          <button
            aria-pressed={householdInput.has_kitchen_chimney}
            onClick={() => updateHouseholdInput({ has_kitchen_chimney: !householdInput.has_kitchen_chimney })}
            className={`p-3 rounded-xl border text-left flex items-start justify-between gap-2 transition-all ${
              householdInput.has_kitchen_chimney
                ? 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30'
                : 'bg-slate-900/60 text-slate-400 border-slate-800'
            }`}
          >
            <div>
              <span className="text-xs font-bold block">{t.chimneyLabel}</span>
              <span className="text-[11px] opacity-80">Ducted electric chimney</span>
            </div>
            <Fan className="w-4 h-4 shrink-0 mt-0.5" />
          </button>

          {/* Incense / Agarbatti */}
          <button
            aria-pressed={householdInput.burns_agarbatti_or_dhoop}
            onClick={() => updateHouseholdInput({ burns_agarbatti_or_dhoop: !householdInput.burns_agarbatti_or_dhoop })}
            className={`p-3 rounded-xl border text-left flex items-start justify-between gap-2 transition-all ${
              householdInput.burns_agarbatti_or_dhoop
                ? 'bg-rose-500/15 text-rose-300 border-rose-500/30'
                : 'bg-slate-900/60 text-slate-400 border-slate-800'
            }`}
          >
            <div>
              <span className="text-xs font-bold block">{t.incenseLabel}</span>
              <span className="text-[11px] opacity-80">Daily incense or mosquito coil</span>
            </div>
            <Flame className="w-4 h-4 shrink-0 mt-0.5" />
          </button>

          {/* Indoor Smoking */}
          <button
            aria-pressed={householdInput.indoor_smoking}
            onClick={() => updateHouseholdInput({ indoor_smoking: !householdInput.indoor_smoking })}
            className={`p-3 rounded-xl border text-left flex items-start justify-between gap-2 transition-all ${
              householdInput.indoor_smoking
                ? 'bg-rose-500/20 text-rose-300 border-rose-500/40'
                : 'bg-slate-900/60 text-slate-400 border-slate-800'
            }`}
          >
            <div>
              <span className="text-xs font-bold block">{t.smokingLabel}</span>
              <span className="text-[11px] opacity-80">Cigarette or bidi smoke</span>
            </div>
            <ShieldAlert className="w-4 h-4 shrink-0 mt-0.5" />
          </button>

          {/* Cleaning Method */}
          <button
            aria-pressed={householdInput.cleaning_method === 'wet_mopping'}
            onClick={() =>
              updateHouseholdInput({
                cleaning_method:
                  householdInput.cleaning_method === 'wet_mopping' ? 'dry_broom' : 'wet_mopping',
              })
            }
            className={`p-3 rounded-xl border text-left flex items-start justify-between gap-2 transition-all ${
              householdInput.cleaning_method === 'wet_mopping'
                ? 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30'
                : 'bg-amber-500/15 text-amber-300 border-amber-500/30'
            }`}
          >
            <div>
              <span className="text-xs font-bold block">{t.cleaningMethodLabel}</span>
              <span className="text-[11px] opacity-80">
                {householdInput.cleaning_method === 'wet_mopping'
                  ? t.wetMoppingOption
                  : t.dryBroomOption}
              </span>
            </div>
            <Layers className="w-4 h-4 shrink-0 mt-0.5" />
          </button>

          {/* Air Purifier Present */}
          <button
            aria-pressed={householdInput.has_air_purifier}
            onClick={() => updateHouseholdInput({ has_air_purifier: !householdInput.has_air_purifier })}
            className={`p-3 rounded-xl border text-left flex items-start justify-between gap-2 transition-all ${
              householdInput.has_air_purifier
                ? 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30'
                : 'bg-slate-900/60 text-slate-400 border-slate-800'
            }`}
          >
            <div>
              <span className="text-xs font-bold block">{t.purifierPresentLabel}</span>
              <span className="text-[11px] opacity-80">HEPA Air Purifier in room</span>
            </div>
            <Wind className="w-4 h-4 shrink-0 mt-0.5" />
          </button>
        </div>
      </div>

      {/* 4. Core Feature Cards: CADR Purifier, Smart Ventilation, Kitchen Smog */}
      {indoorAssessment && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* Card A: HEPA Purifier Sizing & CADR Calculator */}
          <div className="glass-card rounded-2xl p-5 border border-slate-800 flex flex-col justify-between space-y-4">
            <div>
              <div className="flex items-center gap-2 mb-3">
                <span className="p-2 rounded-xl bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
                  <Wind className="w-5 h-5" />
                </span>
                <h4 className="text-sm font-bold text-white leading-tight">
                  {t.purifierGuidanceTitle}
                </h4>
              </div>

              {/* Sizing Metrics */}
              <div className="grid grid-cols-2 gap-2 bg-slate-900/70 p-3 rounded-xl border border-slate-800 mb-3">
                <div>
                  <span className="text-[10px] text-slate-400 uppercase font-semibold block">
                    {t.recommendedCadrLabel}
                  </span>
                  <span className="text-lg font-extrabold text-white">
                    {indoorAssessment.purifier_guidance.recommended_min_cadr_m3h}{' '}
                    <span className="text-xs font-medium text-emerald-400">m³/h</span>
                  </span>
                  <span className="text-[10px] text-slate-400 block">
                    ({indoorAssessment.purifier_guidance.recommended_min_cadr_cfm} CFM)
                  </span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-400 uppercase font-semibold block">
                    {t.targetAchLabel}
                  </span>
                  <span className="text-lg font-extrabold text-white">
                    {indoorAssessment.purifier_guidance.target_ach}{' '}
                    <span className="text-xs font-medium text-emerald-400">ACH</span>
                  </span>
                  <span className="text-[10px] text-slate-400 block">Winter Smog Spec</span>
                </div>
              </div>

              <p className="text-xs text-slate-300 leading-relaxed font-medium mb-3">
                {indoorAssessment.purifier_guidance.filter_type_guidance}
              </p>

              {/* Maintenance Schedule */}
              <div className="text-xs text-slate-400 bg-slate-950/40 p-2.5 rounded-xl border border-slate-900 mb-3">
                <strong className="text-slate-300 block text-[11px] mb-0.5">Filter Maintenance:</strong>
                <span className="text-[11px] leading-relaxed">{indoorAssessment.purifier_guidance.maintenance_schedule}</span>
              </div>
            </div>

            {/* Placement Tips */}
            <div className="pt-3 border-t border-slate-800/80">
              <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-1.5">
                Placement Best Practices:
              </span>
              <ul className="space-y-1">
                {indoorAssessment.purifier_guidance.placement_tips.map((tip, i) => (
                  <li key={i} className="text-[11px] text-slate-300 flex items-start gap-1.5">
                    <ChevronRight className="w-3 h-3 text-emerald-400 shrink-0 mt-0.5" />
                    <span>{tip}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Card B: Smart Window Aeration Strategy */}
          <div className="glass-card rounded-2xl p-5 border border-slate-800 flex flex-col justify-between space-y-4">
            <div>
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <span className="p-2 rounded-xl bg-blue-500/15 text-blue-400 border border-blue-500/30">
                    <Fan className="w-5 h-5" />
                  </span>
                  <h4 className="text-sm font-bold text-white leading-tight">
                    {t.ventilationStrategyTitle}
                  </h4>
                </div>
                <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-blue-500/15 text-blue-300 border border-blue-500/30">
                  {indoorAssessment.ventilation.action}
                </span>
              </div>

              {/* Recommended Window Pill */}
              <div className="bg-slate-900/70 p-3 rounded-xl border border-slate-800 mb-3">
                <span className="text-[10px] text-slate-400 uppercase font-semibold block">
                  Optimal Aeration Window:
                </span>
                <div className="flex items-baseline justify-between mt-0.5">
                  <span className="text-sm font-bold text-white">
                    {indoorAssessment.ventilation.optimal_window}
                  </span>
                  <span className="text-xs font-semibold text-emerald-400">
                    {indoorAssessment.ventilation.duration_minutes} Mins Max
                  </span>
                </div>
              </div>

              {/* Rationale */}
              <p className="text-xs text-slate-300 leading-relaxed font-medium bg-slate-950/40 p-3 rounded-xl border border-slate-900 mb-3">
                {indoorAssessment.ventilation.rationale}
              </p>
            </div>

            {/* Precautions */}
            <div className="pt-3 border-t border-slate-800/80">
              <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-1.5">
                Ventilation Precautions:
              </span>
              <ul className="space-y-1">
                {indoorAssessment.ventilation.precautions.map((prec, i) => (
                  <li key={i} className="text-[11px] text-slate-300 flex items-start gap-1.5">
                    <ChevronRight className="w-3 h-3 text-blue-400 shrink-0 mt-0.5" />
                    <span>{prec}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Card C: Kitchen Smog & Gas Safety Protocol */}
          <div className="glass-card rounded-2xl p-5 border border-slate-800 flex flex-col justify-between space-y-4">
            <div>
              <div className="flex items-center gap-2 mb-3">
                <span className="p-2 rounded-xl bg-amber-500/15 text-amber-400 border border-amber-500/30">
                  <Utensils className="w-5 h-5" />
                </span>
                <h4 className="text-sm font-bold text-white leading-tight">
                  {t.kitchenManagementTitle}
                </h4>
              </div>

              {/* Risk Summary */}
              <p className="text-xs text-slate-300 leading-relaxed font-medium bg-slate-900/60 p-3 rounded-xl border border-slate-800/80 mb-3">
                {indoorAssessment.kitchen_guidance.risk_summary}
              </p>

              {/* 2-Minute Chimney Rule */}
              <div className="text-xs text-amber-300 bg-amber-950/20 p-2.5 rounded-xl border border-amber-900/40 mb-3">
                <strong className="text-amber-200 block text-[11px] mb-0.5">
                  2-Minute Pre-Exhaust Protocol:
                </strong>
                <span className="text-[11px] leading-relaxed">
                  {indoorAssessment.kitchen_guidance.chimney_exhaust_guidance}
                </span>
              </div>

              {/* Combustion Safety */}
              <div className="text-xs text-slate-400 bg-slate-950/40 p-2.5 rounded-xl border border-slate-900 mb-3">
                <strong className="text-slate-300 block text-[11px] mb-0.5">Gas Combustion Safety:</strong>
                <span className="text-[11px] leading-relaxed">
                  {indoorAssessment.kitchen_guidance.combustion_safety}
                </span>
              </div>
            </div>

            {/* Advice List */}
            <div className="pt-3 border-t border-slate-800/80">
              <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-1.5">
                Cooking Emission Controls:
              </span>
              <ul className="space-y-1">
                {indoorAssessment.kitchen_guidance.cooking_habits_advice.map((adv, i) => (
                  <li key={i} className="text-[11px] text-slate-300 flex items-start gap-1.5">
                    <ChevronRight className="w-3 h-3 text-amber-400 shrink-0 mt-0.5" />
                    <span>{adv}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* 5. Scientific Fact Check: Plant Myth Banner */}
      {indoorAssessment && (
        <div className="glass-card rounded-2xl p-5 border border-teal-900/40 bg-teal-950/20 flex flex-col md:flex-row items-start gap-4">
          <div className="p-2.5 rounded-xl bg-teal-500/20 text-teal-400 border border-teal-500/30 shrink-0 mt-0.5">
            <Leaf className="w-5 h-5" />
          </div>
          <div>
            <h4 className="text-sm font-bold text-white mb-1">{t.plantMythTitle}</h4>
            <p className="text-xs text-slate-300 leading-relaxed">
              {indoorAssessment.plant_myth_clarification}
            </p>
          </div>
        </div>
      )}

      {/* 6. Room-Wise Targeted Recommendations */}
      {indoorAssessment && indoorAssessment.room_recommendations && (
        <div className="space-y-4">
          <h3 className="text-base font-bold text-white flex items-center gap-2">
            <Layers className="w-5 h-5 text-emerald-400" />
            <span>{t.roomSpecificTitle}</span>
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Object.entries(indoorAssessment.room_recommendations).map(([key, rm]) => (
              <div
                key={key}
                className="glass-card rounded-2xl p-5 border border-slate-800 flex flex-col justify-between space-y-3"
              >
                <div>
                  <div className="flex items-center gap-2 pb-2 border-b border-slate-800/80 mb-2">
                    <div className="p-1.5 rounded-lg bg-slate-800 text-emerald-400">
                      {roomIcons[key as RoomType] || <Home className="w-4 h-4" />}
                    </div>
                    <h5 className="text-sm font-bold text-white">{rm.room_name}</h5>
                  </div>

                  {/* Primary Threats */}
                  <div className="mb-2">
                    <span className="text-[10px] uppercase font-semibold text-slate-400 block mb-1">
                      Primary Hazards:
                    </span>
                    <ul className="space-y-0.5">
                      {rm.primary_threats.map((threat, i) => (
                        <li key={i} className="text-[11px] text-slate-300 flex items-start gap-1.5">
                          <span className="w-1.5 h-1.5 rounded-full bg-rose-400 mt-1 shrink-0" />
                          <span>{threat}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Immediate Actions */}
                  <div className="mb-2">
                    <span className="text-[10px] uppercase font-semibold text-slate-400 block mb-1">
                      Immediate Action:
                    </span>
                    <ul className="space-y-0.5">
                      {rm.immediate_actions.map((act, i) => (
                        <li key={i} className="text-[11px] text-slate-200 flex items-start gap-1.5 font-medium">
                          <CheckCircle2 className="w-3 h-3 text-emerald-400 mt-0.5 shrink-0" />
                          <span>{act}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Night Protocol if present */}
                  {rm.night_protocol && (
                    <div className="mt-2 text-[11px] text-indigo-300 bg-indigo-950/30 p-2 rounded-lg border border-indigo-900/30">
                      <strong className="block text-indigo-200 text-[10px]">Night Protocol:</strong>
                      <span>{rm.night_protocol}</span>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 7. Actionable Clean Air Checklist */}
      {indoorAssessment && indoorAssessment.actionable_checklist && (
        <div className="glass-card rounded-2xl p-6 border border-slate-800 space-y-3">
          <div className="flex items-center gap-2 text-emerald-400">
            <CheckSquare className="w-5 h-5" />
            <h4 className="text-sm font-bold uppercase tracking-wide">{t.actionChecklistTitle}</h4>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-1">
            {indoorAssessment.actionable_checklist.map((item, i) => (
              <div
                key={i}
                className="flex items-start gap-2.5 p-3 rounded-xl bg-slate-900/80 border border-slate-800/80 text-xs text-slate-200 font-medium"
              >
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                <span className="leading-relaxed">{item}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 8. Medical & Environmental Disclaimer */}
      {indoorAssessment && (
        <div className="p-4 rounded-2xl bg-slate-900/90 border border-slate-800 text-xs text-slate-400 leading-relaxed flex items-start gap-3">
          <Info className="w-4 h-4 text-slate-500 shrink-0 mt-0.5" />
          <div>
            <strong className="text-slate-300 block mb-0.5">{t.disclaimerTitle}</strong>
            <p>{indoorAssessment.disclaimer}</p>
          </div>
        </div>
      )}
    </div>
  );
};
