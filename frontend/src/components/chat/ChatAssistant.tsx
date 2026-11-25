import React, { useState, useRef, useEffect } from 'react';
import {
  Send,
  Bot,
  User,
  Sparkles,
  ShieldCheck,
  RotateCcw,
  AlertCircle,
  MapPin,
  Activity,
  Info,
  CornerDownLeft,
  Loader2,
} from 'lucide-react';
import { useApp } from '../../context/AppContext';
import { fetchChatMessage } from '../../services/api';
import { ChatMessage, ChatResponse } from '../../types/chat';
import { translations } from '../../utils/translations';
import { getAqiCategory, getAqiCategoryLabel } from '../../utils/aqiUtils';

interface ExtendedChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  responseMeta?: Partial<ChatResponse>;
}

export const ChatAssistant: React.FC = () => {
  const {
    currentAqi,
    selectedStationId,
    stations,
    language,
    familyProfile,
    householdInput,
    isDemoData,
  } = useApp();

  const t = translations[language];
  const station = stations.find((s) => s.id === selectedStationId) || stations[0];
  const aqiCategory = currentAqi ? getAqiCategory(currentAqi.aqi) : null;

  const [messages, setMessages] = useState<ExtendedChatMessage[]>(() => [
    {
      id: 'welcome-0',
      role: 'assistant',
      content:
        language === 'hi'
          ? `**नमस्ते! मैं एयरसाथी AI पर्यावरण सहायक हूँ।**\n\nवर्तमान में **${
              station ? station.name : 'दिल्ली'
            }** पर वायु गुणवत्ता सूचकांक **${
              currentAqi ? currentAqi.aqi : 379
            }** (${
              aqiCategory ? getAqiCategoryLabel(aqiCategory, language) : 'बहुत खराब'
            }) दर्ज है।\n\nआप मुझसे प्रदूषण से बचाव, मास्क का चुनाव, बच्चों/बुजुर्गों की सुरक्षा या इनडोर वायु सुधार के विषय में कोई भी प्रश्न पूछ सकते हैं।`
          : `**Hello! I am your AirSaathi AI Environmental Assistant.**\n\nCurrently, **${
              station ? station.name : 'Delhi'
            }** is reporting an AQI of **${
              currentAqi ? currentAqi.aqi : 379
            }** (${
              aqiCategory ? getAqiCategoryLabel(aqiCategory, language) : 'Very Poor'
            }).\n\nFeel free to ask about smog precautions, certified respirators, outdoor activities, or optimizing indoor air quality.`,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      responseMeta: {
        ai_provider: 'expert-rules-fallback',
        ai_generated: false,
        suggested_followups:
          language === 'hi'
            ? [
                'PM2.5 और PM10 में क्या अंतर है?',
                'आज बच्चों को स्मॉग से कैसे बचाएं?',
                'क्या वर्तमान एक्यूआई में सुबह दौड़ना सुरक्षित है?',
                'क्या घर के पौधे HEPA फिल्टर की जगह ले सकते हैं?',
              ]
            : [
                'What is the difference between PM2.5 and PM10?',
                'How should I protect children during peak morning smog?',
                'Is running or morning walking safe in current AQI?',
                'Can indoor snake plants replace a HEPA air purifier?',
              ],
      },
    },
  ]);

  const [inputMessage, setInputMessage] = useState('');
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, sending]);

  const starterQuestions = [
    t.chatStarter1,
    t.chatStarter2,
    t.chatStarter3,
    t.chatStarter4,
  ];

  const handleSendMessage = async (textToSend?: string) => {
    const rawText = textToSend !== undefined ? textToSend : inputMessage;
    const trimmed = rawText.trim();
    if (!trimmed || sending) return;

    if (trimmed.length > 1000) {
      setError('Message exceeds 1000 character limit.');
      return;
    }

    setError(null);
    setInputMessage('');

    const userMsgId = `user-${Date.now()}`;
    const userMsg: ExtendedChatMessage = {
      id: userMsgId,
      role: 'user',
      content: trimmed,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setSending(true);

    try {
      // Build history for backend (bounded to last 8 turns)
      const chatHistory: ChatMessage[] = messages.slice(-8).map((m) => ({
        role: m.role,
        content: m.content,
      }));

      const payload = {
        message: trimmed,
        station_id: selectedStationId,
        language,
        history: chatHistory,
        family_profile: {
          seniors_at_home: familyProfile.hasSeniors,
          children_at_home: familyProfile.hasChildren,
          asthma_or_respiratory: familyProfile.hasRespiratoryCondition,
          pregnant_member: familyProfile.isPregnant,
          pets_at_home: householdInput.has_pets,
        },
        household: householdInput,
      };

      const result = await fetchChatMessage(payload);

      const assistantMsg: ExtendedChatMessage = {
        id: `asst-${Date.now()}`,
        role: 'assistant',
        content: result.data.message,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        responseMeta: result.data,
      };

      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err: any) {
      console.error('Chat error:', err);
      setError(
        language === 'hi'
          ? 'उत्तर प्राप्त करने में असमर्थ। कृपया पुनः प्रयास करें।'
          : 'Unable to retrieve answer. Please try again.'
      );
    } finally {
      setSending(false);
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleResetChat = () => {
    setMessages([
      {
        id: `welcome-${Date.now()}`,
        role: 'assistant',
        content:
          language === 'hi'
            ? `**नमस्ते! मैं एयरसाथी AI पर्यावरण सहायक हूँ।**\n\nवर्तमान में **${
                station ? station.name : 'दिल्ली'
              }** पर वायु गुणवत्ता सूचकांक **${
                currentAqi ? currentAqi.aqi : 379
              }** (${
                aqiCategory ? getAqiCategoryLabel(aqiCategory, language) : 'बहुत खराब'
              }) दर्ज है।\n\nआप मुझसे प्रदूषण से बचाव, मास्क का चुनाव, बच्चों/बुजुर्गों की सुरक्षा या इनडोर वायु सुधार के विषय में कोई भी प्रश्न पूछ सकते हैं।`
            : `**Hello! I am your AirSaathi AI Environmental Assistant.**\n\nCurrently, **${
                station ? station.name : 'Delhi'
              }** is reporting an AQI of **${
                currentAqi ? currentAqi.aqi : 379
              }** (${
                aqiCategory ? getAqiCategoryLabel(aqiCategory, language) : 'Very Poor'
              }).\n\nFeel free to ask about smog precautions, certified respirators, outdoor activities, or optimizing indoor air quality.`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        responseMeta: {
          ai_provider: 'expert-rules-fallback',
          ai_generated: false,
          suggested_followups:
            language === 'hi'
              ? [
                  'PM2.5 और PM10 में क्या अंतर है?',
                  'आज बच्चों को स्मॉग से कैसे बचाएं?',
                  'क्या वर्तमान एक्यूआई में सुबह दौड़ना सुरक्षित है?',
                  'क्या घर के पौधे HEPA फिल्टर की जगह ले सकते हैं?',
                ]
              : [
                  'What is the difference between PM2.5 and PM10?',
                  'How should I protect children during peak morning smog?',
                  'Is running or morning walking safe in current AQI?',
                  'Can indoor snake plants replace a HEPA air purifier?',
                ],
        },
      },
    ]);
    setError(null);
  };

  // Safe lightweight markdown parser for messages
  const renderFormattedContent = (content: string) => {
    const lines = content.split('\n');

    return (
      <div className="space-y-2 text-sm leading-relaxed">
        {lines.map((line, idx) => {
          const trimmed = line.trim();
          if (!trimmed) {
            return <div key={idx} className="h-1" />;
          }

          // Headers
          if (trimmed.startsWith('### ')) {
            return (
              <h4 key={idx} className="text-sm font-bold text-white pt-1">
                {renderInlineStyles(trimmed.slice(4))}
              </h4>
            );
          }
          if (trimmed.startsWith('## ')) {
            return (
              <h3 key={idx} className="text-base font-bold text-white pt-1.5">
                {renderInlineStyles(trimmed.slice(3))}
              </h3>
            );
          }

          // Bullet points
          if (trimmed.startsWith('- ') || trimmed.startsWith('* ')) {
            return (
              <div key={idx} className="flex items-start gap-2 pl-2">
                <span className="text-emerald-400 mt-1 text-xs">•</span>
                <span className="flex-1 text-slate-200">
                  {renderInlineStyles(trimmed.slice(2))}
                </span>
              </div>
            );
          }

          // Numbered lists
          const numMatch = trimmed.match(/^(\d+)\.\s+(.*)$/);
          if (numMatch) {
            return (
              <div key={idx} className="flex items-start gap-2 pl-2">
                <span className="text-purple-400 font-semibold text-xs min-w-[1.2rem]">
                  {numMatch[1]}.
                </span>
                <span className="flex-1 text-slate-200">
                  {renderInlineStyles(numMatch[2])}
                </span>
              </div>
            );
          }

          // Normal paragraph
          return (
            <p key={idx} className="text-slate-200">
              {renderInlineStyles(trimmed)}
            </p>
          );
        })}
      </div>
    );
  };

  // Helper to parse **bold** and `code` inline
  const renderInlineStyles = (text: string) => {
    const parts = text.split(/(\*\*.*?\*\*|`.*?`)/g);
    return parts.map((part, i) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        return (
          <strong key={i} className="font-semibold text-white">
            {part.slice(2, -2)}
          </strong>
        );
      }
      if (part.startsWith('`') && part.endsWith('`')) {
        return (
          <code
            key={i}
            className="px-1 py-0.5 rounded bg-slate-800 text-emerald-400 font-mono text-xs border border-slate-700/50"
          >
            {part.slice(1, -1)}
          </code>
        );
      }
      return part;
    });
  };

  return (
    <div className="space-y-6">
      {/* Header & Station Context Banner */}
      <div className="glass-card rounded-2xl p-5 border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2.5">
            <div className="p-2.5 rounded-xl bg-purple-500/10 border border-purple-500/30 text-purple-400">
              <Bot className="w-5 h-5" />
            </div>
            <div>
              <h1 className="text-xl font-extrabold text-white flex items-center gap-2">
                <span>{t.chatTabTitle}</span>
                <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-purple-500/20 text-purple-300 border border-purple-500/40 flex items-center gap-1">
                  <Sparkles className="w-3 h-3 text-purple-400" />
                  Gemini 2.5 Flash
                </span>
              </h1>
              <p className="text-xs text-slate-400 mt-0.5">{t.chatSubtitle}</p>
            </div>
          </div>
        </div>

        {/* Live Context Telemetry Chip */}
        <div className="flex items-center flex-wrap gap-2">
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-xs">
            <MapPin className="w-3.5 h-3.5 text-emerald-400" />
            <span className="text-slate-300 font-medium">{station ? station.name : 'CPCB Station'}</span>
          </div>

          {currentAqi && (
            <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-xs">
              <Activity className="w-3.5 h-3.5 text-amber-400" />
              <span className="text-slate-400">AQI:</span>
              <strong className="text-white font-bold">{currentAqi.aqi}</strong>
              <span className="text-[10px] px-1.5 py-0.5 rounded font-medium bg-amber-500/20 text-amber-300 border border-amber-500/30">
                {aqiCategory ? getAqiCategoryLabel(aqiCategory, language) : 'CPCB'}
              </span>
            </div>
          )}

          <div className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-xs text-slate-400">
            <span
              className={`w-2 h-2 rounded-full ${
                isDemoData ? 'bg-amber-400' : 'bg-emerald-400'
              } animate-pulse`}
            />
            <span>{isDemoData ? 'Demo CPCB' : 'CPCB Live'}</span>
          </div>

          <button
            onClick={handleResetChat}
            aria-label={t.chatClearTitle}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold border border-slate-700/60 transition-colors ml-auto sm:ml-0"
            title={t.chatClearTitle}
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>{t.chatClearTitle}</span>
          </button>
        </div>
      </div>

      {/* Suggested Starter Questions (Shown when messages <= 1) */}
      {messages.length <= 1 && (
        <div className="glass-card rounded-2xl p-4 border border-slate-800/80 bg-slate-900/40">
          <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2.5 flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5 text-purple-400" />
            {t.chatStarterTitle}
          </p>
          <div className="flex flex-wrap gap-2">
            {starterQuestions.map((q, idx) => (
              <button
                key={idx}
                onClick={() => handleSendMessage(q)}
                className="text-xs px-3 py-1.5 rounded-xl bg-slate-800/80 hover:bg-purple-950/40 text-slate-300 hover:text-purple-300 border border-slate-700 hover:border-purple-500/40 transition-all text-left flex items-center gap-1.5 group"
              >
                <span>{q}</span>
                <CornerDownLeft className="w-3 h-3 text-slate-500 group-hover:text-purple-400 shrink-0" />
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Chat Messages Stream Area */}
      <div className="glass-card rounded-2xl border border-slate-800 p-4 md:p-6 min-h-[460px] max-h-[640px] overflow-y-auto space-y-5">
        {messages.map((msg) => {
          const isUser = msg.role === 'user';
          const meta = msg.responseMeta;

          return (
            <div
              key={msg.id}
              className={`flex items-start gap-3 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}
            >
              {/* Avatar Icon */}
              <div
                className={`w-9 h-9 rounded-xl flex items-center justify-center shrink-0 border ${
                  isUser
                    ? 'bg-blue-600/20 text-blue-400 border-blue-500/30'
                    : 'bg-purple-600/20 text-purple-400 border-purple-500/30'
                }`}
              >
                {isUser ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
              </div>

              {/* Message Bubble & Context */}
              <div className={`max-w-[85%] sm:max-w-[78%] space-y-2`}>
                <div
                  className={`rounded-2xl p-4 border transition-all ${
                    isUser
                      ? 'bg-blue-600/10 border-blue-500/30 text-white shadow-md shadow-blue-500/5'
                      : 'bg-slate-900/90 border-slate-800 text-slate-200 shadow-md'
                  }`}
                >
                  {/* Assistant Engine Badge */}
                  {!isUser && meta && (
                    <div className="flex items-center flex-wrap gap-2 mb-2 pb-2 border-b border-slate-800/80 text-[11px]">
                      {meta.ai_generated ? (
                        <span className="inline-flex items-center gap-1 font-semibold text-purple-300 bg-purple-500/10 px-2 py-0.5 rounded-full border border-purple-500/20">
                          <Sparkles className="w-3 h-3 text-purple-400" />
                          {t.chatAiBadge}
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 font-semibold text-amber-300 bg-amber-500/10 px-2 py-0.5 rounded-full border border-amber-500/20">
                          <ShieldCheck className="w-3 h-3 text-amber-400" />
                          {t.chatRulesBadge}
                        </span>
                      )}

                      {meta.context_used && (
                        <span className="text-slate-400 text-[10px]">
                          CPCB: {meta.context_used.station_name} • AQI {meta.context_used.aqi} (
                          {meta.context_used.prominent_pollutant}) •{' '}
                          {meta.context_used.is_demo_data ? 'Demo' : 'Live'}
                        </span>
                      )}
                    </div>
                  )}

                  {/* Message Content */}
                  {renderFormattedContent(msg.content)}

                  {/* Medical Disclaimer on Assistant Message */}
                  {!isUser && meta?.disclaimer && (
                    <div className="mt-3 pt-2 border-t border-slate-800/60 text-[10px] text-slate-400 flex items-start gap-1.5">
                      <Info className="w-3 h-3 text-amber-400 shrink-0 mt-0.5" />
                      <span>{meta.disclaimer}</span>
                    </div>
                  )}
                </div>

                {/* Suggested Followups Chips Under Assistant Messages */}
                {!isUser && meta?.suggested_followups && meta.suggested_followups.length > 0 && (
                  <div className="space-y-1 pt-1">
                    <p className="text-[11px] font-medium text-slate-400 flex items-center gap-1">
                      <Sparkles className="w-3 h-3 text-purple-400" />
                      <span>{language === 'hi' ? 'अगला प्रश्न पूछें:' : 'Suggested follow-up:'}</span>
                    </p>
                    <div className="flex flex-wrap gap-1.5">
                      {meta.suggested_followups.map((item, fIdx) => (
                        <button
                          key={fIdx}
                          onClick={() => handleSendMessage(item)}
                          disabled={sending}
                          className="text-[11px] px-2.5 py-1 rounded-lg bg-slate-800/80 hover:bg-purple-950/40 text-slate-300 hover:text-purple-300 border border-slate-700/80 hover:border-purple-500/40 transition-colors text-left"
                        >
                          {item}
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {/* Message Timestamp */}
                <div
                  className={`text-[10px] text-slate-400 px-1 ${
                    isUser ? 'text-right' : 'text-left'
                  }`}
                >
                  {msg.timestamp}
                </div>
              </div>
            </div>
          );
        })}

        {/* Sending / Typing Indicator */}
        {sending && (
          <div className="flex items-start gap-3">
            <div className="w-9 h-9 rounded-xl flex items-center justify-center shrink-0 bg-purple-600/20 text-purple-400 border border-purple-500/30">
              <Bot className="w-4 h-4 animate-bounce" />
            </div>
            <div className="rounded-2xl px-4 py-3 bg-slate-900 border border-slate-800 text-slate-300 flex items-center gap-2 text-xs">
              <Loader2 className="w-4 h-4 animate-spin text-purple-400" />
              <span>{t.chatSending}</span>
            </div>
          </div>
        )}

        {/* Error Alert in Stream */}
        {error && (
          <div className="rounded-xl p-3 bg-rose-500/10 border border-rose-500/20 text-rose-400 flex items-center justify-between gap-2 text-xs">
            <div className="flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{error}</span>
            </div>
            <button
              onClick={() => handleSendMessage()}
              className="px-2.5 py-1 rounded-lg bg-rose-500/20 hover:bg-rose-500/30 text-rose-300 font-semibold border border-rose-500/40 text-[11px]"
            >
              {t.retryBtn}
            </button>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Bar & Actions */}
      <div className="glass-card rounded-2xl p-3 border border-slate-800 space-y-2">
        <div className="relative flex items-center gap-2">
          <input
            ref={inputRef}
            id="chat-input-field"
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={t.chatPlaceholder}
            aria-label={t.chatPlaceholder}
            disabled={sending}
            maxLength={1000}
            className="flex-1 bg-slate-900 border border-slate-700/80 rounded-xl px-4 py-3 text-sm text-white placeholder-slate-400 focus:outline-none focus:border-purple-500/60 focus:ring-1 focus:ring-purple-500/50 disabled:opacity-50 transition-all"
          />

          <button
            onClick={() => handleSendMessage()}
            disabled={!inputMessage.trim() || sending}
            aria-label={t.chatSendBtn}
            className="px-4 py-3 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white font-semibold text-xs flex items-center gap-1.5 shadow-lg shadow-purple-600/20 disabled:opacity-50 disabled:cursor-not-allowed transition-all shrink-0"
          >
            {sending ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Send className="w-4 h-4" />
            )}
            <span className="hidden sm:inline">{t.chatSendBtn}</span>
          </button>
        </div>

        {/* Footer Subtext: Character Counter & Medical Disclaimer Notice */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-1 text-[11px] text-slate-400 px-1 pt-1">
          <div className="flex items-center gap-1 text-slate-400">
            <Info className="w-3.5 h-3.5 text-slate-400 shrink-0" />
            <span>{t.chatDisclaimerNote}</span>
          </div>
          <span className="text-slate-400 self-end sm:self-auto font-mono text-[10px]">
            {inputMessage.length} / 1000
          </span>
        </div>
      </div>
    </div>
  );
};
