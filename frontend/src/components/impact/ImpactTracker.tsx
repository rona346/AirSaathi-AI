import React, { useState, useEffect, useCallback } from 'react';
import {
  AreaChart,
  Area,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import {
  Leaf,
  Navigation,
  Cloud,
  ShieldCheck,
  TreePine,
  Sparkles,
  TrendingUp,
  PieChart as PieIcon,
  PlusCircle,
  Trash2,
  HelpCircle,
  RefreshCw,
  Calendar,
  Users,
  Train,
  Bus,
  Car,
  Bike,
  Footprints,
  Zap,
  Wind,
  AlertCircle,
  CheckCircle2,
  Info,
  ChevronLeft,
  ChevronRight,
  X,
  ShieldAlert,
} from 'lucide-react';
import { useApp } from '../../context/AppContext';
import {
  CalculationMethodologyDetail,
  ImpactActivityType,
  ImpactLogCreate,
  ImpactSummaryResponse,
  PaginatedImpactLogs,
  TimeframeFilter,
  TransportMode,
} from '../../types/impact';
import {
  createImpactLog,
  deleteImpactLog,
  fetchImpactLogs,
  fetchImpactMethodology,
  fetchImpactSummary,
} from '../../services/api';
import { getCurrentIdToken } from '../../services/firebase';
import { translations } from '../../utils/translations';

const MODE_COLORS: Record<string, string> = {
  metro: '#10b981', // emerald-500
  electric_bus: '#06b6d4', // cyan-500
  public_bus: '#3b82f6', // blue-500
  carpool: '#8b5cf6', // purple-500
  electric_car: '#14b8a6', // teal-500
  walking: '#84cc16', // lime-500
  cycling: '#22c55e', // green-500
  cng_auto: '#f59e0b', // amber-500
  petrol_car: '#f43f5e', // rose-500
  diesel_car: '#e11d48', // rose-600
  electric_two_wheeler: '#2dd4bf', // teal-400
  two_wheeler: '#0284c7', // sky-600
  other: '#64748b', // slate-500
};

export const ImpactTracker: React.FC = () => {
  const { language, user, setAuthModalOpen } = useApp();
  const t = translations[language];
  const isHi = language === 'hi';

  // State
  const [timeframe, setTimeframe] = useState<TimeframeFilter>('week');
  const [summary, setSummary] = useState<ImpactSummaryResponse | null>(null);
  const [logs, setLogs] = useState<PaginatedImpactLogs | null>(null);
  const [methodology, setMethodology] = useState<CalculationMethodologyDetail | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Pagination
  const [page, setPage] = useState<number>(0);
  const pageSize = 5;

  // Modals
  const [isAddModalOpen, setIsAddModalOpen] = useState<boolean>(false);
  const [isMethodologyOpen, setIsMethodologyOpen] = useState<boolean>(false);
  const [deletingLogId, setDeletingLogId] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [actionSuccessMsg, setActionSuccessMsg] = useState<string | null>(null);

  // New Activity Form State
  const [activityType, setActivityType] = useState<ImpactActivityType>('public_transit');
  const [transportMode, setTransportMode] = useState<TransportMode>('metro');
  const [distanceKm, setDistanceKm] = useState<number>(15.0);
  const [passengers, setPassengers] = useState<number>(1);
  const [activityDate, setActivityDate] = useState<string>(
    new Date().toISOString().split('T')[0]
  );
  const [notes, setNotes] = useState<string>('');
  const [exposureScore, setExposureScore] = useState<number>(30.0);
  const [formError, setFormError] = useState<string | null>(null);

  // Load Data
  const loadData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const token = user ? await getCurrentIdToken() : null;
      const [sumRes, logsRes, methData] = await Promise.all([
        fetchImpactSummary(token, timeframe),
        fetchImpactLogs(token, timeframe, pageSize, page * pageSize),
        fetchImpactMethodology(),
      ]);

      setSummary(sumRes.data);
      setLogs(logsRes.data);
      setMethodology(methData);
    } catch (err: any) {
      console.error('Error loading impact tracker data:', err);
      setError(err?.message || 'Failed to load environmental impact records.');
      if (user) {
        setSummary(null);
        setLogs(null);
      }
    } finally {
      setLoading(false);
    }
  }, [user, timeframe, page]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  // Mode icon helper
  const getModeIcon = (modeStr?: string | null, type?: ImpactActivityType) => {
    if (type === 'purifier_optimized' || type === 'ventilation_timed') {
      return <Wind className="w-4 h-4 text-teal-400" />;
    }
    switch (modeStr) {
      case 'metro':
        return <Train className="w-4 h-4 text-emerald-400" />;
      case 'electric_bus':
        return <Bus className="w-4 h-4 text-cyan-400" />;
      case 'public_bus':
        return <Bus className="w-4 h-4 text-blue-400" />;
      case 'carpool':
        return <Users className="w-4 h-4 text-purple-400" />;
      case 'electric_car':
        return <Zap className="w-4 h-4 text-teal-400" />;
      case 'walking':
        return <Footprints className="w-4 h-4 text-lime-400" />;
      case 'cycling':
        return <Bike className="w-4 h-4 text-green-400" />;
      case 'cng_auto':
        return <Car className="w-4 h-4 text-amber-400" />;
      default:
        return <Navigation className="w-4 h-4 text-slate-400" />;
    }
  };

  // Live scientific preview calculation
  const calculateLivePreview = () => {
    if (activityType === 'purifier_optimized' || activityType === 'ventilation_timed') {
      return {
        emissionsKg: 0.0,
        baselineKg: 0.0,
        savingsKg: 0.0,
        isIndoor: true,
      };
    }

    const dist = Math.max(0.1, distanceKm || 0);
    const baselineG = dist * 165.0; // Solo petrol car 165 g/km
    let factorG = 165.0;

    if (transportMode === 'metro') {
      factorG = 22.0; // already passenger-allocated
    } else if (transportMode === 'electric_bus') {
      factorG = 859.2 / 35.0; // ~24.5 g/pax-km
    } else if (transportMode === 'public_bus') {
      factorG = 1100.0 / 35.0; // ~31.4 g/pax-km
    } else if (transportMode === 'carpool') {
      const occ = Math.max(2, passengers > 1 ? passengers : 3);
      factorG = 165.0 / occ;
    } else if (transportMode === 'walking' || transportMode === 'cycling') {
      factorG = 0.0;
    } else if (transportMode === 'electric_car') {
      factorG = 107.4 / Math.max(1, passengers);
    } else if (transportMode === 'electric_two_wheeler') {
      factorG = 25.1 / Math.max(1, passengers);
    } else if (transportMode === 'cng_auto') {
      factorG = 72.0 / 2.0;
    } else if (transportMode === 'two_wheeler' || transportMode === 'two_wheeler_petrol') {
      factorG = 52.0 / Math.max(1, passengers);
    } else if (transportMode === 'diesel_car') {
      factorG = 175.0 / Math.max(1, passengers);
    } else {
      factorG = 165.0 / Math.max(1, passengers);
    }

    const actualG = dist * factorG;
    const actualKg = Math.round((actualG / 1000.0) * 100) / 100;
    const baseKg = Math.round((baselineG / 1000.0) * 100) / 100;
    const saveKg = Math.max(0.0, Math.round((baseKg - actualKg) * 100) / 100);

    return {
      emissionsKg: actualKg,
      baselineKg: baseKg,
      savingsKg: saveKg,
      isIndoor: false,
    };
  };

  const preview = calculateLivePreview();

  // Handle Add Activity
  const handleCreateActivity = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError(null);

    const isIndoor =
      activityType === 'purifier_optimized' || activityType === 'ventilation_timed';

    if (!isIndoor && (!distanceKm || distanceKm <= 0)) {
      setFormError(
        isHi
          ? 'कृपया यात्रा की दूरी (किमी) सही भरें (> 0)'
          : 'Trip distance must be greater than 0 km for transit activities.'
      );
      return;
    }

    if (!isIndoor && distanceKm > 150) {
      setFormError(
        isHi
          ? 'अधिकतम अनुमत दूरी 150 किमी है'
          : 'Maximum permitted single trip distance is 150 km.'
      );
      return;
    }

    if (!user) {
      setFormError(
        isHi
          ? 'गतिविधि सहेजने के लिए कृपया लॉगिन करें।'
          : 'Please sign in to persist your personal impact log.'
      );
      setAuthModalOpen(true);
      return;
    }

    setIsSubmitting(true);
    try {
      const token = await getCurrentIdToken();
      if (!token) throw new Error('Authentication token unavailable.');

      const payload: ImpactLogCreate = {
        activity_type: activityType,
        mode: isIndoor ? null : transportMode,
        distance_km: isIndoor ? 0 : distanceKm,
        passengers: isIndoor ? 1 : passengers,
        activity_date: activityDate,
        notes: notes.trim() || undefined,
        exposure_avoided_score: exposureScore,
      };

      await createImpactLog(token, payload);
      setIsAddModalOpen(false);
      setActionSuccessMsg(
        isHi
          ? 'पर्यावरणीय गतिविधि सफलतापूर्वक दर्ज की गई!'
          : 'Environmental activity logged successfully!'
      );
      setTimeout(() => setActionSuccessMsg(null), 4000);
      loadData();
    } catch (err: any) {
      setFormError(err?.message || 'Failed to record activity.');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Handle Delete Activity
  const handleDeleteActivity = async (logId: string) => {
    if (!user) {
      alert(
        isHi
          ? 'डेमो गतिविधियों को हटाया नहीं जा सकता। केवल व्यक्तिगत खाते की गतिविधियां हटाई जा सकती हैं।'
          : 'Demonstration records cannot be deleted. Sign in to manage personal logs.'
      );
      setDeletingLogId(null);
      return;
    }

    setIsSubmitting(true);
    try {
      const token = await getCurrentIdToken();
      if (!token) throw new Error('Authentication token unavailable.');

      await deleteImpactLog(token, logId);
      setDeletingLogId(null);
      setActionSuccessMsg(
        isHi ? 'गतिविधि सफलतापूर्वक हटाई गई।' : 'Activity record deleted successfully.'
      );
      setTimeout(() => setActionSuccessMsg(null), 3000);
      loadData();
    } catch (err: any) {
      alert(err?.message || 'Failed to delete activity record.');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Custom Chart Tooltip
  const CustomTrendTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const d = payload[0].payload;
      return (
        <div className="glass-panel p-3 rounded-xl border border-slate-700 shadow-2xl text-xs space-y-1.5">
          <p className="font-bold text-slate-200">{d.day_label} ({d.date_str})</p>
          <div className="flex items-center justify-between gap-4 text-emerald-400 font-semibold">
            <span>{isHi ? 'कार्बन बचत:' : 'CO2e Savings:'}</span>
            <span className="font-mono font-bold">{d.savings_kg} kg</span>
          </div>
          <div className="flex items-center justify-between gap-4 text-rose-400 font-semibold">
            <span>{isHi ? 'वास्तविक उत्सर्जन:' : 'Modeled Emissions:'}</span>
            <span className="font-mono font-bold">{d.emissions_kg} kg</span>
          </div>
          <div className="pt-1 border-t border-slate-700/80 text-slate-400 flex justify-between gap-4 text-[11px]">
            <span>{isHi ? 'स्वच्छ दूरी:' : 'Clean Dist:'} {d.clean_distance_km} km</span>
            <span>{isHi ? 'गतिविधियां:' : 'Count:'} {d.activity_count}</span>
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="space-y-8">
      {/* 1. Header Banner & Controls */}
      <div className="glass-panel rounded-3xl p-6 lg:p-8 border border-slate-800 space-y-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2.5 flex-wrap">
              <div className="p-2.5 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 shadow-lg shadow-emerald-500/10">
                <Leaf className="w-6 h-6 animate-pulse" />
              </div>
              <div>
                <h1 className="text-2xl font-extrabold text-white flex items-center gap-2">
                  <span>{t.impactTabTitle}</span>
                  <span className="text-xs px-2 py-0.5 rounded-full bg-emerald-500/20 border border-emerald-500/40 text-emerald-300 font-mono font-semibold">
                    Module 6
                  </span>
                </h1>
                <p className="text-xs text-slate-400 mt-0.5">{t.impactHeaderSubtitle}</p>
              </div>
            </div>
          </div>

          {/* Timeframe Filter Buttons */}
          <div className="flex items-center bg-slate-900/90 p-1.5 rounded-2xl border border-slate-800 self-start md:self-auto">
            {(
              [
                ['day', t.impactTimeframeDay],
                ['week', t.impactTimeframeWeek],
                ['month', t.impactTimeframeMonth],
                ['all_time', t.impactTimeframeAll],
              ] as [TimeframeFilter, string][]
            ).map(([tf, label]) => (
              <button
                key={tf}
                onClick={() => {
                  setTimeframe(tf);
                  setPage(0);
                }}
                className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all ${
                  timeframe === tf
                    ? 'bg-emerald-500 text-white shadow-md shadow-emerald-500/20'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                {label}
              </button>
            ))}
          </div>
        </div>

        {/* Action Header Row: Provenance Tag, Add Button, Methodology Button, Refresh */}
        <div className="flex flex-wrap items-center justify-between gap-3 pt-4 border-t border-slate-800/80">
          <div className="flex items-center gap-2">
            {summary?.is_demo_data ? (
              <span className="inline-flex items-center gap-1.5 text-xs font-semibold px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-300 shadow-sm">
                <ShieldAlert className="w-3.5 h-3.5 text-amber-400" />
                <span>
                  {isHi ? 'सिम्युलेटेड डेमो डेटा' : 'Simulated Guest Demonstration Data'}
                </span>
              </span>
            ) : (
              <span className="inline-flex items-center gap-1.5 text-xs font-semibold px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 shadow-sm">
                <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                <span>{isHi ? 'सत्यापित व्यक्तिगत रिकॉर्ड' : 'Personal Cloud Firestore Records'}</span>
              </span>
            )}
            <span className="text-xs text-slate-500 hidden sm:inline">
              | {isHi ? 'शून्य-सिंथेटिक भ्रम नीति' : 'Zero-Synthetic Hallucination Standard'}
            </span>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setIsMethodologyOpen(true)}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-300 hover:text-white text-xs font-semibold border border-slate-800 transition-colors"
            >
              <HelpCircle className="w-3.5 h-3.5 text-teal-400" />
              <span>{t.impactMethodologyBtn}</span>
            </button>

            <button
              onClick={() => {
                if (!user) {
                  setAuthModalOpen(true);
                } else {
                  setIsAddModalOpen(true);
                }
              }}
              className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-600 hover:to-teal-700 text-white text-xs font-bold shadow-lg shadow-emerald-500/20 transition-all active:scale-95"
            >
              <PlusCircle className="w-3.5 h-3.5" />
              <span>{t.impactLogActivityBtn}</span>
            </button>

            <button
              onClick={loadData}
              disabled={loading}
              className="p-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-800 transition-colors"
              title="Refresh Records"
            >
              <RefreshCw
                className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-emerald-400' : ''}`}
              />
            </button>
          </div>
        </div>

        {error && (
          <div className="p-3 rounded-2xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {actionSuccessMsg && (
          <div className="p-3 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs flex items-center gap-2 animate-fadeIn">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
            <span>{actionSuccessMsg}</span>
          </div>
        )}
      </div>

      {error && !summary && user ? (
        <div className="glass-panel rounded-3xl p-8 border border-rose-500/30 bg-rose-500/5 text-center space-y-4">
          <div className="p-3.5 rounded-2xl bg-rose-500/10 text-rose-400 w-fit mx-auto border border-rose-500/20">
            <AlertCircle className="w-8 h-8" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-white">
              {isHi ? 'व्यक्तिगत प्रभाव रिकॉर्ड लोड करने में असमर्थ' : 'Unable to Retrieve Personal Impact Records'}
            </h3>
            <p className="text-xs text-rose-300/80 max-w-md mx-auto mt-1 leading-relaxed">
              {error}
            </p>
          </div>
          <button
            onClick={loadData}
            className="px-4 py-2 rounded-xl bg-emerald-500 hover:bg-emerald-600 text-white font-semibold text-xs transition-all shadow-lg shadow-emerald-500/20 inline-flex items-center gap-2"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>{isHi ? 'पुनः प्रयास करें' : 'Retry Connection'}</span>
          </button>
        </div>
      ) : (
        <>
          {/* 2. Hero 4-Metrics Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Card 1: Clean Distance */}
        <div className="glass-card rounded-3xl p-5 border border-slate-800 flex flex-col justify-between relative overflow-hidden group hover:border-emerald-500/40 transition-all">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-semibold text-slate-400">{t.impactTotalDistance}</span>
            <div className="p-2 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
              <Navigation className="w-4 h-4" />
            </div>
          </div>
          <div>
            <div className="flex items-baseline gap-1.5">
              <span className="text-3xl font-extrabold text-white font-mono tracking-tight">
                {summary?.total_distance_km.toFixed(1) || '0.0'}
              </span>
              <span className="text-sm font-semibold text-slate-400">km</span>
            </div>
            <p className="text-[11px] text-slate-400 mt-1">
              {isHi ? 'मेट्रो, बस, कारपूल व पैदल यात्रा' : 'Via transit, carpool & active modes'}
            </p>
          </div>
        </div>

        {/* Card 2: Modeled Commute Emissions */}
        <div className="glass-card rounded-3xl p-5 border border-slate-800 flex flex-col justify-between relative overflow-hidden group hover:border-rose-500/40 transition-all">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-semibold text-slate-400">{t.impactModeledEmissions}</span>
            <div className="p-2 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400">
              <Cloud className="w-4 h-4" />
            </div>
          </div>
          <div>
            <div className="flex items-baseline gap-1.5">
              <span className="text-3xl font-extrabold text-white font-mono tracking-tight">
                {summary?.total_emissions_kg_co2e.toFixed(2) || '0.00'}
              </span>
              <span className="text-sm font-semibold text-slate-400">kg CO₂e</span>
            </div>
            <p className="text-[11px] text-slate-400 mt-1">
              {isHi ? 'आवंटित व्यक्तिगत उत्सर्जन' : 'Allocated per-passenger emissions'}
            </p>
          </div>
        </div>

        {/* Card 3: Avoided Emissions (Savings) */}
        <div className="glass-card rounded-3xl p-5 border border-emerald-500/30 bg-emerald-950/10 flex flex-col justify-between relative overflow-hidden group hover:border-emerald-500/60 transition-all">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-semibold text-emerald-400">{t.impactAvoidedEmissions}</span>
            <div className="p-2 rounded-xl bg-emerald-500/20 border border-emerald-500/30 text-emerald-300">
              <ShieldCheck className="w-4 h-4" />
            </div>
          </div>
          <div>
            <div className="flex items-baseline gap-1.5">
              <span className="text-3xl font-extrabold text-emerald-300 font-mono tracking-tight">
                +{summary?.total_savings_kg_co2e.toFixed(2) || '0.00'}
              </span>
              <span className="text-sm font-semibold text-emerald-400">kg CO₂e</span>
            </div>
            <p className="text-[11px] text-emerald-400/80 mt-1">
              {isHi ? 'अकेले पेट्रोल कार की तुलना में बचत' : 'Avoided vs solo private petrol car'}
            </p>
          </div>
        </div>

        {/* Card 4: Tree-Months Equivalent (Educational) */}
        <div className="glass-card rounded-3xl p-5 border border-slate-800 flex flex-col justify-between relative overflow-hidden group hover:border-teal-500/40 transition-all">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-1">
              <span className="text-xs font-semibold text-slate-400">{t.impactTreeMonths}</span>
              <span className="text-[9px] px-1.5 py-0.2 rounded bg-slate-800 text-teal-400 border border-slate-700 font-mono">
                EDU
              </span>
            </div>
            <div className="p-2 rounded-xl bg-teal-500/10 border border-teal-500/20 text-teal-400">
              <TreePine className="w-4 h-4" />
            </div>
          </div>
          <div>
            <div className="flex items-baseline gap-1.5">
              <span className="text-3xl font-extrabold text-white font-mono tracking-tight">
                {summary?.tree_months_equivalent?.toFixed(1) || '0.0'}
              </span>
              <span className="text-sm font-semibold text-slate-400">
                {isHi ? 'पेड़-माह' : 'tree-months'}
              </span>
            </div>
            <p className="text-[10px] text-slate-400 mt-1 leading-tight">
              {t.impactTreeDisclaimer}
            </p>
          </div>
        </div>
      </div>

      {/* 3. Scientific Disclosures Banner: Indoor Action Integrity */}
      <div className="p-4 rounded-3xl bg-slate-900/80 border border-slate-800 flex items-start gap-3.5">
        <Info className="w-5 h-5 text-teal-400 shrink-0 mt-0.5" />
        <div className="text-xs text-slate-300 space-y-1">
          <strong className="text-white block font-semibold">
            {isHi ? 'डेटा सत्यनिष्ठा व गणना सिद्धांत:' : 'Scientific Integrity & Calculation Principles:'}
          </strong>
          <p className="leading-relaxed text-slate-400">
            {t.impactIndoorIntegrityNote}
          </p>
        </div>
      </div>

      {/* 4. Interactive Charts Grid (Trend & Modal Split) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Chart: Daily Impact Trend (2 columns on lg) */}
        <div className="lg:col-span-2 glass-panel rounded-3xl p-6 border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-bold text-white flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-emerald-400" />
                <span>{t.impactDailyTrendTitle}</span>
              </h2>
              <p className="text-xs text-slate-400 mt-0.5">{t.impactDailyTrendSubtitle}</p>
            </div>
            <div className="flex items-center gap-3 text-xs">
              <div className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 inline-block" />
                <span className="text-slate-300">{isHi ? 'बचत' : 'Avoided'}</span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-rose-400 inline-block" />
                <span className="text-slate-300">{isHi ? 'उत्सर्जन' : 'Emissions'}</span>
              </div>
            </div>
          </div>

          <div className="h-64 w-full">
            {summary?.daily_trends && summary.daily_trends.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart
                  data={summary.daily_trends}
                  margin={{ top: 10, right: 10, left: -20, bottom: 0 }}
                >
                  <defs>
                    <linearGradient id="impactSavingsGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#10b981" stopOpacity={0.35} />
                      <stop offset="95%" stopColor="#10b981" stopOpacity={0.0} />
                    </linearGradient>
                    <linearGradient id="impactEmissionsGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#f43f5e" stopOpacity={0.25} />
                      <stop offset="95%" stopColor="#f43f5e" stopOpacity={0.0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.5} />
                  <XAxis
                    dataKey="day_label"
                    stroke="#94a3b8"
                    tick={{ fill: '#94a3b8', fontSize: 11 }}
                    tickLine={false}
                  />
                  <YAxis
                    stroke="#94a3b8"
                    tick={{ fill: '#94a3b8', fontSize: 11 }}
                    tickLine={false}
                    unit=" kg"
                  />
                  <Tooltip content={<CustomTrendTooltip />} />
                  <Area
                    type="monotone"
                    dataKey="savings_kg"
                    stroke="#10b981"
                    strokeWidth={2.5}
                    fillOpacity={1}
                    fill="url(#impactSavingsGrad)"
                    name="Avoided CO2e"
                  />
                  <Area
                    type="monotone"
                    dataKey="emissions_kg"
                    stroke="#f43f5e"
                    strokeWidth={2}
                    fillOpacity={1}
                    fill="url(#impactEmissionsGrad)"
                    name="Emissions"
                  />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-slate-500 text-xs">
                {t.impactNoActivities}
              </div>
            )}
          </div>
        </div>

        {/* Right Chart: Modal Split & Distribution (1 column on lg) */}
        <div className="glass-panel rounded-3xl p-6 border border-slate-800 space-y-4 flex flex-col justify-between">
          <div>
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <PieIcon className="w-4 h-4 text-teal-400" />
              <span>{t.impactModalSplitTitle}</span>
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">{t.impactModalSplitSubtitle}</p>
          </div>

          <div className="h-48 w-full flex items-center justify-center">
            {summary?.mode_breakdown && summary.mode_breakdown.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={summary.mode_breakdown}
                    dataKey="distance_km"
                    nameKey={isHi ? 'label_hi' : 'label_en'}
                    cx="50%"
                    cy="50%"
                    innerRadius={45}
                    outerRadius={75}
                    paddingAngle={4}
                  >
                    {summary.mode_breakdown.map((entry, idx) => (
                      <Cell
                        key={`cell-${idx}`}
                        fill={MODE_COLORS[entry.mode] || MODE_COLORS.other}
                      />
                    ))}
                  </Pie>
                  <Tooltip
                    formatter={(val: any, name: any, item: any) => [
                      `${val} km (${item.payload.distance_share_pct}%)`,
                      name,
                    ]}
                    contentStyle={{
                      backgroundColor: '#0f172a',
                      border: '1px solid #334155',
                      borderRadius: '0.75rem',
                      fontSize: '12px',
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="text-slate-500 text-xs text-center">
                {isHi ? 'कोई यात्रा डेटा उपलब्ध नहीं' : 'No modal distribution data'}
              </div>
            )}
          </div>

          {/* Modal Legend List */}
          <div className="space-y-1.5 pt-2 border-t border-slate-800">
            {summary?.mode_breakdown?.slice(0, 4).map((m) => (
              <div key={m.mode} className="flex items-center justify-between text-xs">
                <div className="flex items-center gap-2">
                  <span
                    className="w-2.5 h-2.5 rounded-full"
                    style={{ backgroundColor: MODE_COLORS[m.mode] || MODE_COLORS.other }}
                  />
                  <span className="text-slate-300 font-medium">
                    {isHi ? m.label_hi : m.label_en}
                  </span>
                </div>
                <span className="text-slate-400 font-mono text-[11px]">
                  {m.distance_km} km ({m.distance_share_pct}%)
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* 5. Personalized Sustainability Suggestions */}
      {summary?.suggestions && summary.suggestions.length > 0 && (
        <div className="glass-panel rounded-3xl p-6 border border-slate-800 space-y-4">
          <div>
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-emerald-400" />
              <span>{t.impactSuggestionsTitle}</span>
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">{t.impactSuggestionsSubtitle}</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {summary.suggestions.map((sug) => (
              <div
                key={sug.id}
                className="glass-card rounded-2xl p-4 border border-slate-800 flex flex-col justify-between hover:border-emerald-500/40 transition-all group"
              >
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span
                      className={`text-[10px] uppercase font-bold px-2 py-0.5 rounded-full border ${
                        sug.difficulty === 'easy'
                          ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                          : 'bg-amber-500/10 text-amber-400 border-amber-500/30'
                      }`}
                    >
                      {sug.difficulty}
                    </span>
                    {sug.potential_monthly_savings_kg > 0 && (
                      <span className="text-xs font-mono font-bold text-emerald-400">
                        ~{sug.potential_monthly_savings_kg} kg/mo saved
                      </span>
                    )}
                  </div>
                  <h3 className="text-sm font-bold text-white group-hover:text-emerald-300 transition-colors">
                    {isHi ? sug.title_hi : sug.title_en}
                  </h3>
                  <p className="text-xs text-slate-400 mt-1.5 leading-relaxed">
                    {isHi ? sug.description_hi : sug.description_en}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 6. Action History Log & Pagination */}
      <div className="glass-panel rounded-3xl p-6 border border-slate-800 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div>
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <Calendar className="w-4 h-4 text-emerald-400" />
              <span>{t.impactHistoryTitle}</span>
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">{t.impactHistorySubtitle}</p>
          </div>

          {logs && logs.total_count > 0 && (
            <span className="text-xs font-mono text-slate-400 self-start sm:self-auto">
              {isHi
                ? `कुल गतिविधियां: ${logs.total_count}`
                : `Total Logged: ${logs.total_count} activities`}
            </span>
          )}
        </div>

        {/* Records List */}
        {logs?.items && logs.items.length > 0 ? (
          <div className="space-y-3">
            {logs.items.map((item) => (
              <div
                key={item.log_id}
                className="glass-card rounded-2xl p-4 border border-slate-800/90 flex flex-col md:flex-row md:items-center justify-between gap-3 hover:border-slate-700 transition-all"
              >
                {/* Left: Mode icon + Title + Date */}
                <div className="flex items-start gap-3">
                  <div className="p-2.5 rounded-xl bg-slate-900 border border-slate-700/80 mt-0.5">
                    {getModeIcon(item.mode, item.activity_type)}
                  </div>
                  <div>
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="text-sm font-bold text-white">
                        {item.activity_type === 'purifier_optimized'
                          ? isHi
                            ? 'HEPA प्यूरीफायर अनुकूलन'
                            : 'HEPA Purifier Smog Scheduling'
                          : item.activity_type === 'ventilation_timed'
                          ? isHi
                            ? 'निर्धारित वेंटिलेशन'
                            : 'Timed Afternoon Ventilation'
                          : item.mode?.replace('_', ' ').toUpperCase() || 'COMMUTE'}
                      </span>
                      {item.data_provenance === 'simulated_demo' ? (
                        <span className="text-[10px] px-2 py-0.2 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/20 font-mono">
                          demo
                        </span>
                      ) : (
                        <span className="text-[10px] px-2 py-0.2 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-mono">
                          verified
                        </span>
                      )}
                    </div>
                    <div className="flex items-center gap-2 text-xs text-slate-400 mt-0.5 flex-wrap">
                      <span>{item.activity_date}</span>
                      {item.distance_km > 0 && <span>• {item.distance_km} km</span>}
                      {item.passengers > 1 && (
                        <span>• {item.passengers} {isHi ? 'सवारियां' : 'pax'}</span>
                      )}
                      {item.notes && <span className="italic text-slate-300">"{item.notes}"</span>}
                    </div>
                  </div>
                </div>

                {/* Right: Metrics + Delete Action */}
                <div className="flex items-center justify-between md:justify-end gap-6 pt-2 md:pt-0 border-t md:border-t-0 border-slate-800/60">
                  {/* Emissions vs Savings */}
                  {item.activity_type === 'purifier_optimized' ||
                  item.activity_type === 'ventilation_timed' ? (
                    <div className="text-right">
                      <span className="text-[10px] text-teal-400 block font-semibold uppercase">
                        {isHi ? 'फेफड़े सुरक्षा स्कोर' : 'Lung Exposure Mitigation'}
                      </span>
                      <strong className="text-teal-300 font-mono text-sm">
                        +{item.exposure_avoided_score.toFixed(0)} pts
                      </strong>
                    </div>
                  ) : (
                    <div className="flex items-center gap-4 text-right">
                      <div>
                        <span className="text-[10px] text-rose-400 block font-semibold uppercase">
                          {isHi ? 'उत्सर्जन' : 'Emissions'}
                        </span>
                        <strong className="text-rose-200 font-mono text-xs">
                          {item.per_passenger_emissions_kg_co2e.toFixed(2)} kg
                        </strong>
                      </div>
                      <div>
                        <span className="text-[10px] text-emerald-400 block font-semibold uppercase">
                          {isHi ? 'बचत' : 'Avoided'}
                        </span>
                        <strong className="text-emerald-300 font-mono text-sm">
                          +{item.emission_saved_kg_co2e.toFixed(2)} kg
                        </strong>
                      </div>
                    </div>
                  )}

                  {/* Delete Button */}
                  <button
                    onClick={() => setDeletingLogId(item.log_id)}
                    className="p-2 rounded-xl bg-slate-900 hover:bg-rose-500/20 text-slate-400 hover:text-rose-400 border border-slate-800 hover:border-rose-500/30 transition-all"
                    title={isHi ? 'हटाएं' : 'Delete Log'}
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="p-8 text-center text-slate-500 text-xs">
            {t.impactNoActivities}
          </div>
        )}

        {/* Pagination Controls */}
        {logs && logs.total_count > pageSize && (
          <div className="flex items-center justify-between pt-4 border-t border-slate-800/80 text-xs">
            <span className="text-slate-400">
              {isHi
                ? `पृष्ठ ${page + 1} (कुल ${Math.ceil(logs.total_count / pageSize)})`
                : `Page ${page + 1} of ${Math.ceil(logs.total_count / pageSize)}`}
            </span>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setPage((p) => Math.max(0, p - 1))}
                disabled={page === 0}
                className="flex items-center gap-1 px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-slate-300 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-800 transition-colors"
              >
                <ChevronLeft className="w-3.5 h-3.5" />
                <span>{isHi ? 'पिछला' : 'Previous'}</span>
              </button>
              <button
                onClick={() => setPage((p) => p + 1)}
                disabled={!logs.has_more}
                className="flex items-center gap-1 px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-slate-300 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-800 transition-colors"
              >
                <span>{isHi ? 'अगला' : 'Next'}</span>
                <ChevronRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        )}
      </div>
      </>
      )}

      {/* 7. Modal: Add Activity Dialog */}
      {isAddModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-fadeIn">
          <div className="glass-panel w-full max-w-lg rounded-3xl p-6 lg:p-7 border border-slate-700 shadow-2xl relative space-y-5">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-bold text-white flex items-center gap-2">
                  <PlusCircle className="w-5 h-5 text-emerald-400" />
                  <span>{t.impactAddModalTitle}</span>
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">{t.impactAddModalSubtitle}</p>
              </div>
              <button
                onClick={() => setIsAddModalOpen(false)}
                className="p-1.5 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreateActivity} className="space-y-4">
              {/* Activity Type Selector */}
              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">
                  {t.impactActivityTypeLabel}
                </label>
                <select
                  value={activityType}
                  onChange={(e) => setActivityType(e.target.value as ImpactActivityType)}
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-500"
                >
                  <option value="public_transit">
                    {isHi ? 'सार्वजनिक परिवहन (मेट्रो/बस)' : 'Public Transit (Metro / Bus)'}
                  </option>
                  <option value="carpool">
                    {isHi ? 'कारपूलिंग (साझा सफर)' : 'Carpooling (Shared Ride)'}
                  </option>
                  <option value="ev_transit">
                    {isHi ? 'इलेक्ट्रिक वाहन (EV)' : 'Electric Transit (e-Bus / EV)'}
                  </option>
                  <option value="active_travel">
                    {isHi ? 'सक्रिय शारीरिक यात्रा (पैदल / साइकिल)' : 'Active Travel (Walk / Cycle)'}
                  </option>
                  <option value="purifier_optimized">
                    {isHi ? 'HEPA प्यूरीफायर स्मॉग शेड्यूलिंग' : 'HEPA Purifier Smog Scheduling'}
                  </option>
                  <option value="ventilation_timed">
                    {isHi ? 'निर्धारित वेंटिलेशन' : 'Timed Afternoon Ventilation'}
                  </option>
                </select>
              </div>

              {/* Transit-Only Inputs */}
              {activityType !== 'purifier_optimized' && activityType !== 'ventilation_timed' ? (
                <>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    {/* Mode */}
                    <div>
                      <label className="text-xs font-semibold text-slate-300 block mb-1">
                        {t.impactTransportModeLabel}
                      </label>
                      <select
                        value={transportMode}
                        onChange={(e) => setTransportMode(e.target.value as TransportMode)}
                        className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-500"
                      >
                        <option value="metro">{isHi ? 'मेट्रो रेल' : 'Metro Rail'}</option>
                        <option value="electric_bus">
                          {isHi ? 'इलेक्ट्रिक बस' : 'Electric Bus'}
                        </option>
                        <option value="public_bus">
                          {isHi ? 'सार्वजनिक बस (CNG/डीजल)' : 'City Bus (CNG/Diesel)'}
                        </option>
                        <option value="carpool">{isHi ? 'कारपूलिंग' : 'Carpooling'}</option>
                        <option value="electric_car">
                          {isHi ? 'इलेक्ट्रिक कार (EV)' : 'Electric Car'}
                        </option>
                        <option value="electric_two_wheeler">
                          {isHi ? 'इलेक्ट्रिक 2-व्हीलर (EV)' : 'Electric 2-Wheeler'}
                        </option>
                        <option value="cng_auto">
                          {isHi ? 'साझा CNG ऑटो' : 'Shared CNG Auto'}
                        </option>
                        <option value="two_wheeler">
                          {isHi ? 'पेट्रोल 2-व्हीलर' : 'Petrol 2-Wheeler'}
                        </option>
                        <option value="petrol_car">
                          {isHi ? 'निजी पेट्रोल कार' : 'Petrol Car'}
                        </option>
                        <option value="diesel_car">
                          {isHi ? 'निजी डीजल कार' : 'Diesel Car'}
                        </option>
                        <option value="walking">{isHi ? 'पैदल यात्रा' : 'Walking'}</option>
                        <option value="cycling">{isHi ? 'साइकिलिंग' : 'Cycling'}</option>
                      </select>
                    </div>

                    {/* Distance */}
                    <div>
                      <label className="text-xs font-semibold text-slate-300 block mb-1">
                        {t.impactDistanceLabel}
                      </label>
                      <input
                        type="number"
                        min="0.5"
                        max="150"
                        step="0.5"
                        value={distanceKm}
                        onChange={(e) => setDistanceKm(parseFloat(e.target.value) || 0)}
                        className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-500"
                        required
                      />
                    </div>
                  </div>

                  {/* Passengers */}
                  {['carpool', 'electric_car', 'petrol_car', 'diesel_car'].includes(transportMode) ? (
                    <div>
                      <label className="text-xs font-semibold text-slate-300 block mb-1">
                        {t.impactPassengersLabel}
                      </label>
                      <input
                        type="number"
                        min={transportMode === 'carpool' ? 2 : 1}
                        max="6"
                        value={passengers}
                        onChange={(e) => setPassengers(parseInt(e.target.value, 10) || 1)}
                        className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-500"
                      />
                    </div>
                  ) : null}
                </>
              ) : (
                /* Indoor Mitigation Score */
                <div>
                  <label className="text-xs font-semibold text-slate-300 block mb-1">
                    {t.impactExposureMitigationLabel}
                  </label>
                  <input
                    type="range"
                    min="10"
                    max="100"
                    step="5"
                    value={exposureScore}
                    onChange={(e) => setExposureScore(parseInt(e.target.value, 10))}
                    className="w-full accent-teal-400"
                  />
                  <div className="flex justify-between text-[11px] text-slate-400 mt-1">
                    <span>{isHi ? 'मध्यम सुरक्षा' : 'Moderate Protection'}</span>
                    <strong className="text-teal-400 font-mono">{exposureScore} pts</strong>
                    <span>{isHi ? 'अधिकतम HEPA H13' : 'Peak HEPA H13'}</span>
                  </div>
                </div>
              )}

              {/* Date & Notes */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="text-xs font-semibold text-slate-300 block mb-1">
                    {t.impactDateLabel}
                  </label>
                  <input
                    type="date"
                    value={activityDate}
                    onChange={(e) => setActivityDate(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-500"
                    required
                  />
                </div>
                <div>
                  <label className="text-xs font-semibold text-slate-300 block mb-1">
                    {t.impactNotesLabel}
                  </label>
                  <input
                    type="text"
                    maxLength={100}
                    value={notes}
                    onChange={(e) => setNotes(e.target.value)}
                    placeholder={isHi ? 'जैसे: ऑफिस यात्रा' : 'e.g. Office commute'}
                    className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-500"
                  />
                </div>
              </div>

              {/* Live Scientific Formula Preview */}
              <div className="p-3.5 rounded-2xl bg-slate-900 border border-slate-800 text-xs space-y-1.5">
                <div className="flex items-center justify-between text-slate-300 font-medium">
                  <span>{isHi ? 'वैज्ञानिक गणना पूर्वावलोकन:' : 'Scientific Formula Preview:'}</span>
                  {preview.isIndoor ? (
                    <span className="text-teal-400 font-semibold font-mono">
                      +0.0 kg CO₂ (Exposure Safeguard)
                    </span>
                  ) : (
                    <span className="text-emerald-400 font-bold font-mono">
                      +{preview.savingsKg} kg CO₂e {isHi ? 'बचत' : 'avoided'}
                    </span>
                  )}
                </div>
                <div className="text-[11px] text-slate-400 flex items-center justify-between">
                  <span>
                    {preview.isIndoor
                      ? isHi
                        ? 'वायु शोधक फेफड़ों को धूल से बचाते हैं, वाहन CO2 नहीं घटाते।'
                        : 'Purifier actions mitigate inhaled PM2.5/PM10, not tailpipe CO2.'
                      : `${t.impactPreviewEmissions} ${preview.emissionsKg} kg | Base: ${preview.baselineKg} kg`}
                  </span>
                </div>
              </div>

              {formError && (
                <div className="p-2.5 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs">
                  {formError}
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex items-center justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setIsAddModalOpen(false)}
                  className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-300 hover:text-white hover:bg-slate-800 transition-colors"
                >
                  {t.impactCancelBtn}
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-emerald-500 hover:bg-emerald-600 text-white text-xs font-bold shadow-lg shadow-emerald-500/20 transition-all disabled:opacity-50"
                >
                  <PlusCircle className="w-3.5 h-3.5" />
                  <span>{isSubmitting ? t.impactSaving : t.impactSaveActivityBtn}</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* 8. Modal: Delete Confirmation */}
      {deletingLogId && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-fadeIn">
          <div className="glass-panel w-full max-w-sm rounded-3xl p-6 border border-slate-700 shadow-2xl space-y-4">
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-2xl bg-rose-500/10 border border-rose-500/30 text-rose-400">
                <Trash2 className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-white">{t.impactDeleteConfirmTitle}</h3>
                <p className="text-xs text-slate-400 mt-0.5">{t.impactDeleteConfirmDesc}</p>
              </div>
            </div>

            <div className="flex items-center justify-end gap-2 pt-2">
              <button
                onClick={() => setDeletingLogId(null)}
                className="px-3.5 py-1.5 rounded-xl text-xs font-semibold text-slate-300 hover:bg-slate-800 transition-colors"
              >
                {t.impactCancelBtn}
              </button>
              <button
                onClick={() => handleDeleteActivity(deletingLogId)}
                disabled={isSubmitting}
                className="px-3.5 py-1.5 rounded-xl bg-rose-600 hover:bg-rose-700 text-white text-xs font-bold transition-colors disabled:opacity-50"
              >
                {isSubmitting ? t.impactDeleting : t.impactDeleteBtn}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 9. Modal: Scientific Methodology & Disclosures */}
      {isMethodologyOpen && methodology && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-fadeIn">
          <div className="glass-panel w-full max-w-2xl max-h-[85vh] overflow-y-auto rounded-3xl p-6 lg:p-8 border border-slate-700 shadow-2xl relative space-y-5">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div>
                <h3 className="text-lg font-bold text-white flex items-center gap-2">
                  <HelpCircle className="w-5 h-5 text-teal-400" />
                  <span>{t.impactMethodologyTitle}</span>
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">{t.impactMethodologySubtitle}</p>
              </div>
              <button
                onClick={() => setIsMethodologyOpen(false)}
                className="p-1.5 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-4 text-xs leading-relaxed text-slate-300">
              <div className="p-3.5 rounded-2xl bg-slate-900 border border-slate-800 space-y-1">
                <h4 className="font-bold text-white flex items-center gap-1.5">
                  <Zap className="w-4 h-4 text-amber-400" />
                  <span>1. National Grid Emission Factor (CEA v19)</span>
                </h4>
                <p className="text-slate-400">
                  Electric modes (Metro Rail, e-Buses, EVs) evaluate indirect upstream emissions
                  using India's Central Electricity Authority baseline:{' '}
                  <strong className="text-white">
                    {methodology.grid_emission_factor_g_per_kwh} g CO₂/kWh
                  </strong>
                  . Electric vehicles are never described as having zero emissions.
                </p>
                <span className="text-[11px] text-slate-500 block italic">
                  Source: {methodology.grid_factor_source}
                </span>
              </div>

              <div className="p-3.5 rounded-2xl bg-slate-900 border border-slate-800 space-y-1">
                <h4 className="font-bold text-white flex items-center gap-1.5">
                  <Car className="w-4 h-4 text-rose-400" />
                  <span>2. Baseline Comparator Benchmark (ARAI / BEE)</span>
                </h4>
                <p className="text-slate-400">
                  Emissions avoided are measured against a single commuter traveling the identical
                  distance in a solo private petrol car:{' '}
                  <strong className="text-white">
                    {methodology.petrol_car_baseline_factor_g_per_km} g CO₂e/km
                  </strong>
                  .
                </p>
                <span className="text-[11px] text-slate-500 block italic">
                  Source: {methodology.baseline_source}
                </span>
              </div>

              <div className="p-3.5 rounded-2xl bg-slate-900 border border-slate-800 space-y-1">
                <h4 className="font-bold text-white flex items-center gap-1.5">
                  <Train className="w-4 h-4 text-emerald-400" />
                  <span>3. Metro Rail Passenger Allocation (DMRC)</span>
                </h4>
                <p className="text-slate-400">
                  Delhi Metro emissions are benchmarked at{' '}
                  <strong className="text-white">
                    {methodology.metro_factor_g_per_pax_km} g CO₂e/passenger-km
                  </strong>
                  . Because this factor is already passenger-allocated, it is never divided by
                  occupancy a second time.
                </p>
                <span className="text-[11px] text-slate-500 block italic">
                  Source: {methodology.metro_source}
                </span>
              </div>

              <div className="p-3.5 rounded-2xl bg-slate-900 border border-slate-800 space-y-1">
                <h4 className="font-bold text-white flex items-center gap-1.5">
                  <TreePine className="w-4 h-4 text-teal-400" />
                  <span>4. Educational Tree-Month Equivalency</span>
                </h4>
                <p className="text-slate-400">
                  Based on US EPA Greenhouse Gas Equivalencies, an urban mature tree absorbs
                  approximately{' '}
                  <strong className="text-white">
                    {methodology.tree_monthly_absorption_kg} kg CO₂ per month
                  </strong>{' '}
                  (~21 kg/year). This is an illustrative indicator to help users conceptualize
                  quantities; it does not represent certified carbon offsets or trees planted.
                </p>
                <span className="text-[11px] text-slate-500 block italic">
                  Source: {methodology.tree_source}
                </span>
              </div>

              <div className="p-3.5 rounded-2xl bg-slate-900 border border-slate-800 space-y-1">
                <h4 className="font-bold text-white flex items-center gap-1.5">
                  <Wind className="w-4 h-4 text-cyan-400" />
                  <span>5. Indoor Air Safeguard Integrity</span>
                </h4>
                <p className="text-slate-400">{methodology.indoor_action_disclaimer}</p>
              </div>
            </div>

            <div className="flex justify-end pt-2">
              <button
                onClick={() => setIsMethodologyOpen(false)}
                className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-white text-xs font-semibold transition-colors"
              >
                {isHi ? 'बंद करें' : 'Close'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
