import React from 'react';
import {
  Wind,
  MapPin,
  RefreshCw,
  Languages,
  Users,
  LayoutDashboard,
  Calendar,
  Home,
  MessageSquare,
  Navigation,
  Leaf,
  User,
  Cloud,
  LogOut,
} from 'lucide-react';
import { useApp } from '../../context/AppContext';
import { translations } from '../../utils/translations';

export const Navbar: React.FC = () => {
  const {
    activeTab,
    setActiveTab,
    stations,
    selectedStationId,
    setSelectedStationId,
    language,
    setLanguage,
    refreshData,
    loading,
    familyProfile,
    isDemoData,
    user,
    logout,
    persistenceStatus,
    isFirebaseAvailable,
    setAuthModalOpen,
  } = useApp();

  const t = translations[language];

  const activeSensitivitiesCount = [
    familyProfile.hasChildren,
    familyProfile.hasSeniors,
    familyProfile.hasRespiratoryCondition,
    familyProfile.isPregnant,
  ].filter(Boolean).length;

  return (
    <header className="sticky top-0 z-50 glass-panel border-b border-slate-800/80 px-4 lg:px-8 py-3">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-3">
        {/* Brand & Logo + Module Tabs */}
        <div className="flex items-center justify-between w-full md:w-auto gap-4">
          <div className="flex items-center gap-3">
            <div className="relative flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-700 shadow-lg shadow-emerald-500/20 text-white">
              <Wind className="w-5 h-5 animate-pulse" />
              <span className="absolute -top-1 -right-1 flex h-3 w-3">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
              </span>
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xl font-extrabold tracking-tight bg-gradient-to-r from-white via-slate-100 to-slate-400 bg-clip-text text-transparent">
                  {t.appName.replace(/\s*AI$/, '')}{' '}
                  <span className="text-emerald-400 font-semibold text-xs px-1.5 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/30">
                    AI
                  </span>
                </span>
                {isDemoData && (
                  <span className="text-[10px] font-medium tracking-wide uppercase px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/30">
                    {t.demoMode}
                  </span>
                )}
              </div>
              <p className="text-xs text-slate-400 font-normal">{t.appSubtitle}</p>
            </div>
          </div>

          {/* Module Navigation Tabs */}
          <nav className="hidden lg:flex items-center bg-slate-900/90 p-1 rounded-2xl border border-slate-800 ml-2">
            <button
              onClick={() => setActiveTab('dashboard')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold transition-all ${
                activeTab === 'dashboard'
                  ? 'bg-emerald-500 text-white shadow-md shadow-emerald-500/20'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <LayoutDashboard className="w-3.5 h-3.5" />
              <span>{t.dashboardTabTitle}</span>
            </button>
            <button
              onClick={() => setActiveTab('planner')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold transition-all ${
                activeTab === 'planner'
                  ? 'bg-blue-600 text-white shadow-md shadow-blue-500/20'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <Calendar className="w-3.5 h-3.5" />
              <span>{t.plannerTabTitle}</span>
            </button>
            <button
              onClick={() => setActiveTab('indoor')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold transition-all ${
                activeTab === 'indoor'
                  ? 'bg-teal-600 text-white shadow-md shadow-teal-500/20'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <Home className="w-3.5 h-3.5" />
              <span>{t.indoorTabTitle}</span>
            </button>
            <button
              onClick={() => setActiveTab('chat')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold transition-all ${
                activeTab === 'chat'
                  ? 'bg-purple-600 text-white shadow-md shadow-purple-500/20'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <MessageSquare className="w-3.5 h-3.5" />
              <span>{t.chatTabTitle}</span>
            </button>
            <button
              onClick={() => setActiveTab('mobility')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold transition-all ${
                activeTab === 'mobility'
                  ? 'bg-amber-600 text-white shadow-md shadow-amber-500/20'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <Navigation className="w-3.5 h-3.5" />
              <span>{t.mobilityTabTitle}</span>
            </button>
            <button
              onClick={() => setActiveTab('impact')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold transition-all ${
                activeTab === 'impact'
                  ? 'bg-emerald-600 text-white shadow-md shadow-emerald-500/20'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <Leaf className="w-3.5 h-3.5" />
              <span>{t.impactTabTitle}</span>
            </button>
            <button
              onClick={() => setActiveTab('family')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold transition-all ${
                activeTab === 'family'
                  ? 'bg-cyan-600 text-white shadow-md shadow-cyan-500/20'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <Users className="w-3.5 h-3.5" />
              <span>{t.familyTabTitle}</span>
            </button>
          </nav>

          {/* Mobile Refresh Button */}
          <button
            onClick={refreshData}
            disabled={loading}
            className="md:hidden p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors"
            title={t.refreshBtn}
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-emerald-400' : ''}`} />
          </button>
        </div>

        {/* Controls: Station Selector, Family Pill, Language, Refresh */}
        <div className="flex items-center flex-wrap justify-end gap-2.5 w-full md:w-auto">
          {/* Station Selector Dropdown */}
          <div className="relative flex items-center bg-slate-900/90 border border-slate-700/80 rounded-xl px-3 py-1.5 shadow-inner w-full sm:w-auto">
            <MapPin className="w-4 h-4 text-emerald-400 mr-2 shrink-0" />
            <select
              value={selectedStationId}
              onChange={(e) => setSelectedStationId(e.target.value)}
              className="bg-transparent text-sm text-slate-200 font-medium focus:outline-none cursor-pointer pr-2 w-full sm:w-auto"
            >
              {stations.map((st) => (
                <option key={st.id} value={st.id} className="bg-slate-900 text-slate-200">
                  {st.name}, {st.city} {st.is_hotspot ? `🔥 (${t.hotspot})` : ''}
                </option>
              ))}
            </select>
          </div>

          {/* Active Family Sensitivity Pill */}
          <button
            type="button"
            onClick={() => setActiveTab('family')}
            className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-900/90 hover:bg-slate-800/90 border border-slate-700/80 hover:border-cyan-500/50 text-xs text-slate-300 transition-all cursor-pointer"
            title="Open Family Profile & Personalization"
          >
            <Users className="w-3.5 h-3.5 text-cyan-400" />
            <span>
              {t.familyPillLabel}{' '}
              <strong className="text-cyan-300">
                {activeSensitivitiesCount} {t.activeCount}
              </strong>
            </span>
          </button>

          {/* Language Toggle (Hindi / English) */}
          <button
            onClick={() => setLanguage(language === 'en' ? 'hi' : 'en')}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-900/90 hover:bg-slate-800 border border-slate-700/80 text-xs font-semibold text-slate-200 transition-colors"
            title="Switch Language"
          >
            <Languages className="w-3.5 h-3.5 text-emerald-400" />
            <span>{language === 'en' ? 'हिन्दी' : 'English'}</span>
          </button>

          {/* User Auth & Cloud Persistence Button */}
          {user ? (
            <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-900/90 border border-emerald-500/30 text-xs text-slate-200">
              <div className="flex items-center gap-1 text-emerald-400 font-medium">
                <Cloud className="w-3.5 h-3.5" />
                <span className="hidden sm:inline text-[11px]">
                  {persistenceStatus === 'saving'
                    ? t.cloudSaving
                    : persistenceStatus === 'error'
                    ? t.cloudError
                    : t.cloudSynced}
                </span>
              </div>
              <span className="text-slate-600">|</span>
              <span className="font-semibold text-white max-w-[100px] truncate" title={user.email || ''}>
                {user.displayName || user.email?.split('@')[0] || 'User'}
              </span>
              <button
                onClick={logout}
                className="p-1 hover:text-rose-400 rounded transition text-slate-400 ml-0.5"
                title={t.signOut}
              >
                <LogOut className="w-3.5 h-3.5" />
              </button>
            </div>
          ) : (
            <button
              onClick={() => setAuthModalOpen(true)}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-emerald-500/10 hover:bg-emerald-500/20 border border-emerald-500/30 text-xs font-semibold text-emerald-300 transition-colors"
              title={isFirebaseAvailable ? 'Sign In / Register' : 'Guest Mode Active'}
            >
              <User className="w-3.5 h-3.5 text-emerald-400" />
              <span>{isFirebaseAvailable ? t.signIn : t.guestModeLabel}</span>
            </button>
          )}

          {/* Desktop Refresh Button */}
          <button
            onClick={refreshData}
            disabled={loading}
            className="hidden md:flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700/60 text-xs font-medium text-slate-200 transition-colors disabled:opacity-50"
            title={t.refreshBtn}
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-emerald-400' : ''}`} />
            <span>{t.refreshBtn}</span>
          </button>
        </div>
      </div>

      {/* Mobile Tab Switcher */}
      <div className="flex lg:hidden items-center gap-2 mt-3 pt-2.5 border-t border-slate-800/60 overflow-x-auto [scrollbar-width:none] [-ms-overflow-style:none] [&::-webkit-scrollbar]:hidden pb-1 px-1">
        <button
          onClick={() => setActiveTab('dashboard')}
          className={`shrink-0 flex items-center justify-center gap-1.5 px-3 py-2 rounded-xl text-xs font-bold transition-all whitespace-nowrap ${
            activeTab === 'dashboard'
              ? 'bg-emerald-500 text-white shadow-md shadow-emerald-500/20'
              : 'bg-slate-900 text-slate-400 border border-slate-800'
          }`}
        >
          <LayoutDashboard className="w-3.5 h-3.5" />
          <span>{t.dashboardTabTitle}</span>
        </button>
        <button
          onClick={() => setActiveTab('planner')}
          className={`shrink-0 flex items-center justify-center gap-1.5 px-3 py-2 rounded-xl text-xs font-bold transition-all whitespace-nowrap ${
            activeTab === 'planner'
              ? 'bg-blue-600 text-white shadow-md shadow-blue-500/20'
              : 'bg-slate-900 text-slate-400 border border-slate-800'
          }`}
        >
          <Calendar className="w-3.5 h-3.5" />
          <span>{t.plannerTabTitle}</span>
        </button>
        <button
          onClick={() => setActiveTab('indoor')}
          className={`shrink-0 flex items-center justify-center gap-1.5 px-3 py-2 rounded-xl text-xs font-bold transition-all whitespace-nowrap ${
            activeTab === 'indoor'
              ? 'bg-teal-600 text-white shadow-md shadow-teal-500/20'
              : 'bg-slate-900 text-slate-400 border border-slate-800'
          }`}
        >
          <Home className="w-3.5 h-3.5" />
          <span>{t.indoorTabTitle}</span>
        </button>
        <button
          onClick={() => setActiveTab('chat')}
          className={`shrink-0 flex items-center justify-center gap-1.5 px-3 py-2 rounded-xl text-xs font-bold transition-all whitespace-nowrap ${
            activeTab === 'chat'
              ? 'bg-purple-600 text-white shadow-md shadow-purple-500/20'
              : 'bg-slate-900 text-slate-400 border border-slate-800'
          }`}
        >
          <MessageSquare className="w-3.5 h-3.5" />
          <span>{t.chatTabTitle}</span>
        </button>
        <button
          onClick={() => setActiveTab('mobility')}
          className={`shrink-0 flex items-center justify-center gap-1.5 px-3 py-2 rounded-xl text-xs font-bold transition-all whitespace-nowrap ${
            activeTab === 'mobility'
              ? 'bg-amber-600 text-white shadow-md shadow-amber-500/20'
              : 'bg-slate-900 text-slate-400 border border-slate-800'
          }`}
        >
          <Navigation className="w-3.5 h-3.5" />
          <span>{t.mobilityTabTitle}</span>
        </button>
        <button
          onClick={() => setActiveTab('impact')}
          className={`shrink-0 flex items-center justify-center gap-1.5 px-3 py-2 rounded-xl text-xs font-bold transition-all whitespace-nowrap ${
            activeTab === 'impact'
              ? 'bg-emerald-600 text-white shadow-md shadow-emerald-500/20'
              : 'bg-slate-900 text-slate-400 border border-slate-800'
          }`}
        >
          <Leaf className="w-3.5 h-3.5" />
          <span>{t.impactTabTitle}</span>
        </button>
        <button
          onClick={() => setActiveTab('family')}
          className={`shrink-0 flex items-center justify-center gap-1.5 px-3 py-2 rounded-xl text-xs font-bold transition-all whitespace-nowrap ${
            activeTab === 'family'
              ? 'bg-cyan-600 text-white shadow-md shadow-cyan-500/20'
              : 'bg-slate-900 text-slate-400 border border-slate-800'
          }`}
        >
          <Users className="w-3.5 h-3.5" />
          <span>{t.familyTabTitle}</span>
        </button>
      </div>
    </header>
  );
};
