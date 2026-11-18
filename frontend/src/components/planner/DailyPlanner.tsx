import React from 'react';
import {
  Calendar,
  Clock,
  ShieldAlert,
  AlertTriangle,
  CheckCircle2,
  Home,
  Sparkles,
  RefreshCw,
  Users,
  GraduationCap,
  Briefcase,
  Dumbbell,
  ShoppingBag,
  Info,
  ChevronRight,
  Flame,
} from 'lucide-react';
import { useApp } from '../../context/AppContext';
import { ActivityTimeWindow } from '../../types/routine';
import { translations } from '../../utils/translations';
import { getAqiBadgeClasses } from '../../utils/aqiUtils';

export const DailyPlanner: React.FC = () => {
  const {
    routinePlan,
    routineLoading,
    refreshRoutinePlan,
    language,
    familyProfile,
    updateFamilyProfile,
    routinePreferences,
    updateRoutinePreferences,
  } = useApp();

  const t = translations[language];

  const getStatusBadge = (status: string) => {
    switch (status.toLowerCase()) {
      case 'recommended':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
            <CheckCircle2 className="w-3.5 h-3.5" />
            {status}
          </span>
        );
      case 'caution':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-500/15 text-amber-400 border border-amber-500/30">
            <AlertTriangle className="w-3.5 h-3.5" />
            {status}
          </span>
        );
      case 'avoid':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-rose-500/15 text-rose-400 border border-rose-500/30">
            <ShieldAlert className="w-3.5 h-3.5" />
            {status}
          </span>
        );
      case 'indoor alternative':
      default:
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-indigo-500/15 text-indigo-400 border border-indigo-500/30">
            <Home className="w-3.5 h-3.5" />
            {status}
          </span>
        );
    }
  };

  const getRiskBadge = (risk: string) => {
    switch (risk.toLowerCase()) {
      case 'critical':
        return 'text-rose-400 bg-rose-500/10 border-rose-500/20';
      case 'high':
        return 'text-amber-400 bg-amber-500/10 border-amber-500/20';
      case 'moderate':
        return 'text-yellow-400 bg-yellow-500/10 border-yellow-500/20';
      default:
        return 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20';
    }
  };

  const renderActivityCard = (activity: ActivityTimeWindow, icon: React.ReactNode, keyPrefix: string) => (
    <div
      key={`${keyPrefix}-${activity.title}`}
      className="glass-card rounded-2xl p-5 border border-slate-800 hover:border-slate-700 transition-all flex flex-col justify-between space-y-4"
    >
      <div>
        {/* Card Header: Icon, Time, Status */}
        <div className="flex items-start justify-between gap-2 mb-3">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-slate-800 text-slate-300 border border-slate-700/60">
              {icon}
            </div>
            <div>
              <h4 className="text-sm font-bold text-white leading-tight">{activity.title}</h4>
              <div className="flex items-center gap-1.5 text-xs text-slate-400 mt-0.5">
                <Clock className="w-3 h-3 text-emerald-400" />
                <span>{activity.recommended_time}</span>
              </div>
            </div>
          </div>
          <div className="flex flex-col items-end gap-1">
            {getStatusBadge(activity.status)}
            <span
              className={`text-[10px] font-semibold uppercase px-2 py-0.5 rounded-md border ${getRiskBadge(
                activity.risk_level
              )}`}
            >
              {activity.risk_level} {language === 'hi' ? 'जोखिम' : 'Risk'}
            </span>
          </div>
        </div>

        {/* Advice text */}
        <p className="text-xs text-slate-200 leading-relaxed font-medium bg-slate-900/60 p-3 rounded-xl border border-slate-800/80">
          {activity.advice}
        </p>

        {/* Atmospheric Rationale */}
        {activity.rationale && (
          <div className="mt-3 text-xs text-slate-400 bg-slate-950/40 p-2.5 rounded-xl border border-slate-900 flex items-start gap-2">
            <Info className="w-3.5 h-3.5 text-sky-400 shrink-0 mt-0.5" />
            <div>
              <span className="font-semibold text-sky-300 block text-[11px] mb-0.5">
                {t.scientificRationale}:
              </span>
              <span className="text-slate-300 text-[11px] leading-relaxed">{activity.rationale}</span>
            </div>
          </div>
        )}

        {/* Indoor Alternative Box */}
        {activity.indoor_alternative && (
          <div className="mt-3 text-xs text-indigo-300 bg-indigo-950/30 p-2.5 rounded-xl border border-indigo-900/40 flex items-start gap-2">
            <Home className="w-3.5 h-3.5 text-indigo-400 shrink-0 mt-0.5" />
            <div>
              <span className="font-semibold text-indigo-300 block text-[11px] mb-0.5">
                {t.indoorAlternative}:
              </span>
              <span className="text-slate-300 text-[11px] leading-relaxed">{activity.indoor_alternative}</span>
            </div>
          </div>
        )}
      </div>

      {/* Precautions checklist */}
      {activity.precautions && activity.precautions.length > 0 && (
        <div className="pt-3 border-t border-slate-800/80">
          <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-1.5">
            {t.actionPrecautions}
          </span>
          <ul className="space-y-1">
            {activity.precautions.map((prec, i) => (
              <li key={i} className="text-[11px] text-slate-300 flex items-start gap-1.5">
                <ChevronRight className="w-3 h-3 text-emerald-400 shrink-0 mt-0.5" />
                <span>{prec}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );

  return (
    <div className="space-y-8">
      {/* Planner Header Banner */}
      <div className="glass-panel rounded-3xl p-6 sm:p-8 border border-slate-800 relative overflow-hidden">
        <div className="relative z-10 flex flex-col lg:flex-row lg:items-center justify-between gap-6">
          <div className="space-y-2">
            <div className="flex items-center flex-wrap gap-2.5">
              <span className="p-2.5 rounded-2xl bg-gradient-to-br from-blue-500/20 to-indigo-500/10 text-blue-400 border border-blue-500/30">
                <Calendar className="w-6 h-6" />
              </span>
              <h2 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
                {t.plannerTabTitle}
              </h2>
              {routinePlan && (
                <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-indigo-500/15 text-indigo-300 border border-indigo-500/30">
                  <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
                  {routinePlan.ai_generated ? t.aiEngineBadge : t.ruleEngineBadge}
                </span>
              )}
              {routinePlan?.is_demo_data && (
                <span className="text-[11px] font-semibold uppercase tracking-wider px-2.5 py-0.5 rounded-full bg-amber-500/15 text-amber-400 border border-amber-500/30">
                  {t.demoMode}
                </span>
              )}
            </div>

            <p className="text-xs sm:text-sm text-slate-300 max-w-3xl leading-relaxed">
              {t.plannerHeaderSubtitle}
            </p>

            {/* Station and Verified AQI telemetry snapshot */}
            {routinePlan && (
              <div className="flex items-center flex-wrap gap-3 pt-2 text-xs text-slate-400">
                <span>
                  <strong className="text-white">{routinePlan.station_name}</strong> ({routinePlan.city})
                </span>
                <span>•</span>
                <span>
                  AQI:{' '}
                  <strong className={`px-2 py-0.5 rounded-md font-bold border ${getAqiBadgeClasses(routinePlan.category as any).bg} ${getAqiBadgeClasses(routinePlan.category as any).text} ${getAqiBadgeClasses(routinePlan.category as any).border}`}>
                    {routinePlan.aqi} ({routinePlan.category})
                  </strong>
                </span>
                <span>•</span>
                <span>
                  {t.prominentPollutant}: <strong className="text-white">{routinePlan.prominent_pollutant}</strong>
                </span>
                <span>•</span>
                <span className="text-slate-400">
                  {t.lastUpdated}: {new Date(routinePlan.observed_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </span>
              </div>
            )}
          </div>

          {/* Action Button: Refresh / Regenerate Plan */}
          <button
            onClick={refreshRoutinePlan}
            disabled={routineLoading}
            className="flex items-center justify-center gap-2 px-5 py-3 rounded-2xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-bold text-xs shadow-lg shadow-indigo-500/20 transition-all disabled:opacity-50 shrink-0"
          >
            <RefreshCw className={`w-4 h-4 ${routineLoading ? 'animate-spin' : ''}`} />
            <span>{routineLoading ? t.regenerating : t.regeneratePlanBtn}</span>
          </button>
        </div>
      </div>

      {/* Interactive Preferences & Sensitivity Bar */}
      <div className="glass-card rounded-2xl p-5 border border-slate-800 space-y-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          {/* Exercise Preferences */}
          <div className="flex items-center flex-wrap gap-2">
            <span className="text-xs font-semibold text-slate-300 flex items-center gap-1.5 mr-1">
              <Dumbbell className="w-4 h-4 text-emerald-400" />
              {t.exercisePrefLabel}
            </span>
            {[
              { id: 'walk', label: t.exerciseWalk },
              { id: 'run', label: t.exerciseRun },
              { id: 'gym', label: t.exerciseGym },
              { id: 'yoga', label: t.exerciseYoga },
              { id: 'cycling', label: t.exerciseCycling },
            ].map((ex) => (
              <button
                key={ex.id}
                onClick={() => updateRoutinePreferences({ preferred_exercise_type: ex.id })}
                className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition-all ${
                  routinePreferences.preferred_exercise_type === ex.id
                    ? 'bg-blue-600 text-white shadow-md shadow-blue-500/20'
                    : 'bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-800'
                }`}
              >
                {ex.label}
              </button>
            ))}
          </div>

          {/* Family Sensitivity Quick Badges */}
          <div className="flex items-center flex-wrap gap-2 text-xs">
            <span className="text-slate-400 font-medium flex items-center gap-1 mr-1">
              <Users className="w-3.5 h-3.5 text-indigo-400" />
              {t.familyPillLabel}
            </span>
            <button
              onClick={() => updateFamilyProfile({ hasChildren: !familyProfile.hasChildren })}
              className={`px-2.5 py-1 rounded-lg border transition-all ${
                familyProfile.hasChildren
                  ? 'bg-amber-500/20 text-amber-300 border-amber-500/40'
                  : 'bg-slate-900/60 text-slate-500 border-slate-800'
              }`}
            >
              {t.childrenToggle}
            </button>
            <button
              onClick={() => updateFamilyProfile({ hasSeniors: !familyProfile.hasSeniors })}
              className={`px-2.5 py-1 rounded-lg border transition-all ${
                familyProfile.hasSeniors
                  ? 'bg-purple-500/20 text-purple-300 border-purple-500/40'
                  : 'bg-slate-900/60 text-slate-500 border-slate-800'
              }`}
            >
              {t.seniorsToggle}
            </button>
            <button
              onClick={() => updateFamilyProfile({ hasRespiratoryCondition: !familyProfile.hasRespiratoryCondition })}
              className={`px-2.5 py-1 rounded-lg border transition-all ${
                familyProfile.hasRespiratoryCondition
                  ? 'bg-rose-500/20 text-rose-300 border-rose-500/40'
                  : 'bg-slate-900/60 text-slate-500 border-slate-800'
              }`}
            >
              {t.asthmaToggle}
            </button>
            <button
              onClick={() => updateFamilyProfile({ isPregnant: !familyProfile.isPregnant })}
              className={`px-2.5 py-1 rounded-lg border transition-all ${
                familyProfile.isPregnant
                  ? 'bg-pink-500/20 text-pink-300 border-pink-500/40'
                  : 'bg-slate-900/60 text-slate-500 border-slate-800'
              }`}
            >
              {t.maternalToggle}
            </button>
          </div>
        </div>
      </div>

      {/* Dedicated Domain Cards: School, Office, Exercise, Chores */}
      {routinePlan && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <Flame className="w-5 h-5 text-amber-400" />
              <span>{t.keyActivitiesTitle}</span>
            </h3>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {renderActivityCard(
              routinePlan.school_commute,
              <GraduationCap className="w-5 h-5 text-amber-400" />,
              'domain-school'
            )}
            {renderActivityCard(
              routinePlan.office_commute,
              <Briefcase className="w-5 h-5 text-blue-400" />,
              'domain-office'
            )}
            {renderActivityCard(
              routinePlan.exercise_plan,
              <Dumbbell className="w-5 h-5 text-emerald-400" />,
              'domain-exercise'
            )}
            {renderActivityCard(
              routinePlan.chores_plan,
              <ShoppingBag className="w-5 h-5 text-purple-400" />,
              'domain-chores'
            )}
          </div>
        </div>
      )}

      {/* Chronological Daily Timeline Sections */}
      {routinePlan && (
        <div className="space-y-8">
          {/* 1. Morning Section */}
          <div className="space-y-4">
            <div className="flex items-center gap-2 text-white">
              <span className="p-1.5 rounded-lg bg-amber-500/20 text-amber-400 border border-amber-500/30">
                <Clock className="w-4 h-4" />
              </span>
              <h3 className="text-base font-bold">{t.timeOfDayMorning}</h3>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {routinePlan.morning.map((act, idx) =>
                renderActivityCard(act, <Clock className="w-5 h-5 text-amber-400" />, `morning-${idx}`)
              )}
            </div>
          </div>

          {/* 2. Afternoon Section */}
          <div className="space-y-4">
            <div className="flex items-center gap-2 text-white">
              <span className="p-1.5 rounded-lg bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                <Clock className="w-4 h-4" />
              </span>
              <h3 className="text-base font-bold">{t.timeOfDayAfternoon}</h3>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {routinePlan.afternoon.map((act, idx) =>
                renderActivityCard(act, <Clock className="w-5 h-5 text-emerald-400" />, `afternoon-${idx}`)
              )}
            </div>
          </div>

          {/* 3. Evening & Night Section */}
          <div className="space-y-4">
            <div className="flex items-center gap-2 text-white">
              <span className="p-1.5 rounded-lg bg-indigo-500/20 text-indigo-400 border border-indigo-500/30">
                <Clock className="w-4 h-4" />
              </span>
              <h3 className="text-base font-bold">{t.timeOfDayEvening}</h3>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {routinePlan.evening.map((act, idx) =>
                renderActivityCard(act, <Clock className="w-5 h-5 text-indigo-400" />, `evening-${idx}`)
              )}
            </div>
          </div>
        </div>
      )}

      {/* Family Safeguards & Vulnerability Precautions */}
      {routinePlan && routinePlan.family_precautions && routinePlan.family_precautions.length > 0 && (
        <div className="glass-card rounded-2xl p-6 border border-indigo-900/40 bg-indigo-950/20 space-y-3">
          <div className="flex items-center gap-2 text-indigo-300">
            <ShieldAlert className="w-5 h-5 text-indigo-400" />
            <h4 className="text-sm font-bold uppercase tracking-wide">{t.familyPrecautionsTitle}</h4>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-1">
            {routinePlan.family_precautions.map((prec, i) => (
              <div
                key={i}
                className="flex items-start gap-2.5 p-3 rounded-xl bg-slate-900/80 border border-indigo-900/30 text-xs text-slate-200"
              >
                <div className="w-1.5 h-1.5 rounded-full bg-indigo-400 mt-1.5 shrink-0" />
                <span className="leading-relaxed">{prec}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Medical & Environmental Disclaimer */}
      {routinePlan && (
        <div className="p-4 rounded-2xl bg-slate-900/90 border border-slate-800 text-xs text-slate-400 leading-relaxed flex items-start gap-3">
          <Info className="w-4 h-4 text-slate-500 shrink-0 mt-0.5" />
          <div>
            <strong className="text-slate-300 block mb-0.5">{t.disclaimerTitle}</strong>
            <p>{routinePlan.disclaimer}</p>
          </div>
        </div>
      )}
    </div>
  );
};
