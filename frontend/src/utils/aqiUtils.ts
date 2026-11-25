import { AqiCategory, GrapStatus, SupportedLanguage } from '../types/aqi';
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

const NCR_CITIES = new Set([
  'delhi',
  'new delhi',
  'noida',
  'greater noida',
  'ghaziabad',
  'gurugram',
  'gurgaon',
  'faridabad',
  'sonipat',
  'sonepat',
  'panipat',
  'meerut',
  'jhajjar',
  'rohtak',
  'hapur',
  'bulandshahr',
  'baghpat',
  'alwar',
  'bharatpur',
  'rewari',
  'palwal',
]);

const NCR_STATES = new Set([
  'delhi',
  'nct of delhi',
  'national capital territory of delhi',
]);

const GRAP_DISCLAIMER_NCR =
  'Indicative stage modeled from ambient CPCB AQI telemetry under the revised CAQM GRAP schedule (September 2026). Statutory invocation or revocation is ordered by the CAQM Sub-Committee based on IMD/IITM meteorological forecasts.';

const GRAP_DISCLAIMER_NON_NCR =
  'GRAP is an emergency response framework under the Commission for Air Quality Management in NCR & Adjoining Areas Act, 2021. Stations outside Delhi-NCR adhere to standard CPCB National Air Quality Index (NAQI) health advisories.';

export function isNcrLocation(city?: string, state?: string): boolean {
  if (city && NCR_CITIES.has(city.trim().toLowerCase())) return true;
  if (state && NCR_STATES.has(state.trim().toLowerCase())) return true;
  return false;
}

export function evaluateGrapFrontend(aqi: number, city?: string, state?: string): GrapStatus {
  if (!isNcrLocation(city, state)) {
    return {
      applicable: false,
      stage: 'None',
      stage_name: 'Not Applicable (Outside Delhi-NCR)',
      aqi_threshold: 'N/A',
      status_type: 'indicative_aqi_based',
      is_official_order: false,
      curbs_summary: [
        'CAQM Graded Response Action Plan (GRAP) is statutory only within the National Capital Region (Delhi-NCR).',
        'Standard CPCB National Air Quality Index (NAQI) health advisories apply.',
      ],
      notice: GRAP_DISCLAIMER_NON_NCR,
    };
  }

  if (aqi <= 200) {
    return {
      applicable: true,
      stage: 'None',
      stage_name: 'Normal (AQI ≤ 200) — No GRAP Curbs Active',
      aqi_threshold: '0–200',
      status_type: 'indicative_aqi_based',
      is_official_order: false,
      curbs_summary: [
        'Standard environmental guidelines and routine dust mitigation.',
        'No emergency vehicular, industrial, or construction curbs active.',
      ],
      notice: GRAP_DISCLAIMER_NCR,
    };
  }

  if (aqi <= 300) {
    return {
      applicable: true,
      stage: 'Stage I',
      stage_name: 'Stage I — Poor (AQI 201–300)',
      aqi_threshold: '201–300',
      status_type: 'indicative_aqi_based',
      is_official_order: false,
      curbs_summary: [
        'Strict enforcement of CAQM Direction on regulated DG set operation, fuel conversion (PNG/bi-fuel/approved retrofits), and emergency-only limits (advanced from Stage II in Sep 2026 revision).',
        'Entry restrictions on BS-IV and below diesel buses entering Delhi from adjoining states (advanced from Stage II in Sep 2026 revision).',
        'Strict dust suppression enforcement at construction & demolition sites (>500 sq m) with anti-smog guns.',
        'Strict prohibition and intensified vigilance against open burning of biomass and municipal solid waste.',
      ],
      notice: GRAP_DISCLAIMER_NCR,
    };
  }

  if (aqi <= 400) {
    return {
      applicable: true,
      stage: 'Stage II',
      stage_name: 'Stage II — Very Poor (AQI 301–400)',
      aqi_threshold: '301–400',
      status_type: 'indicative_aqi_based',
      is_official_order: false,
      curbs_summary: [
        'Daily mechanical sweeping and intensive water sprinkling with chemical dust suppressants on identified high-density corridors.',
        'Augmentation of CNG/electric bus services and increased Delhi Metro trip frequency to maximize public transit mode share.',
        'Enhanced parking fee structures to discourage non-essential private vehicle usage.',
        'Targeted dust suppression and intensive vehicular emissions monitoring across identified pollution hotspots.',
      ],
      notice: GRAP_DISCLAIMER_NCR,
    };
  }

  if (aqi <= 450) {
    return {
      applicable: true,
      stage: 'Stage III',
      stage_name: 'Stage III — Severe (AQI 401–450)',
      aqi_threshold: '401–450',
      status_type: 'indicative_aqi_based',
      is_official_order: false,
      curbs_summary: [
        'Strict ban on non-essential construction and demolition activities across NCR (exempting critical healthcare, defense, metro, railway).',
        'Plying restrictions on BS-III Petrol and BS-IV Diesel 4-wheeler passenger vehicles (LMVs) across Delhi, Gurugram, Faridabad, Ghaziabad, Gautam Buddha Nagar, and Sonipat.',
        'Strict restriction on interstate buses entering Delhi (only EV/CNG/BS-VI diesel buses permitted from NCR states).',
        'Discontinuation of physical classes for children up to Class V; shift to online mode.',
      ],
      notice: GRAP_DISCLAIMER_NCR,
    };
  }

  return {
    applicable: true,
    stage: 'Stage IV',
    stage_name: 'Stage IV — Severe+ (AQI > 450)',
    aqi_threshold: '> 450',
    status_type: 'indicative_aqi_based',
    is_official_order: false,
    curbs_summary: [
      'Strict ban on entry of non-essential trucks into Delhi (exempting LNG/CNG/electric and trucks carrying essential commodities).',
      'Ban on Delhi-registered diesel medium and heavy goods vehicles (BS-IV and below) other than essentials.',
      'Physical classes suspended for grades VI to IX and XI (online mode recommended).',
      '50% capacity advisory for public and private offices with mandatory work-from-home (WFH) for remaining staff.',
    ],
    notice: GRAP_DISCLAIMER_NCR,
  };
}
