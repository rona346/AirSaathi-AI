import React from 'react';
import { Calendar, Home, MessageSquare, Navigation, Leaf, UserCheck, ArrowRight, Sparkles } from 'lucide-react';
import { useApp } from '../../context/AppContext';
import { translations } from '../../utils/translations';

export const QuickModuleNav: React.FC = () => {
  const { language, setActiveTab } = useApp();
  const t = translations[language];

  const modules = [
    {
      id: 'routine',
      title: language === 'hi' ? 'AI दैनिक दिनचर्या नियोजक' : 'AI Daily Routine Planner',
      desc: language === 'hi' ? 'स्मॉग से बचाव हेतु सुरक्षित सैर, स्कूल व ऑफिस समय सारणी' : 'Dynamic smog-adjusted school, transit, and workout schedules generated with Gemini',
      icon: Calendar,
      color: 'from-blue-500/20 to-indigo-500/10 text-blue-400 border-blue-500/30',
      status: t.statusActive,
      isAvailable: true,
    },
    {
      id: 'indoor',
      title: language === 'hi' ? 'इनडोर वायु गुणवत्ता सहायक' : 'Indoor Air Quality Assistant',
      desc: language === 'hi' ? 'स्मार्ट HEPA प्यूरीफायर नियंत्रण, खिड़की वेंटिलेशन समय' : 'CADR requirements, filter health tracking, and optimal natural aeration hours',
      icon: Home,
      color: 'from-emerald-500/20 to-teal-500/10 text-emerald-400 border-emerald-500/30',
      status: t.statusActive,
      isAvailable: true,
    },
    {
      id: 'chat',
      title: language === 'hi' ? 'जेमिनी द्विभाषी चैटबॉट' : 'Gemini Hindi/English Assistant',
      desc: language === 'hi' ? 'हिंदी व अंग्रेजी में तात्कालिक परामर्श व वायु प्रदूषण प्रश्नोत्तरी' : 'Conversational intelligence for real-time smog queries, masks, and pediatric care',
      icon: MessageSquare,
      color: 'from-purple-500/20 to-pink-500/10 text-purple-400 border-purple-500/30',
      status: t.statusActive,
      isAvailable: true,
    },
    {
      id: 'mobility',
      title: language === 'hi' ? 'सतत गतिशीलता सहायक' : 'Sustainable Mobility Guide',
      desc: language === 'hi' ? 'कम उत्सर्जन मार्ग, मेट्रो/ई-बस विकल्प व उत्सर्जन तुलना' : 'Low-exposure commuting routes, metro/EV transit planning, and fleet alerts',
      icon: Navigation,
      color: 'from-amber-500/20 to-orange-500/10 text-amber-400 border-amber-500/30',
      status: t.statusActive,
      isAvailable: true,
    },
    {
      id: 'impact',
      title: language === 'hi' ? 'पर्यावरणीय प्रभाव ट्रैकर' : 'Environmental Impact Tracker',
      desc: language === 'hi' ? 'पारिवारिक कार्बन फुटप्रिंट, वायु उत्सर्जन बचत और लक्ष्य' : 'Community emission savings, carbon avoided, and collective green milestones',
      icon: Leaf,
      color: 'from-teal-500/20 to-emerald-500/10 text-teal-400 border-teal-500/30',
      status: t.statusActive,
      isAvailable: true,
    },
    {
      id: 'family',
      title: language === 'hi' ? 'पारिवारिक प्रोफ़ाइल व प्राथमिकताएं' : 'Family Health Preferences',
      desc: language === 'hi' ? 'सदस्यों के अनुसार कस्टम अलर्ट व संवेदनशील स्वास्थ्य रिकॉर्ड' : 'Multi-generational clinical vulnerability tracking and emergency contacts',
      icon: UserCheck,
      color: 'from-sky-500/20 to-cyan-500/10 text-sky-400 border-sky-500/30',
      status: t.statusActive,
    },
  ];

  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-xl font-bold text-white flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-emerald-400" />
          <span>{t.modularSuiteTitle}</span>
        </h2>
        <p className="text-xs text-slate-400 mt-0.5">
          {t.modularSuiteSubtitle}
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {modules.map((m) => {
          const Icon = m.icon;
          return (
            <div
              key={m.id}
              onClick={() => {
                if (m.isAvailable) {
                  if (m.id === 'routine') setActiveTab('planner');
                  if (m.id === 'indoor') setActiveTab('indoor');
                  if (m.id === 'chat') setActiveTab('chat');
                  if (m.id === 'mobility') setActiveTab('mobility');
                  if (m.id === 'impact') setActiveTab('impact');
                  window.scrollTo({ top: 0, behavior: 'smooth' });
                }
              }}
              className={`glass-card rounded-2xl p-5 border border-slate-800 transition-all flex flex-col justify-between group ${
                m.isAvailable ? 'hover:border-blue-500/50 cursor-pointer shadow-lg hover:shadow-blue-500/10' : 'hover:border-slate-700'
              }`}
            >
              <div>
                <div className="flex items-center justify-between mb-3">
                  <div className={`p-2.5 rounded-xl bg-gradient-to-br ${m.color} border`}>
                    <Icon className="w-5 h-5" />
                  </div>
                  <span
                    className={`text-[10px] font-semibold uppercase tracking-wider px-2 py-0.5 rounded-full border ${
                      m.isAvailable
                        ? 'bg-blue-500/15 text-blue-300 border-blue-500/30'
                        : 'bg-slate-800 text-slate-400 border-slate-700'
                    }`}
                  >
                    {m.status}
                  </span>
                </div>
                <h3 className="text-base font-bold text-white group-hover:text-emerald-400 transition-colors">
                  {m.title}
                </h3>
                <p className="text-xs text-slate-400 mt-1.5 leading-relaxed">
                  {m.desc}
                </p>
              </div>

              <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400 group-hover:text-slate-200 transition-colors">
                <span>{m.isAvailable ? (language === 'hi' ? 'प्लानर खोलें' : 'Launch Planner') : t.viewArchitecture}</span>
                <ArrowRight className="w-3.5 h-3.5 transform group-hover:translate-x-1 transition-transform" />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
