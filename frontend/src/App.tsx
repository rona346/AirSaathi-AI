import React, { Suspense } from 'react';
import { AppProvider, useApp } from './context/AppContext';
import { Navbar } from './components/layout/Navbar';
import { DemoDataBanner } from './components/dashboard/DemoDataBanner';
import { AqiCard } from './components/dashboard/AqiCard';
import { HourlyTrendChart } from './components/dashboard/HourlyTrendChart';
import { PollutantBreakdown } from './components/dashboard/PollutantBreakdown';
import { HealthRecommendations } from './components/dashboard/HealthRecommendations';
import { VulnerabilityAlerts } from './components/dashboard/VulnerabilityAlerts';
import { QuickModuleNav } from './components/dashboard/QuickModuleNav';
import { AuthModal } from './components/auth/AuthModal';
import { Footer } from './components/layout/Footer';
import { AlertCircle, RefreshCw, Loader2 } from 'lucide-react';
import { translations } from './utils/translations';

// Lazy-loaded assistant modules for optimal bundle code-splitting
const DailyPlanner = React.lazy(() =>
  import('./components/planner/DailyPlanner').then((m) => ({ default: m.DailyPlanner }))
);
const IndoorAssistant = React.lazy(() =>
  import('./components/indoor/IndoorAssistant').then((m) => ({ default: m.IndoorAssistant }))
);
const ChatAssistant = React.lazy(() =>
  import('./components/chat/ChatAssistant').then((m) => ({ default: m.ChatAssistant }))
);
const MobilityAssistant = React.lazy(() =>
  import('./components/mobility/MobilityAssistant').then((m) => ({ default: m.MobilityAssistant }))
);
const ImpactTracker = React.lazy(() =>
  import('./components/impact/ImpactTracker').then((m) => ({ default: m.ImpactTracker }))
);
const FamilyProfileAssistant = React.lazy(() =>
  import('./components/family/FamilyProfileAssistant').then((m) => ({ default: m.FamilyProfileAssistant }))
);

const ModuleFallback: React.FC = () => (
  <div className="min-h-[50vh] flex flex-col items-center justify-center gap-3 text-center">
    <div className="relative">
      <Loader2 className="w-8 h-8 text-emerald-400 animate-spin" />
      <div className="absolute inset-0 rounded-full blur-md bg-emerald-500/20 pointer-events-none" />
    </div>
    <span className="text-xs text-slate-400 font-medium">Loading AirSaathi module...</span>
  </div>
);

const DashboardSkeleton: React.FC<{ loadingTitle: string; loadingSubtitle: string }> = ({
  loadingTitle,
  loadingSubtitle,
}) => (
  <main className="max-w-7xl mx-auto px-4 lg:px-8 py-6 space-y-8 animate-pulse" aria-busy="true" aria-label={loadingTitle}>
    {/* Loading indicator bar */}
    <div className="flex items-center justify-between pb-2 border-b border-slate-800/60">
      <div className="flex items-center gap-2.5">
        <Loader2 className="w-4 h-4 text-emerald-400 animate-spin" />
        <span className="text-xs font-semibold text-slate-300">{loadingTitle}</span>
      </div>
      <span className="text-[11px] text-slate-500">{loadingSubtitle}</span>
    </div>

    {/* Hero AQI Card Skeleton */}
    <div className="glass-panel rounded-3xl p-6 lg:p-8 border border-slate-800 space-y-6">
      <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6">
        <div className="space-y-3 w-full lg:w-1/2">
          <div className="h-4 w-32 bg-slate-800 rounded-md" />
          <div className="h-8 w-64 bg-slate-800 rounded-lg" />
          <div className="flex items-baseline gap-4 pt-2">
            <div className="h-16 w-28 bg-slate-800 rounded-2xl" />
            <div className="h-8 w-36 bg-slate-800 rounded-xl" />
          </div>
        </div>
        <div className="w-full lg:w-72 h-36 bg-slate-900/80 rounded-2xl border border-slate-800/90" />
      </div>
      <div className="pt-4 border-t border-slate-800/80 space-y-2">
        <div className="h-3 w-full bg-slate-800 rounded-full" />
      </div>
    </div>

    {/* Hourly Trend Skeleton */}
    <div className="glass-panel rounded-3xl p-6 lg:p-8 border border-slate-800 space-y-4">
      <div className="flex items-center justify-between">
        <div className="space-y-2">
          <div className="h-5 w-48 bg-slate-800 rounded-md" />
          <div className="h-3 w-64 bg-slate-800 rounded-md" />
        </div>
        <div className="h-10 w-44 bg-slate-800 rounded-xl hidden sm:block" />
      </div>
      <div className="h-64 w-full bg-slate-900/60 rounded-2xl border border-slate-800/60" />
    </div>

    {/* Pollutant Breakdown Grid Skeleton */}
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      {[1, 2, 3, 4, 5, 6].map((i) => (
        <div key={i} className="glass-card rounded-2xl p-5 border border-slate-800 h-44 space-y-3">
          <div className="flex justify-between">
            <div className="h-5 w-16 bg-slate-800 rounded" />
            <div className="h-5 w-20 bg-slate-800 rounded-full" />
          </div>
          <div className="h-8 w-24 bg-slate-800 rounded-lg" />
          <div className="h-3 w-full bg-slate-800 rounded mt-4" />
        </div>
      ))}
    </div>
  </main>
);

const DashboardContent: React.FC = () => {
  const { loading, error, refreshData, currentAqi, language } = useApp();
  const t = translations[language];

  // Loading State - Dashboard Skeleton prevents layout shift
  if (loading && !currentAqi) {
    return <DashboardSkeleton loadingTitle={t.loadingTitle} loadingSubtitle={t.loadingSubtitle} />;
  }

  // Error State
  if (error && !currentAqi) {
    return (
      <div className="min-h-[60vh] flex flex-col items-center justify-center gap-4 text-center px-4">
        <div className="p-4 rounded-2xl bg-rose-500/10 text-rose-400 border border-rose-500/20">
          <AlertCircle className="w-10 h-10" />
        </div>
        <div className="max-w-md">
          <h2 className="text-lg font-bold text-white">
            {t.errorTitle}
          </h2>
          <p className="text-xs text-slate-400 mt-1.5 leading-relaxed">{error}</p>
        </div>
        <button
          onClick={refreshData}
          className="mt-2 flex items-center gap-2 px-4 py-2 rounded-xl bg-emerald-500 hover:bg-emerald-600 text-white font-semibold text-xs shadow-lg shadow-emerald-500/20 transition-all"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>{t.retryBtn}</span>
        </button>
      </div>
    );
  }

  return (
    <main className="max-w-7xl mx-auto px-4 lg:px-8 py-6 space-y-8">
      {/* Demonstration Banner */}
      <DemoDataBanner />

      {/* Hero AQI Card & Dispersion Telemetry */}
      <AqiCard />

      {/* 24-Hour Diurnal Projection Area Chart */}
      <HourlyTrendChart />

      {/* Pollutant Breakdown Grid (PM2.5, PM10, NO2, SO2, CO, O3) */}
      <PollutantBreakdown />

      {/* Family Vulnerability Customization & Demographics Guard */}
      <VulnerabilityAlerts />

      {/* Health Actions & Protection Recommendations */}
      <HealthRecommendations />

      {/* Modular Pipeline & Upcoming Architecture Roadmap */}
      <QuickModuleNav />
    </main>
  );
};

const MainContent: React.FC = () => {
  const { activeTab } = useApp();

  return (
    <Suspense fallback={<ModuleFallback />}>
      {activeTab === 'planner' && (
        <main className="max-w-7xl mx-auto px-4 lg:px-8 py-6">
          <DailyPlanner />
        </main>
      )}
      {activeTab === 'indoor' && (
        <main className="max-w-7xl mx-auto px-4 lg:px-8 py-6">
          <IndoorAssistant />
        </main>
      )}
      {activeTab === 'chat' && (
        <main className="max-w-7xl mx-auto px-4 lg:px-8 py-6">
          <ChatAssistant />
        </main>
      )}
      {activeTab === 'mobility' && (
        <main className="max-w-7xl mx-auto px-4 lg:px-8 py-6">
          <MobilityAssistant />
        </main>
      )}
      {activeTab === 'impact' && (
        <main className="max-w-7xl mx-auto px-4 lg:px-8 py-6">
          <ImpactTracker />
        </main>
      )}
      {activeTab === 'family' && (
        <main className="max-w-7xl mx-auto px-4 lg:px-8 py-6">
          <FamilyProfileAssistant />
        </main>
      )}
      {activeTab === 'dashboard' && <DashboardContent />}
    </Suspense>
  );
};

const AuthModalWrapper: React.FC = () => {
  const { authModalOpen, setAuthModalOpen } = useApp();
  return <AuthModal isOpen={authModalOpen} onClose={() => setAuthModalOpen(false)} />;
};

export const App: React.FC = () => {
  return (
    <AppProvider>
      <div className="min-h-screen flex flex-col bg-slate-950 text-slate-100 selection:bg-emerald-500 selection:text-white">
        <Navbar />
        <div className="flex-1">
          <MainContent />
        </div>
        <Footer />
        <AuthModalWrapper />
      </div>
    </AppProvider>
  );
};

export default App;
