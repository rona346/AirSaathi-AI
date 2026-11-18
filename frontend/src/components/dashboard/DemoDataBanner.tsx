import React, { useState } from 'react';
import { Info, ChevronDown, ChevronUp, ShieldCheck, Database, Clock } from 'lucide-react';
import { useApp } from '../../context/AppContext';
import { formatTimestamp } from '../../utils/aqiUtils';
import { translations } from '../../utils/translations';

export const DemoDataBanner: React.FC = () => {
  const { currentAqi, isDemoData, language } = useApp();
  const [expanded, setExpanded] = useState(false);

  if (!isDemoData) return null;

  const t = translations[language];

  return (
    <div className="rounded-2xl bg-gradient-to-r from-amber-500/10 via-amber-600/5 to-slate-900 border border-amber-500/25 p-4 mb-6 transition-all shadow-lg shadow-amber-500/5">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
        <div className="flex items-start sm:items-center gap-3">
          <div className="p-2 rounded-xl bg-amber-500/20 text-amber-400 shrink-0">
            <Info className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2 flex-wrap">
              <span className="font-bold text-sm text-amber-300">
                {t.demoModeLong}
              </span>
              <span className="text-[11px] font-medium bg-amber-500/20 text-amber-300 border border-amber-500/30 px-2 py-0.5 rounded-full">
                {t.demoBaseline}
              </span>
            </div>
            <p className="text-xs text-slate-300 mt-0.5 leading-relaxed">
              {t.demoNotice}
            </p>
          </div>
        </div>

        <button
          onClick={() => setExpanded(!expanded)}
          className="self-end sm:self-center flex items-center gap-1.5 text-xs font-medium text-amber-400 hover:text-amber-300 px-3 py-1.5 rounded-lg bg-amber-500/10 hover:bg-amber-500/20 border border-amber-500/20 transition-colors shrink-0"
        >
          <span>{expanded ? t.hideDetails : t.showDetails}</span>
          {expanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
        </button>
      </div>

      {expanded && (
        <div className="mt-4 pt-3 border-t border-amber-500/20 grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs text-slate-300 animate-fadeIn">
          <div className="flex items-center gap-2 bg-slate-900/60 p-2.5 rounded-xl border border-slate-800">
            <Database className="w-4 h-4 text-emerald-400 shrink-0" />
            <div>
              <span className="text-slate-400 block text-[11px]">{t.benchmarkSource}</span>
              <strong className="text-slate-200">{currentAqi?.data_source || 'CPCB / CAAQMS Historical Baseline'}</strong>
            </div>
          </div>

          <div className="flex items-center gap-2 bg-slate-900/60 p-2.5 rounded-xl border border-slate-800">
            <Clock className="w-4 h-4 text-sky-400 shrink-0" />
            <div>
              <span className="text-slate-400 block text-[11px]">{t.simulatedTime}</span>
              <strong className="text-slate-200">
                {currentAqi?.last_updated ? formatTimestamp(currentAqi.last_updated) : 'Current Interval'}
              </strong>
            </div>
          </div>

          <div className="flex items-center gap-2 bg-slate-900/60 p-2.5 rounded-xl border border-slate-800">
            <ShieldCheck className="w-4 h-4 text-indigo-400 shrink-0" />
            <div>
              <span className="text-slate-400 block text-[11px]">{t.integrityStandard}</span>
              <strong className="text-slate-200">{t.zeroHallucinationPolicy}</strong>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
