import React from 'react';
import { HeartPulse, Shield, Wind, Fan, Home } from 'lucide-react';
import { useApp } from '../../context/AppContext';

export const HealthRecommendations: React.FC = () => {
  const { currentAqi, language } = useApp();

  if (!currentAqi) return null;

  const { health_advisory, aqi } = currentAqi;

  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-xl font-bold text-white flex items-center gap-2">
          <HeartPulse className="w-5 h-5 text-emerald-400" />
          <span>{language === 'hi' ? 'स्वास्थ्य सलाह एवं सुरक्षा निर्देश' : 'Health Advisory & Action Guidelines'}</span>
        </h2>
        <p className="text-xs text-slate-400 mt-0.5">
          {language === 'hi'
            ? 'वर्तमान वायु गुणवत्ता के आधार पर व्यक्तिगत एवं पारिवारिक सुरक्षा उपाय'
            : 'Evidence-based mitigation tailored to current exposure severity'}
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
                {language === 'hi' ? 'मास्क अनुशंसा' : 'Mask Recommendation'}
              </span>
              <h3 className="text-sm font-bold text-white">N95 / N99 / FFP2</h3>
            </div>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed">
            {health_advisory.mask_recommendation}
          </p>
          <div className="pt-2 border-t border-slate-800/80 text-[11px] text-indigo-300 font-medium">
            Cloth & surgical masks do not filter PM2.5 aerosols.
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
                {language === 'hi' ? 'एयर प्यूरीफायर मोड' : 'Air Purifier Setting'}
              </span>
              <h3 className="text-sm font-bold text-white">HEPA H13 Filtration</h3>
            </div>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed">
            {health_advisory.purifier_recommendation}
          </p>
          <div className="pt-2 border-t border-slate-800/80 text-[11px] text-emerald-300 font-medium">
            Maintain CADR ≥ 2.5 air changes per hour (ACH).
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
                {language === 'hi' ? 'आउटडोर गतिविधि' : 'Outdoor Exercise'}
              </span>
              <h3 className="text-sm font-bold text-white">
                {aqi > 300 ? 'Indoor Transition' : 'Moderate Exposure'}
              </h3>
            </div>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed">
            {health_advisory.outdoor_activity}
          </p>
          <div className="pt-2 border-t border-slate-800/80 text-[11px] text-amber-300 font-medium">
            Deep breathing increases ultrafine particulate deposition by 4x.
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
                {language === 'hi' ? 'घर की खिड़कियां व वेंटिलेशन' : 'Ventilation Window'}
              </span>
              <h3 className="text-sm font-bold text-white">Safe Air Exchange</h3>
            </div>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed">
            {health_advisory.ventilation_window}
          </p>
          <div className="pt-2 border-t border-slate-800/80 text-[11px] text-sky-300 font-medium">
            Do not aerate before 11:30 AM or after sunset in smog season.
          </div>
        </div>
      </div>
    </div>
  );
};
