import React from 'react';
import { Wind, ShieldCheck, HeartHandshake, Database } from 'lucide-react';
import { useApp } from '../../context/AppContext';

export const Footer: React.FC = () => {
  const { currentAqi, language } = useApp();

  return (
    <footer className="border-t border-slate-800/80 mt-16 py-8 px-4 lg:px-8 text-xs text-slate-400">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
            <Wind className="w-4 h-4" />
          </div>
          <div>
            <span className="font-bold text-slate-200">AirSaathi AI</span>
            <p className="text-[11px] text-slate-500">
              {language === 'hi'
                ? 'स्वच्छ वायु और स्वस्थ परिवार के लिए एक गैर-लाभकारी तकनीकी पहल'
                : 'Dedicated to urban health intelligence, winter smog navigation & clean air.'}
            </p>
          </div>
        </div>

        <div className="flex items-center flex-wrap gap-4 text-[11px]">
          <div className="flex items-center gap-1.5 text-slate-400">
            <Database className="w-3.5 h-3.5 text-emerald-400" />
            <span>Benchmark: {currentAqi?.data_source || 'Central Pollution Control Board'}</span>
          </div>

          <div className="flex items-center gap-1.5 text-slate-400">
            <ShieldCheck className="w-3.5 h-3.5 text-indigo-400" />
            <span>Strict Zero Hallucination Protocol</span>
          </div>

          <div className="flex items-center gap-1.5 text-slate-400">
            <HeartHandshake className="w-3.5 h-3.5 text-rose-400" />
            <span>National NAQI & WHO Compliant</span>
          </div>
        </div>

        <div className="text-[11px] text-slate-500 text-center md:text-right">
          <span>FastAPI + Vite React + Cloud Run Architecture</span>
        </div>
      </div>
    </footer>
  );
};
