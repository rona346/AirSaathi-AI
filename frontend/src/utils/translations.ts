import { SupportedLanguage } from '../types/aqi';

export interface Translations {
  appName: string;
  appSubtitle: string;
  demoMode: string;
  demoModeLong: string;
  demoBaseline: string;
  demoNotice: string;
  showDetails: string;
  hideDetails: string;
  benchmarkSource: string;
  simulatedTime: string;
  integrityStandard: string;
  zeroHallucinationPolicy: string;
  lastUpdated: string;
  prominentPollutant: string;
  hotspot: string;
  dispersionConditions: string;
  temperature: string;
  humidity: string;
  wind: string;
  visibility: string;
  boundaryLayer: string;
  trappingPollutants: string;
  naqiScale: string;
  currentValue: string;
  scale0500: string;
  pollutantBreakdownTitle: string;
  pollutantBreakdownSubtitle: string;
  cpcbLimit: string;
  whoBenchmark: string;
  nationalStandard: string;
  whoGuideline: string;
  withinLimit: string;
  aboveLimit: string;
  subIndex: string;
  maxScale: string;
  diurnalTitle: string;
  diurnalSubtitle: string;
  peakDangerWindow: string;
  safestOutdoorWindow: string;
  inversionFootnote: string;
  diurnalSource: string;
  moderateLimit: string;
  poorLimit: string;
  severeLimit: string;
  healthAdvisoryTitle: string;
  healthAdvisorySubtitle: string;
  maskRecommendation: string;
  maskNote: string;
  purifierRecommendation: string;
  purifierNote: string;
  outdoorExercise: string;
  outdoorNote: string;
  ventilationWindow: string;
  ventilationNote: string;
  familyGuardTitle: string;
  familyGuardSubtitle: string;
  childrenToggle: string;
  seniorsToggle: string;
  asthmaToggle: string;
  maternalToggle: string;
  childrenProtocolTitle: string;
  childrenProtocolNote: string;
  seniorsProtocolTitle: string;
  seniorsProtocolNote: string;
  asthmaProtocolTitle: string;
  asthmaProtocolNote: string;
  maternalProtocolTitle: string;
  maternalProtocolAdvice: string;
  maternalProtocolNote: string;
  modularSuiteTitle: string;
  modularSuiteSubtitle: string;
  statusNext: string;
  statusPlanned: string;
  statusActive: string;
  viewArchitecture: string;
  footerMission: string;
  footerCompliance: string;
  footerZeroHallucination: string;
  footerStack: string;
  loadingTitle: string;
  loadingSubtitle: string;
  errorTitle: string;
  retryBtn: string;
  refreshBtn: string;
  familyPillLabel: string;
  activeCount: string;
}

export const translations: Record<SupportedLanguage, Translations> = {
  en: {
    appName: 'AirSaathi AI',
    appSubtitle: 'Urban Air Quality & Smog Intelligence',
    demoMode: 'Demo Mode',
    demoModeLong: 'Demonstration Data Mode',
    demoBaseline: 'Simulated CPCB Baseline',
    demoNotice:
      'Measurements currently reflect realistic historical winter smog patterns calibrated against CPCB monitoring stations. Live continuous sensor feeds and Gemini AI reasoning are architected for subsequent module integration.',
    showDetails: 'Provenance & Source',
    hideDetails: 'Hide Details',
    benchmarkSource: 'Primary Benchmark Source',
    simulatedTime: 'Simulated Timestamp',
    integrityStandard: 'Data Integrity Standard',
    zeroHallucinationPolicy: 'Zero Synthetic Hallucination Policy',
    lastUpdated: 'Last Updated:',
    prominentPollutant: 'Prominent:',
    hotspot: 'Pollution Hotspot',
    dispersionConditions: 'Atmospheric Dispersion',
    temperature: 'Temperature',
    humidity: 'Humidity',
    wind: 'Wind',
    visibility: 'Visibility',
    boundaryLayer: 'Boundary Layer (Inversion Height)',
    trappingPollutants: '(Trapping pollutants)',
    naqiScale: 'National Air Quality Scale (NAQI)',
    currentValue: 'Current:',
    scale0500: 'Scale 0-500',
    pollutantBreakdownTitle: 'Real-time Pollutant Breakdown',
    pollutantBreakdownSubtitle:
      'Continuous measurements benchmarked against CPCB 24-hr standards & WHO limits',
    cpcbLimit: 'CPCB Limit',
    whoBenchmark: 'WHO Benchmark',
    nationalStandard: 'National Standard (CPCB):',
    whoGuideline: 'WHO Guideline:',
    withinLimit: '(Within Limit)',
    aboveLimit: 'x limit',
    subIndex: 'Sub-index:',
    maxScale: 'Max: 500',
    diurnalTitle: '24-Hour Diurnal AQI Projection',
    diurnalSubtitle:
      'Hourly progression reflecting morning smog inversion vs. afternoon atmospheric dispersion',
    peakDangerWindow: 'Peak Danger Window',
    safestOutdoorWindow: 'Safest Outdoor Window',
    inversionFootnote:
      'Nocturnal surface radiation inversion typically lifts around 11:30 AM in winter',
    diurnalSource:
      'Source: Diurnal CAAQMS model calibrated for Northern Plain winter conditions',
    moderateLimit: 'Moderate Limit (200)',
    poorLimit: 'Poor Limit (300)',
    severeLimit: 'Severe Threshold (400)',
    healthAdvisoryTitle: 'Health Advisory & Action Guidelines',
    healthAdvisorySubtitle: 'Evidence-based mitigation tailored to current exposure severity',
    maskRecommendation: 'Mask Recommendation',
    maskNote: 'Cloth & surgical masks do not filter PM2.5 aerosols.',
    purifierRecommendation: 'Air Purifier Setting',
    purifierNote: 'Maintain CADR ≥ 2.5 air changes per hour (ACH).',
    outdoorExercise: 'Outdoor Exercise',
    outdoorNote: 'Deep breathing increases ultrafine particulate deposition by 4x.',
    ventilationWindow: 'Ventilation Window',
    ventilationNote: 'Do not aerate before 11:30 AM or after sunset in smog season.',
    familyGuardTitle: 'Family Vulnerability Guard',
    familyGuardSubtitle:
      'Toggle household demographics for personalized clinical risk stratification',
    childrenToggle: 'Children',
    seniorsToggle: 'Seniors (60+)',
    asthmaToggle: 'Asthma / Cardiac',
    maternalToggle: 'Maternal / Pregnancy',
    childrenProtocolTitle: 'Children & Infants Protocol',
    childrenProtocolNote:
      'Developing lungs breathe 50% more air per kg of body weight than adults. Keep school bus windows closed.',
    seniorsProtocolTitle: 'Senior Citizens (60+) Cardiorespiratory Protection',
    seniorsProtocolNote:
      'High PM2.5 levels trigger arterial vasoconstriction and elevated blood pressure. Reschedule morning park walks to 2:00 PM indoors.',
    asthmaProtocolTitle: 'Asthma / COPD / Cardiac Patient Warning',
    asthmaProtocolNote:
      'Ensure rescue inhaler and spacer are bedside. Check peak flow meter readings twice daily during Very Poor/Severe spells.',
    maternalProtocolTitle: 'Maternal Health & Foetal Protection',
    maternalProtocolAdvice:
      'Ultrafine PM2.5 particulates can cross the placental barrier. Minimize exposure during peak commute and inversion hours.',
    maternalProtocolNote:
      'Keep indoor HEPA air filtration running in sleeping quarters. Wear certified N95 when traveling for medical checkups.',
    modularSuiteTitle: 'AirSaathi AI Modular Architecture',
    modularSuiteSubtitle:
      'Production-ready 7-module urban defense platform. Modules initialize sequentially.',
    statusNext: 'Next In Pipeline',
    statusPlanned: 'Planned',
    statusActive: 'Configured',
    viewArchitecture: 'View Architecture',
    footerMission: 'Dedicated to urban health intelligence, winter smog navigation & clean air.',
    footerCompliance: 'National NAQI & WHO Compliant',
    footerZeroHallucination: 'Strict Zero Hallucination Protocol',
    footerStack: 'FastAPI + Vite React + Cloud Run Architecture',
    loadingTitle: 'Calibrating Air Quality Intelligence...',
    loadingSubtitle: 'Synchronizing micro-meteorological telemetry and particulate sub-indices',
    errorTitle: 'Unable to Retrieve Sensor Feed',
    retryBtn: 'Retry Connection',
    refreshBtn: 'Refresh',
    familyPillLabel: 'Family Profile:',
    activeCount: 'Active',
  },
  hi: {
    appName: 'एयरसाथी AI',
    appSubtitle: 'शहरी वायु गुणवत्ता व स्मॉग इंटेलिजेंस',
    demoMode: 'डेमो मोड',
    demoModeLong: 'प्रदर्शन डेटा मोड (Demonstration Mode)',
    demoBaseline: 'सिम्युलेटेड CPCB बेंचमार्क',
    demoNotice:
      'यह डैशबोर्ड वर्तमान में प्रामाणिक शीतकालीन स्मॉग पैटर्न पर आधारित डेमो डेटा प्रदर्शित कर रहा है। आगामी मॉड्यूल में लाइव CPCB/OpenAQ और जेमिनी AI पाइपलाइन सक्रिय होंगी।',
    showDetails: 'डेटा स्रोत व विवरण',
    hideDetails: 'कम विवरण',
    benchmarkSource: 'प्राथमिक संदर्भ स्रोत',
    simulatedTime: 'सिम्युलेटेड समय-मोहर',
    integrityStandard: 'डेटा सत्यनिष्ठा मानक',
    zeroHallucinationPolicy: 'शून्य सिंथेटिक भ्रम नीति (सत्यापित डेटा)',
    lastUpdated: 'अंतिम अपडेट:',
    prominentPollutant: 'प्रमुख प्रदूषक:',
    hotspot: 'स्मॉग हॉटस्पॉट',
    dispersionConditions: 'मौसम व वायुमंडलीय फैलाव',
    temperature: 'तापमान',
    humidity: 'आर्द्रता',
    wind: 'हवा की गति',
    visibility: 'दृश्यता',
    boundaryLayer: 'इनवर्जन ऊंचाई (मिश्रण परत)',
    trappingPollutants: '(प्रदूषक सतह पर फंसे हुए)',
    naqiScale: 'राष्ट्रीय वायु गुणवत्ता सूचकांक पैमाना (NAQI)',
    currentValue: 'वर्तमान मान:',
    scale0500: 'पैमाना 0-500',
    pollutantBreakdownTitle: 'प्रदूषक संघटन व सुरक्षित सीमाएं',
    pollutantBreakdownSubtitle:
      'केंद्रीय प्रदूषण नियंत्रण बोर्ड (CPCB) एवं विश्व स्वास्थ्य संगठन (WHO) मानकों से तुलना',
    cpcbLimit: 'CPCB मानक',
    whoBenchmark: 'WHO सुरक्षित सीमा',
    nationalStandard: 'राष्ट्रीय मानक (CPCB):',
    whoGuideline: 'WHO दिशा-निर्देश:',
    withinLimit: '(सुरक्षित सीमा में)',
    aboveLimit: 'गुना अधिक',
    subIndex: 'उप-सूचकांक:',
    maxScale: 'अधिकतम: 500',
    diurnalTitle: '24-घंटे का वायु गुणवत्ता पूर्वानुमान व दैनिक चक्र',
    diurnalSubtitle:
      'तापीय व्युत्क्रमण (Inversion) एवं वायुमंडलीय फैलाव के आधार पर 24 घंटे की प्रवृत्ति',
    peakDangerWindow: 'स्मॉग इनवर्जन पीक (अत्यधिक जोखिम)',
    safestOutdoorWindow: 'सबसे सुरक्षित आउटडोर समय',
    inversionFootnote:
      'सर्दियों में रात का तापीय व्युत्क्रमण आमतौर पर सुबह 11:30 बजे के बाद ही छंटता है।',
    diurnalSource:
      'स्रोत: उत्तर भारत शीतकालीन CAAQMS मॉडल पर आधारित दैनिक चक्र',
    moderateLimit: 'मध्यम सीमा (200)',
    poorLimit: 'खराब सीमा (300)',
    severeLimit: 'गंभीर दहलीज (400)',
    healthAdvisoryTitle: 'स्वास्थ्य सलाह एवं सुरक्षा निर्देश',
    healthAdvisorySubtitle: 'वर्तमान वायु गुणवत्ता के आधार पर व्यक्तिगत एवं पारिवारिक सुरक्षा उपाय',
    maskRecommendation: 'मास्क अनुशंसा',
    maskNote: 'कपड़े या सर्जिकल मास्क PM2.5 एरोसोल को नहीं रोक पाते।',
    purifierRecommendation: 'एयर प्यूरीफायर मोड',
    purifierNote: 'कमरे में CADR ≥ 2.5 वायु विनिमय प्रति घंटा (ACH) बनाए रखें।',
    outdoorExercise: 'आउटडोर व्यायाम व सैर',
    outdoorNote: 'गहरी सांस लेने से फेफड़ों में सूक्ष्म कणों का जमाव 4 गुना बढ़ जाता है।',
    ventilationWindow: 'सुरक्षित खिड़की वेंटिलेशन समय',
    ventilationNote: 'स्मॉग के मौसम में सुबह 11:30 से पहले या सूर्यास्त के बाद खिड़कियां न खोलें।',
    familyGuardTitle: 'परिवार संवेदनशील समूह सुरक्षा',
    familyGuardSubtitle:
      'अपने परिवार के सदस्यों के अनुसार व्यक्तिगत जोखिम चेतावनी अनुकूलित करें',
    childrenToggle: 'बच्चे (Children)',
    seniorsToggle: 'वरिष्ठ नागरिक (60+)',
    asthmaToggle: 'अस्थमा / हृदय रोगी',
    maternalToggle: 'गर्भवती महिलाएं',
    childrenProtocolTitle: 'शिशु एवं बाल सुरक्षा प्रोटोकॉल',
    childrenProtocolNote:
      'विकासशील फेफड़े वयस्कों की तुलना में प्रति किग्रा वजन 50% अधिक हवा अंदर खींचते हैं। स्कूल बस की खिड़कियां बंद रखें।',
    seniorsProtocolTitle: 'वरिष्ठ नागरिक (60+) कार्डियोरेस्पिरेटरी सुरक्षा',
    seniorsProtocolNote:
      'अत्यधिक PM2.5 से रक्त वाहिकाओं में संकुचन और उच्च रक्तचाप होता है। सुबह की पार्क की सैर को दोपहर 2:00 बजे घर के अंदर बदलें।',
    asthmaProtocolTitle: 'अस्थमा / सीओपीडी / हृदय रोगी चेतावनी',
    asthmaProtocolNote:
      'इन्हेलर और स्पेसर हमेशा पास रखें। बहुत खराब/गंभीर वायु में दिन में दो बार पीक फ्लो मीटर की जांच करें।',
    maternalProtocolTitle: 'मातृ स्वास्थ्य एवं भ्रूण सुरक्षा',
    maternalProtocolAdvice:
      'अतिसूक्ष्म PM2.5 कण प्लेसेंटल बैरियर को पार कर सकते हैं। व्यस्त समय और सुबह के स्मॉग में बाहर निकलने से बचें।',
    maternalProtocolNote:
      'सोने के कमरे में HEPA एयर प्यूरीफायर चलाएं। मेडिकल चेकअप के लिए जाते समय प्रमाणित N95 मास्क पहनें।',
    modularSuiteTitle: 'एयरसाथी AI मॉड्यूलर सुइट',
    modularSuiteSubtitle:
      'उत्पादन-तैयार 7-मॉड्यूल संरचना - अगला कदम: AI रूटीन प्लानर एवं इनडोर वायु सहायक',
    statusNext: 'अगला चरण',
    statusPlanned: 'नियोजित',
    statusActive: 'सक्रिय',
    viewArchitecture: 'संरचना देखें',
    footerMission: 'स्वच्छ वायु, शीतकालीन स्मॉग से बचाव और स्वस्थ परिवार के लिए समर्पित।',
    footerCompliance: 'राष्ट्रीय NAQI एवं WHO मानकों के अनुरूप',
    footerZeroHallucination: 'शून्य सिंथेटिक भ्रम नीति (सत्यापित डेटा)',
    footerStack: 'FastAPI + Vite React + Cloud Run संरचना',
    loadingTitle: 'वायु गुणवत्ता डेटा लोड हो रहा है...',
    loadingSubtitle: 'CPCB मॉनिटरिंग स्टेशन टेलीमेट्री व मौसम डेटा एकत्र किया जा रहा है',
    errorTitle: 'सेंसर फीड लोड करने में असमर्थ',
    retryBtn: 'पुनः प्रयास करें',
    refreshBtn: 'रिफ्रेश',
    familyPillLabel: 'परिवार सुरक्षा:',
    activeCount: 'सक्रिय',
  },
};

export const pollutantDescriptions: Record<string, { en: string; hi: string }> = {
  'PM2.5': {
    en: 'Fine Respirable Dust (< 2.5 µm)',
    hi: 'अति-बारीक श्वसनीय कण (< 2.5 µm)',
  },
  'PM10': {
    en: 'Inhalable Particulate Matter (< 10 µm)',
    hi: 'सांस लेने योग्य धूल कण (< 10 µm)',
  },
  'NO2': {
    en: 'Nitrogen Dioxide (Vehicular/Combustion)',
    hi: 'नाइट्रोजन डाइऑक्साइड (वाहनों का धुआं)',
  },
  'SO2': {
    en: 'Sulphur Dioxide (Industrial/Thermal)',
    hi: 'सल्फर डाइऑक्साइड (औद्योगिक उत्सर्जन)',
  },
  'CO': {
    en: 'Carbon Monoxide (Incomplete burning)',
    hi: 'कार्बन मोनोऑक्साइड (अपूर्ण दहन)',
  },
  'O3': {
    en: 'Ozone (Photochemical Smog)',
    hi: 'ओजोन (फोटोकेमिकल स्मॉग)',
  },
};
