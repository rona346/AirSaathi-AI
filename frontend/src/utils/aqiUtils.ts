import { AqiCategory, SupportedLanguage } from '../types/aqi';
export { getAqiCategory, calculateSubindex, concentrationFromSubindex, CPCB_BREAKPOINTS } from './cpcbCalculator';

export function getAqiCategoryLabel(category: AqiCategory, language: SupportedLanguage): string {
  if (language === 'hi') {
    switch (category) {
      case 'Good':
        return 'अच्छा (Good)';
      case 'Satisfactory':
        return 'संतोषजनक (Satisfactory)';
      case 'Moderate':
        return 'मध्यम (Moderate)';
      case 'Poor':
        return 'खराब (Poor)';
      case 'Very Poor':
        return 'बहुत खराब (Very Poor)';
      case 'Severe':
        return 'गंभीर (Severe)';
      case 'Severe+':
        return 'अति-गंभीर (Severe+)';
      default:
        return category;
    }
  }
  return category;
}

export function getAqiColorHex(category: AqiCategory): string {
  switch (category) {
    case 'Good':
      return '#10B981';
    case 'Satisfactory':
      return '#84CC16';
    case 'Moderate':
      return '#EAB308';
    case 'Poor':
      return '#F97316';
    case 'Very Poor':
      return '#EF4444';
    case 'Severe':
      return '#991B1B';
    case 'Severe+':
      return '#6B21A8';
    default:
      return '#94A3B8';
  }
}

export function getAqiBadgeClasses(category: AqiCategory): {
  bg: string;
  text: string;
  border: string;
  glow: string;
} {
  switch (category) {
    case 'Good':
      return {
        bg: 'bg-emerald-500/10',
        text: 'text-emerald-400',
        border: 'border-emerald-500/30',
        glow: 'shadow-emerald-500/20',
      };
    case 'Satisfactory':
      return {
        bg: 'bg-lime-500/10',
        text: 'text-lime-400',
        border: 'border-lime-500/30',
        glow: 'shadow-lime-500/20',
      };
    case 'Moderate':
      return {
        bg: 'bg-yellow-500/10',
        text: 'text-yellow-400',
        border: 'border-yellow-500/30',
        glow: 'shadow-yellow-500/20',
      };
    case 'Poor':
      return {
        bg: 'bg-orange-500/10',
        text: 'text-orange-400',
        border: 'border-orange-500/30',
        glow: 'shadow-orange-500/20',
      };
    case 'Very Poor':
      return {
        bg: 'bg-red-500/10',
        text: 'text-red-400',
        border: 'border-red-500/30',
        glow: 'shadow-red-500/20',
      };
    case 'Severe':
      return {
        bg: 'bg-rose-900/30',
        text: 'text-rose-400',
        border: 'border-rose-700/50',
        glow: 'shadow-rose-900/30',
      };
    case 'Severe+':
      return {
        bg: 'bg-purple-900/30',
        text: 'text-purple-400',
        border: 'border-purple-700/50',
        glow: 'shadow-purple-900/30',
      };
    default:
      return {
        bg: 'bg-slate-800',
        text: 'text-slate-300',
        border: 'border-slate-700',
        glow: 'shadow-none',
      };
  }
}

export function formatTimestamp(isoString: string): string {
  try {
    const d = new Date(isoString);
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: true });
  } catch {
    return 'Just now';
  }
}

export const CPCB_AQI_BANDS = [
  { label: 'Good', min: 0, max: 50, color: '#10B981', labelHi: 'अच्छा' },
  { label: 'Satisfactory', min: 51, max: 100, color: '#84CC16', labelHi: 'संतोषजनक' },
  { label: 'Moderate', min: 101, max: 200, color: '#EAB308', labelHi: 'मध्यम' },
  { label: 'Poor', min: 201, max: 300, color: '#F97316', labelHi: 'खराब' },
  { label: 'Very Poor', min: 301, max: 400, color: '#EF4444', labelHi: 'बहुत खराब' },
  { label: 'Severe', min: 401, max: 500, color: '#991B1B', labelHi: 'गंभीर' },
];
