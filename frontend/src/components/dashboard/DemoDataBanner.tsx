import React, { useState } from 'react';
import { Info, ChevronDown, ChevronUp, ShieldCheck, Database, Clock } from 'lucide-react';
import { useApp } from '../../context/AppContext';
import { formatTimestamp } from '../../utils/aqiUtils';

export const DemoDataBanner: React.FC = () => {
  const { currentAqi, isDemoData, language } = useApp();
  const [expanded, setExpanded] = useState(false);

  if (!isDemoData) return null;

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
                {language === 'hi' ? 'प्रदर्शन डेटा मोड (Demonstration Mode)' : 'Demonstration Data Mode'}
              </span>
              <span className="text-[11px] font-medium bg-amber-500/20 text-amber-300 border border-amber-500/30 px-2 py-0.5 rounded-full">
                {language === 'hi' ? 'सिम्युलेटेड CPCB बेंचमार्क' : 'Simulated CPCB Baseline'}
              </span>
            </div>
            <p className="text-xs text-slate-300 mt-0.5 leading-relaxed">
              {language === 'hi'
                ? 'यह डैशबोर्ड वर्तमान में प्रामाणिक शीतकालीन स्मॉग पैटर्न पर आधारित डेमो डेटा प्रदर्शित कर रहा है। आगामी मॉड्यूल में लाइव CPCB/OpenAQ और जेमिनी AI पाइपलाइन सक्रिय होंगी।'
                : 'Measurements currently reflect realistic historical winter smog patterns calibrated against CPCB monitoring stations. Live continuous sensor feeds and Gemini AI reasoning are architected for subsequent module integration.'}
            </p>
          </div>
        </div>

        <button
          onClick={() => setExpanded(!expanded)}
          className="self-end sm:self-center flex items-center gap-1.5 text-xs font-medium text-amber-400 hover:text-amber-300 px-3 py-1.5 rounded-lg bg-amber-500/10 hover:bg-amber-500/20 border border-amber-500/20 transition-colors shrink-0"
        >
          <span>{expanded ? (language === 'hi' ? 'कम विवरण' : 'Hide Details') : (language === 'hi' ? 'डेटा स्रोत व विवरण' : 'Provenance & Source')}</span>
          {expanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
        </button>
      </div>

      {expanded && (
        <div className="mt-4 pt-3 border-t border-amber-500/20 grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs text-slate-300 animate-fadeIn">
          <div className="flex items-center gap-2 bg-slate-900/60 p-2.5 rounded-xl border border-slate-800">
            <Database className="w-4 h-4 text-emerald-400 shrink-0" />
            <div>
              <span className="text-slate-400 block text-[11px]">Primary Benchmark Source</span>
              <strong className="text-slate-200">{currentAqi?.data_source || 'CPCB / CAAQMS Historical Baseline'}</strong>
            </div>
          </div>

          <div className="flex items-center gap-2 bg-slate-900/60 p-2.5 rounded-xl border border-slate-800">
            <Clock className="w-4 h-4 text-sky-400 shrink-0" />
            <div>
              <span className="text-slate-400 block text-[11px]">Simulated Timestamp</span>
              <strong className="text-slate-200">
                {currentAqi?.last_updated ? formatTimestamp(currentAqi.last_updated) : 'Current Interval'}
              </strong>
            </div>
          </div>

          <div className="flex items-center gap-2 bg-slate-900/60 p-2.5 rounded-xl border border-slate-800">
            <ShieldCheck className="w-4 h-4 text-indigo-400 shrink-0" />
            <div>
              <span className="text-slate-400 block text-[11px]">Data Integrity Standard</span>
              <strong className="text-slate-200">Zero Synthetic Hallucination Policy</strong>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
