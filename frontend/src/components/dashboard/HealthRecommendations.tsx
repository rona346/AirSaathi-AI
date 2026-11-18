import React from 'react';
import { HeartPulse, Shield, Wind, Fan, Home } from 'lucide-react';
import { useApp } from '../../context/AppContext';
import { translations } from '../../utils/translations';

export const HealthRecommendations: React.FC = () => {
  const { currentAqi, language } = useApp();

  if (!currentAqi) return null;

  const t = translations[language];
  const { health_advisory, aqi } = currentAqi;

  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-xl font-bold text-white flex items-center gap-2">
          <HeartPulse className="w-5 h-5 text-emerald-400" />
          <span>{t.healthAdvisoryTitle}</span>
        </h2>
        <p className="text-xs text-slate-400 mt-0.5">
          {t.healthAdvisorySubtitle}
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Mask Advisory */}
        <div className="glass-card rounded-2xl p-5 border border-slate-800 space-y-3">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-indigo-500/10 text-indigo-400">
              <Shield className="w-4 h-4" />
            </div>
            <div>
              <span className="text-[11px] text-slate-400 uppercase tracking-wider font-semibold block">
                {t.maskRecommendation}
              </span>
              <h3 className="text-sm font-bold text-white">N95 / N99 / FFP2</h3>
            </div>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed">
            {health_advisory.mask_recommendation}
          </p>
          <div className="pt-2 border-t border-slate-800/80 text-[11px] text-indigo-300 font-medium">
            {t.maskNote}
          </div>
        </div>

        {/* Indoor Air Purification */}
        <div className="glass-card rounded-2xl p-5 border border-slate-800 space-y-3">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-emerald-500/10 text-emerald-400">
              <Fan className="w-4 h-4" />
            </div>
            <div>
              <span className="text-[11px] text-slate-400 uppercase tracking-wider font-semibold block">
                {t.purifierRecommendation}
              </span>
              <h3 className="text-sm font-bold text-white">HEPA H13 Filtration</h3>
            </div>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed">
            {health_advisory.purifier_recommendation}
          </p>
          <div className="pt-2 border-t border-slate-800/80 text-[11px] text-emerald-300 font-medium">
            {t.purifierNote}
          </div>
        </div>

        {/* Outdoor Activities */}
        <div className="glass-card rounded-2xl p-5 border border-slate-800 space-y-3">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-amber-500/10 text-amber-400">
              <Wind className="w-4 h-4" />
            </div>
            <div>
              <span className="text-[11px] text-slate-400 uppercase tracking-wider font-semibold block">
                {t.outdoorExercise}
              </span>
              <h3 className="text-sm font-bold text-white">
                {aqi > 300 ? (language === 'hi' ? 'इनडोर व्यायाम' : 'Indoor Transition') : (language === 'hi' ? 'सीमित समय' : 'Moderate Exposure')}
              </h3>
            </div>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed">
            {health_advisory.outdoor_activity}
          </p>
          <div className="pt-2 border-t border-slate-800/80 text-[11px] text-amber-300 font-medium">
            {t.outdoorNote}
          </div>
        </div>

        {/* Ventilation Window */}
        <div className="glass-card rounded-2xl p-5 border border-slate-800 space-y-3">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-sky-500/10 text-sky-400">
              <Home className="w-4 h-4" />
            </div>
            <div>
              <span className="text-[11px] text-slate-400 uppercase tracking-wider font-semibold block">
                {t.ventilationWindow}
              </span>
              <h3 className="text-sm font-bold text-white">{language === 'hi' ? 'सुरक्षित वायु विनिमय' : 'Safe Air Exchange'}</h3>
            </div>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed">
            {health_advisory.ventilation_window}
          </p>
          <div className="pt-2 border-t border-slate-800/80 text-[11px] text-sky-300 font-medium">
            {t.ventilationNote}
          </div>
        </div>
      </div>
    </div>
  );
};
