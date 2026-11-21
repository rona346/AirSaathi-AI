import React from 'react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';
import { TrendingUp, Clock, AlertTriangle, ShieldCheck } from 'lucide-react';
import { useApp } from '../../context/AppContext';
import { getAqiCategoryLabel } from '../../utils/aqiUtils';
import { translations } from '../../utils/translations';

export const HourlyTrendChart: React.FC = () => {
  const { forecast, language } = useApp();

  const [isMobile, setIsMobile] = React.useState<boolean>(() => {
    return typeof window !== 'undefined' ? window.innerWidth < 640 : false;
  });

  React.useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth < 640);
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  if (!forecast || !forecast.forecast_24h || forecast.forecast_24h.length === 0) {
    return null;
  }

  const t = translations[language];
  const { forecast_24h, peak_aqi_window, safest_outdoor_window } = forecast;

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      const localizedCat = getAqiCategoryLabel(data.category, language);
      return (
        <div className="glass-panel p-3 rounded-xl border border-slate-700 shadow-xl text-xs space-y-1">
          <p className="font-bold text-slate-200">{label}</p>
          <p className="text-emerald-400 font-extrabold text-sm">
            AQI: <span className="font-mono">{data.aqi}</span> ({localizedCat})
          </p>
          <div className="pt-1 border-t border-slate-700/60 text-slate-300 flex justify-between gap-4">
            <span>PM2.5: {data.pm25} µg/m³</span>
            <span>PM10: {data.pm10} µg/m³</span>
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="glass-panel rounded-3xl p-6 lg:p-8 border border-slate-800 space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-emerald-400" />
              <span>{t.diurnalTitle}</span>
            </h2>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            {t.diurnalSubtitle}
          </p>
        </div>

        {/* Windows summary */}
        <div className="flex flex-col sm:flex-row gap-2 w-full sm:w-auto">
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-rose-500/10 border border-rose-500/30 text-xs text-rose-300">
            <AlertTriangle className="w-3.5 h-3.5 text-rose-400 shrink-0" />
            <div>
              <span className="text-[10px] text-rose-400 block font-semibold uppercase">{t.peakDangerWindow}</span>
              <strong className="text-rose-200">{peak_aqi_window}</strong>
            </div>
          </div>

          <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-xs text-emerald-300">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
            <div>
              <span className="text-[10px] text-emerald-400 block font-semibold uppercase">{t.safestOutdoorWindow}</span>
              <strong className="text-emerald-200">{safest_outdoor_window}</strong>
            </div>
          </div>
        </div>
      </div>

      {/* Recharts Area Chart */}
      <div className="h-64 sm:h-72 w-full pt-2">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={forecast_24h} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <defs>
              <linearGradient id="aqiGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#EF4444" stopOpacity={0.6} />
                <stop offset="40%" stopColor="#F97316" stopOpacity={0.4} />
                <stop offset="95%" stopColor="#10B981" stopOpacity={0.05} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
            <XAxis
              dataKey="hour"
              stroke="#64748b"
              fontSize={11}
              tickLine={false}
              axisLine={{ stroke: '#334155' }}
              interval="preserveStartEnd"
            />
            <YAxis
              stroke="#64748b"
              fontSize={11}
              domain={[0, 500]}
              tickLine={false}
              axisLine={{ stroke: '#334155' }}
              ticks={[50, 100, 200, 300, 400, 500]}
            />
            <Tooltip content={<CustomTooltip />} />
            {/* National threshold reference lines with collision-safe labels */}
            <ReferenceLine
              y={200}
              stroke="#EAB308"
              strokeDasharray="3 3"
              label={{
                value: isMobile ? '200' : t.moderateLimit,
                fill: '#EAB308',
                fontSize: 10,
                position: isMobile ? 'insideTopLeft' : 'insideTopRight',
              }}
            />
            <ReferenceLine
              y={300}
              stroke="#F97316"
              strokeDasharray="3 3"
              label={{
                value: isMobile ? '300' : t.poorLimit,
                fill: '#F97316',
                fontSize: 10,
                position: isMobile ? 'insideTopLeft' : 'insideTopRight',
              }}
            />
            <ReferenceLine
              y={400}
              stroke="#EF4444"
              strokeDasharray="3 3"
              label={{
                value: isMobile ? '400' : t.severeLimit,
                fill: '#EF4444',
                fontSize: 10,
                position: isMobile ? 'insideTopLeft' : 'insideTopRight',
              }}
            />
            <Area
              type="monotone"
              dataKey="aqi"
              stroke="#F43F5E"
              strokeWidth={3}
              fillOpacity={1}
              fill="url(#aqiGradient)"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      <div className="flex flex-wrap items-center justify-between gap-2 pt-2 text-xs text-slate-400 border-t border-slate-800/80">
        <span className="flex items-center gap-1.5">
          <Clock className="w-3.5 h-3.5 text-slate-500" />
          <span>{t.inversionFootnote}</span>
        </span>
        <span className="text-[11px] text-slate-500">
          {t.diurnalSource}
        </span>
      </div>
    </div>
  );
};
