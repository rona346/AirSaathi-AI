import React from 'react';
import { AppProvider, useApp } from './context/AppContext';
import { Navbar } from './components/layout/Navbar';
import { DemoDataBanner } from './components/dashboard/DemoDataBanner';
import { AqiCard } from './components/dashboard/AqiCard';
import { HourlyTrendChart } from './components/dashboard/HourlyTrendChart';
import { PollutantBreakdown } from './components/dashboard/PollutantBreakdown';
import { HealthRecommendations } from './components/dashboard/HealthRecommendations';
import { VulnerabilityAlerts } from './components/dashboard/VulnerabilityAlerts';
import { QuickModuleNav } from './components/dashboard/QuickModuleNav';
import { DailyPlanner } from './components/planner/DailyPlanner';
import { IndoorAssistant } from './components/indoor/IndoorAssistant';
import { ChatAssistant } from './components/chat/ChatAssistant';
import { Footer } from './components/layout/Footer';
import { AlertCircle, RefreshCw, Loader2 } from 'lucide-react';
import { translations } from './utils/translations';

const DashboardContent: React.FC = () => {
  const { loading, error, refreshData, currentAqi, language } = useApp();
  const t = translations[language];

  // Loading State
  if (loading && !currentAqi) {
    return (
      <div className="min-h-[70vh] flex flex-col items-center justify-center gap-4 text-center px-4">
        <div className="relative">
          <Loader2 className="w-12 h-12 text-emerald-400 animate-spin" />
          <div className="absolute inset-0 rounded-full blur-md bg-emerald-500/20 pointer-events-none" />
        </div>
        <div>
          <h2 className="text-lg font-bold text-white">
            {t.loadingTitle}
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            {t.loadingSubtitle}
          </p>
        </div>
      </div>
    );
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

  if (activeTab === 'planner') {
    return (
      <main className="max-w-7xl mx-auto px-4 lg:px-8 py-6">
        <DailyPlanner />
      </main>
    );
  }

  if (activeTab === 'indoor') {
    return (
      <main className="max-w-7xl mx-auto px-4 lg:px-8 py-6">
        <IndoorAssistant />
      </main>
    );
  }

  if (activeTab === 'chat') {
    return (
      <main className="max-w-7xl mx-auto px-4 lg:px-8 py-6">
        <ChatAssistant />
      </main>
    );
  }

  return <DashboardContent />;
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
      </div>
    </AppProvider>
  );
};

export default App;
