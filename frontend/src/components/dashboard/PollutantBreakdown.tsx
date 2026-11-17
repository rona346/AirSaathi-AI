import React from 'react';
import { Activity } from 'lucide-react';
import { useApp } from '../../context/AppContext';
import { getAqiBadgeClasses } from '../../utils/aqiUtils';

export const PollutantBreakdown: React.FC = () => {
  const { currentAqi, language } = useApp();

  if (!currentAqi) return null;

  const { pollutants } = currentAqi;
  const pollutantList = Object.values(pollutants);

  return (
    <div className="space-y-4">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Activity className="w-5 h-5 text-emerald-400" />
            <span>{language === 'hi' ? 'प्रदूषक संघटन व सीमाएं' : 'Real-time Pollutant Breakdown'}</span>
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            {language === 'hi'
              ? 'केंद्रीय प्रदूषण नियंत्रण बोर्ड (CPCB) एवं विश्व स्वास्थ्य संगठन (WHO) मानकों से तुलना'
              : 'Continuous measurements benchmarked against CPCB 24-hr standards & WHO limits'}
          </p>
        </div>

        <div className="flex items-center gap-3 text-[11px] text-slate-400">
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-slate-600 inline-block" />
            CPCB Limit
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 inline-block" />
            WHO Benchmark
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {pollutantList.map((p) => {
          const badge = getAqiBadgeClasses(p.category);
          const cpcbRatio = (p.value / p.standard_limit).toFixed(1);
          const whoRatio = (p.value / p.who_limit).toFixed(1);
          const isAboveSafe = p.value > p.standard_limit;

          return (
            <div
              key={p.name}
              className="glass-card rounded-2xl p-5 border border-slate-800 hover:border-slate-700/80 transition-all hover:shadow-xl relative overflow-hidden"
            >
              {/* Highlight top banner for toxic PM2.5 / PM10 */}
              {isAboveSafe && (
                <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-red-500 via-orange-500 to-amber-500" />
              )}

              <div className="flex items-start justify-between">
                <div>
                  <span className="text-lg font-extrabold text-white tracking-tight">{p.name}</span>
                  <span className="text-[11px] text-slate-400 block">
                    {p.name === 'PM2.5'
                      ? 'Fine Respirable Dust (< 2.5 µm)'
                      : p.name === 'PM10'
                      ? 'Inhalable Particulate Matter (< 10 µm)'
                      : p.name === 'NO2'
                      ? 'Nitrogen Dioxide (Vehicular/Combustion)'
                      : p.name === 'SO2'
                      ? 'Sulphur Dioxide (Industrial/Thermal)'
                      : p.name === 'CO'
                      ? 'Carbon Monoxide (Incomplete burning)'
                      : 'Ozone (Photochemical Smog)'}
                  </span>
                </div>

                <span
                  className={`text-[11px] font-bold px-2.5 py-0.5 rounded-full border ${badge.bg} ${badge.text} ${badge.border}`}
                >
                  {p.category}
                </span>
              </div>

              <div className="mt-4 flex items-baseline gap-2">
                <span className="text-3xl font-black text-white font-mono">{p.value}</span>
                <span className="text-xs font-semibold text-slate-400">{p.unit}</span>
              </div>

              {/* Threshold Comparison Metrics */}
              <div className="mt-4 pt-3 border-t border-slate-800/80 space-y-2 text-xs">
                <div className="flex items-center justify-between text-slate-300">
                  <span className="text-slate-400">National Standard (CPCB):</span>
                  <span className="font-semibold">
                    {p.standard_limit} {p.unit}{' '}
                    {isAboveSafe ? (
                      <span className="text-rose-400 font-bold ml-1">({cpcbRatio}x limit)</span>
                    ) : (
                      <span className="text-emerald-400 font-medium ml-1">(Within Limit)</span>
                    )}
                  </span>
                </div>

                <div className="flex items-center justify-between text-slate-300">
                  <span className="text-slate-400">WHO Guideline:</span>
                  <span className="font-semibold">
                    {p.who_limit} {p.unit}{' '}
                    <span className="text-amber-400 font-medium ml-1">({whoRatio}x WHO)</span>
                  </span>
                </div>

                {/* Sub-Index Progress Bar */}
                <div className="mt-2">
                  <div className="flex justify-between text-[10px] text-slate-400 mb-1">
                    <span>Sub-index: {p.sub_index}</span>
                    <span>Max: 500</span>
                  </div>
                  <div className="w-full h-1.5 rounded-full bg-slate-800 overflow-hidden">
                    <div
                      className={`h-full rounded-full ${
                        p.sub_index > 400
                          ? 'bg-rose-900'
                          : p.sub_index > 300
                          ? 'bg-red-500'
                          : p.sub_index > 200
                          ? 'bg-orange-500'
                          : p.sub_index > 100
                          ? 'bg-yellow-400'
                          : 'bg-emerald-500'
                      }`}
                      style={{ width: `${Math.min(100, (p.sub_index / 500) * 100)}%` }}
                    />
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
