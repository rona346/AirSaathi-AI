import React from 'react';
import { Wind, ShieldCheck, HeartHandshake, Database } from 'lucide-react';
import { useApp } from '../../context/AppContext';
import { translations } from '../../utils/translations';

export const Footer: React.FC = () => {
  const { currentAqi, language } = useApp();
  const t = translations[language];

  return (
    <footer className="border-t border-slate-800/80 mt-16 py-8 px-4 lg:px-8 text-xs text-slate-400">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
            <Wind className="w-4 h-4" />
          </div>
          <div>
            <span className="font-bold text-slate-200">{t.appName}</span>
            <p className="text-[11px] text-slate-500">
              {t.footerMission}
            </p>
          </div>
        </div>

        <div className="flex items-center flex-wrap gap-4 text-[11px]">
          <div className="flex items-center gap-1.5 text-slate-400">
            <Database className="w-3.5 h-3.5 text-emerald-400" />
            <span>
              {language === 'hi' ? 'बेंचमार्क संदर्भ:' : 'Benchmark:'}{' '}
              {currentAqi?.data_source || 'Central Pollution Control Board'}
            </span>
          </div>

          <div className="flex items-center gap-1.5 text-slate-400">
            <ShieldCheck className="w-3.5 h-3.5 text-indigo-400" />
            <span>{t.footerZeroHallucination}</span>
          </div>

          <div className="flex items-center gap-1.5 text-slate-400">
            <HeartHandshake className="w-3.5 h-3.5 text-rose-400" />
            <span>{t.footerCompliance}</span>
          </div>
        </div>

        <div className="text-[11px] text-slate-500 text-center md:text-right">
          <span>{t.footerStack}</span>
        </div>
      </div>
    </footer>
  );
};
