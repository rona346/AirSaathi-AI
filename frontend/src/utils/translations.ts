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
  rainfall: string;
  weatherSource: string;
  weatherObserved: string;
  weatherLive: string;
  weatherDemo: string;
  signIn: string;
  signOut: string;
  guestModeLabel: string;
  cloudSynced: string;
  cloudSaving: string;
  cloudError: string;
  accountLabel: string;
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
  // Module 2 Planner Translations
  plannerTabTitle: string;
  dashboardTabTitle: string;
  plannerHeaderSubtitle: string;
  aiEngineBadge: string;
  ruleEngineBadge: string;
  timeOfDayMorning: string;
  timeOfDayAfternoon: string;
  timeOfDayEvening: string;
  keyActivitiesTitle: string;
  schoolCommuteTitle: string;
  officeCommuteTitle: string;
  exerciseTitle: string;
  choresTitle: string;
  indoorAlternative: string;
  scientificRationale: string;
  actionPrecautions: string;
  familyPrecautionsTitle: string;
  disclaimerTitle: string;
  exercisePrefLabel: string;
  exerciseWalk: string;
  exerciseRun: string;
  exerciseGym: string;
  exerciseYoga: string;
  exerciseCycling: string;
  regeneratePlanBtn: string;
  regenerating: string;
  // Module 3 Indoor Assistant Translations
  indoorTabTitle: string;
  indoorSubtitle: string;
  qualitativeRiskBadge: string;
  riskScoreLabel: string;
  sensorNoticeTitle: string;
  householdConfigTitle: string;
  roomTypeLabel: string;
  roomBedroom: string;
  roomKitchen: string;
  roomLiving: string;
  roomChildren: string;
  roomStudy: string;
  roomAreaLabel: string;
  heavyFryingLabel: string;
  chimneyLabel: string;
  exhaustLabel: string;
  incenseLabel: string;
  smokingLabel: string;
  petsLabel: string;
  cleaningMethodLabel: string;
  wetMoppingOption: string;
  dryBroomOption: string;
  purifierPresentLabel: string;
  hepaCertifiedLabel: string;
  purifierGuidanceTitle: string;
  recommendedCadrLabel: string;
  targetAchLabel: string;
  ventilationStrategyTitle: string;
  kitchenManagementTitle: string;
  roomSpecificTitle: string;
  plantMythTitle: string;
  actionChecklistTitle: string;
  recalculateBtn: string;
  calculating: string;
  // Module 4 Chatbot Translations
  chatTabTitle: string;
  chatSubtitle: string;
  chatPlaceholder: string;
  chatSendBtn: string;
  chatSending: string;
  chatClearTitle: string;
  chatDisclaimerNote: string;
  chatStarterTitle: string;
  chatStarter1: string;
  chatStarter2: string;
  chatStarter3: string;
  chatStarter4: string;
  chatContextBadge: string;
  chatAiBadge: string;
  chatRulesBadge: string;
  chatEmptyState: string;
  // Module 5 Mobility Assistant Translations
  mobilityTabTitle: string;
  mobilitySubtitle: string;
  commutePlannerTitle: string;
  distanceKmLabel: string;
  currentModeLabel: string;
  commutePurposeLabel: string;
  commuteFrequencyLabel: string;
  accessibilityLabel: string;
  vehicleOccupancyLabel: string;
  calculateMobilityBtn: string;
  calculatingMobility: string;
  recommendedModeTitle: string;
  activeMobilityAlertTitle: string;
  modeComparisonTitle: string;
  carpoolWidgetTitle: string;
  carpoolWidgetSubtitle: string;
  soloBaselineLabel: string;
  shared3PersonLabel: string;
  dailyAvoidedLabel: string;
  annualAvoidedLabel: string;
  co2eSavingsLabel: string;
  perPassengerEmissionsLabel: string;
  methodologyNotesTitle: string;
  mobilityDisclaimerTitle: string;
  // Module 6 Impact Tracker Translations
  impactTabTitle: string;
  impactHeaderSubtitle: string;
  impactTimeframeDay: string;
  impactTimeframeWeek: string;
  impactTimeframeMonth: string;
  impactTimeframeAll: string;
  impactTotalDistance: string;
  impactModeledEmissions: string;
  impactAvoidedEmissions: string;
  impactTreeMonths: string;
  impactTreeDisclaimer: string;
  impactDailyTrendTitle: string;
  impactDailyTrendSubtitle: string;
  impactModalSplitTitle: string;
  impactModalSplitSubtitle: string;
  impactSuggestionsTitle: string;
  impactSuggestionsSubtitle: string;
  impactLogActivityBtn: string;
  impactMethodologyBtn: string;
  impactHistoryTitle: string;
  impactHistorySubtitle: string;
  impactNoActivities: string;
  impactDeleteConfirmTitle: string;
  impactDeleteConfirmDesc: string;
  impactAddModalTitle: string;
  impactAddModalSubtitle: string;
  impactActivityTypeLabel: string;
  impactTransportModeLabel: string;
  impactDistanceLabel: string;
  impactPassengersLabel: string;
  impactDateLabel: string;
  impactNotesLabel: string;
  impactExposureMitigationLabel: string;
  impactIndoorIntegrityNote: string;
  impactPreviewEmissions: string;
  impactPreviewSavings: string;
  impactSaveActivityBtn: string;
  impactSaving: string;
  impactDeleteBtn: string;
  impactDeleting: string;
  impactCancelBtn: string;
  impactMethodologyTitle: string;
  impactMethodologySubtitle: string;
  // Module 7 Family Profile & Personalization Translations
  familyTabTitle: string;
  familyHeaderSubtitle: string;
  householdSectionTitle: string;
  householdSizeLabel: string;
  householdSizeDesc: string;
  demographicsTitle: string;
  demographicsDesc: string;
  hasInfantsLabel: string;
  hasChildrenLabel: string;
  hasTeensLabel: string;
  hasAdultsLabel: string;
  hasSeniorsLabel: string;
  preferencesSectionTitle: string;
  alertThresholdTitle: string;
  alertThresholdDesc: string;
  thresholdSensitive: string;
  thresholdStandard: string;
  thresholdHighTolerance: string;
  preferredTransitTitle: string;
  equipmentTitle: string;
  equipmentDesc: string;
  hasHepaLabel: string;
  hasKitchenExhaustLabel: string;
  hasIndoorMonitorLabel: string;
  activityWindowsTitle: string;
  morningWindowLabel: string;
  schoolCommuteLabel: string;
  officeCommuteLabel: string;
  eveningWindowLabel: string;
  advisorySectionTitle: string;
  advisorySectionDesc: string;
  telemetryActive: string;
  telemetryDemo: string;
  telemetryUnavailable: string;
  activeSafeguardsTitle: string;
  priorityUrgent: string;
  priorityCaution: string;
  priorityAdvisory: string;
  priorityGood: string;
  scientificRationaleLabel: string;
  targetGroupLabel: string;
  disclaimerLabel: string;
  savePreferencesBtn: string;
  preferencesSaved: string;
  preferencesGuestNotice: string;
  grapTitle: string;
  grapIndicativeTag: string;
  grapCurbsActive: string;
  grapNonNcrNotice: string;
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
    rainfall: 'Rain / Precipitation',
    weatherSource: 'Weather Telemetry',
    weatherObserved: 'Observed:',
    weatherLive: 'Live Open-Meteo',
    weatherDemo: 'Simulated Weather',
    signIn: 'Sign In',
    signOut: 'Sign Out',
    guestModeLabel: 'Guest Mode',
    cloudSynced: 'Cloud Synced',
    cloudSaving: 'Syncing...',
    cloudError: 'Sync Offline',
    accountLabel: 'Account',
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
    plannerTabTitle: 'AI Daily Routine Planner',
    dashboardTabTitle: 'Air Quality Dashboard',
    plannerHeaderSubtitle:
      'Personalized smog-adjusted schedule for school, commute, workouts, and household tasks powered by atmospheric modeling and Gemini AI',
    aiEngineBadge: 'Google Gemini 2.5 Flash',
    ruleEngineBadge: 'CPCB Expert Rule Engine',
    timeOfDayMorning: 'Morning Schedule (06:00 - 12:00)',
    timeOfDayAfternoon: 'Afternoon Schedule (12:00 - 17:00)',
    timeOfDayEvening: 'Evening & Night Schedule (17:00 - 22:00+)',
    keyActivitiesTitle: 'Personalized Daily Action Plans',
    schoolCommuteTitle: 'School Commute & Recess',
    officeCommuteTitle: 'Office Commute & Transit',
    exerciseTitle: 'Exercise & Workout Routine',
    choresTitle: 'Outdoor Chores & Errands',
    indoorAlternative: 'Indoor Safe Alternative',
    scientificRationale: 'Atmospheric & Physiological Rationale',
    actionPrecautions: 'Key Safety Precautions',
    familyPrecautionsTitle: 'Family Vulnerability Safeguards',
    disclaimerTitle: 'Medical & Environmental Disclaimer',
    exercisePrefLabel: 'Workout Preference:',
    exerciseWalk: 'Brisk Walk',
    exerciseRun: 'Running',
    exerciseGym: 'Gym Workout',
    exerciseYoga: 'Yoga & Pranayama',
    exerciseCycling: 'Cycling',
    regeneratePlanBtn: 'Regenerate Plan',
    regenerating: 'Synthesizing Plan...',
    indoorTabTitle: 'Indoor Air Quality Assistant',
    indoorSubtitle:
      'Personalized qualitative indoor risk evaluation, smart ventilation, CADR purifier calculator, and kitchen pollution management',
    qualitativeRiskBadge: 'Qualitative Hazard Level',
    riskScoreLabel: 'Indoor Risk Index',
    sensorNoticeTitle: 'Sensor Disclosure & Zero Hallucination Protocol',
    householdConfigTitle: 'Household Habits & Room Configuration',
    roomTypeLabel: 'Room Type:',
    roomBedroom: 'Bedroom',
    roomKitchen: 'Kitchen',
    roomLiving: 'Living Room',
    roomChildren: "Children's Room",
    roomStudy: 'Study / Office',
    roomAreaLabel: 'Room Area:',
    heavyFryingLabel: 'Tadka / Deep Frying:',
    chimneyLabel: 'Kitchen Chimney:',
    exhaustLabel: 'Exhaust Fan:',
    incenseLabel: 'Incense / Agarbatti / Coil:',
    smokingLabel: 'Indoor Smoking:',
    petsLabel: 'Pets Present:',
    cleaningMethodLabel: 'Cleaning Technique:',
    wetMoppingOption: 'Damp Microfiber Mopping',
    dryBroomOption: 'Dry Broom Sweeping',
    purifierPresentLabel: 'Air Purifier Present:',
    hepaCertifiedLabel: 'True HEPA (H13) Filter:',
    purifierGuidanceTitle: 'HEPA Air Purifier Sizing & CADR Calculator',
    recommendedCadrLabel: 'Target CADR Output:',
    targetAchLabel: 'Target Air Changes / Hour (ACH):',
    ventilationStrategyTitle: 'Smart Window Aeration Strategy',
    kitchenManagementTitle: 'Kitchen Smog & Gas Safety Protocol',
    roomSpecificTitle: 'Room-Wise Targeted Safeguards',
    plantMythTitle: 'Scientific Fact Check: Indoor Plants vs Mechanical Filtration',
    actionChecklistTitle: 'Actionable Clean Air Checklist',
    recalculateBtn: 'Recalculate Assessment',
    calculating: 'Analyzing Indoor Hazards...',
    // Module 4 Chatbot Translations
    chatTabTitle: 'Environmental Chatbot',
    chatSubtitle: 'Gemini-Powered Smog & Air Quality Assistant',
    chatPlaceholder: 'Ask about smog protection, AQI, masks, purifiers, or daily habits...',
    chatSendBtn: 'Send',
    chatSending: 'AirSaathi is thinking...',
    chatClearTitle: 'Clear Conversation',
    chatDisclaimerNote:
      'Medical Disclaimer: AirSaathi AI provides environmental mitigation insights, not medical advice or prescriptions. Consult a doctor for health emergencies.',
    chatStarterTitle: 'Suggested Questions to Ask',
    chatStarter1: 'What is the difference between PM2.5 and PM10?',
    chatStarter2: 'How should I protect children during peak morning smog?',
    chatStarter3: 'Is running or morning walking safe in current AQI?',
    chatStarter4: 'Can indoor snake plants replace a HEPA air purifier?',
    chatContextBadge: 'CPCB Context Active',
    chatAiBadge: 'Google Gemini 2.5 Flash',
    chatRulesBadge: 'Expert Rules Fallback',
    chatEmptyState: 'Ask AirSaathi anything about smog, AQI, masks, indoor air, or family precautions.',
    // Module 5 Mobility Assistant Translations
    mobilityTabTitle: 'Sustainable Mobility',
    mobilitySubtitle: 'AQI-Aware Commute Planning & Urban Transport Emission Benchmark',
    commutePlannerTitle: 'Sustainable Commute Configuration',
    distanceKmLabel: 'One-Way Distance (km):',
    currentModeLabel: 'Current Commute Mode:',
    commutePurposeLabel: 'Travel Purpose:',
    commuteFrequencyLabel: 'Commute Frequency:',
    accessibilityLabel: 'Accessibility Needs:',
    vehicleOccupancyLabel: 'Vehicle Occupancy:',
    calculateMobilityBtn: 'Calculate Mobility Strategy',
    calculatingMobility: 'Optimizing Commute & Computing Emissions...',
    recommendedModeTitle: 'Recommended Sustainable Transport Option',
    activeMobilityAlertTitle: 'Active Mobility & Inversion Smog Advisory',
    modeComparisonTitle: 'Transport Mode Carbon Emission Comparison',
    carpoolWidgetTitle: 'Carpooling Emission Reductions',
    carpoolWidgetSubtitle: 'Estimated savings from shared occupancy vs solo car driving',
    soloBaselineLabel: 'Solo Driver Baseline:',
    shared3PersonLabel: '3-Person Shared Pool:',
    dailyAvoidedLabel: 'Daily CO2e Avoided:',
    annualAvoidedLabel: 'Annual CO2e Avoided (250 work days):',
    co2eSavingsLabel: 'CO2e Savings:',
    perPassengerEmissionsLabel: 'Per-Passenger Emissions:',
    methodologyNotesTitle: 'Scientific Methodology & Emission Assumptions',
    mobilityDisclaimerTitle: 'Environmental & Health Advisory Disclaimer',
    // Module 6 Impact Tracker Translations
    impactTabTitle: 'Impact Tracker',
    impactHeaderSubtitle: 'Personal Carbon Footprint, Avoided Emissions & Sustainability Milestones',
    impactTimeframeDay: 'Today',
    impactTimeframeWeek: 'Past 7 Days',
    impactTimeframeMonth: 'Past 30 Days',
    impactTimeframeAll: 'All Time',
    impactTotalDistance: 'Clean Distance Logged',
    impactModeledEmissions: 'Modeled Emissions',
    impactAvoidedEmissions: 'Avoided CO2e (Savings)',
    impactTreeMonths: 'Tree-Months Equivalent',
    impactTreeDisclaimer: 'Educational equivalency: 1 mature tree absorbs ~1.75 kg CO2/mo (US EPA). Not a carbon offset credit.',
    impactDailyTrendTitle: 'Daily Impact & Emissions Trend',
    impactDailyTrendSubtitle: 'Modeled commute emissions versus avoided baseline emissions over time',
    impactModalSplitTitle: 'Modal Split & Travel Distribution',
    impactModalSplitSubtitle: 'Commute distance and emission breakdown across transport modes',
    impactSuggestionsTitle: 'Personalized Sustainability Actions',
    impactSuggestionsSubtitle: 'Actionable suggestions based on your commute history to maximize CO2 savings',
    impactLogActivityBtn: 'Log Activity',
    impactMethodologyBtn: 'Scientific Methodology',
    impactHistoryTitle: 'Environmental Action History',
    impactHistorySubtitle: 'Transparent log of commutes, carpools, and indoor air mitigation actions',
    impactNoActivities: 'No environmental activities recorded in this timeframe. Log your daily commute or lifestyle actions to begin tracking!',
    impactDeleteConfirmTitle: 'Confirm Activity Deletion',
    impactDeleteConfirmDesc: 'Are you sure you want to remove this logged activity? This action cannot be undone.',
    impactAddModalTitle: 'Log Environmental Activity',
    impactAddModalSubtitle: 'Record a sustainable commute, carpool, or indoor air safeguard',
    impactActivityTypeLabel: 'Activity Category',
    impactTransportModeLabel: 'Transport Mode',
    impactDistanceLabel: 'Trip Distance (km)',
    impactPassengersLabel: 'Occupancy / Passengers',
    impactDateLabel: 'Activity Date',
    impactNotesLabel: 'Trip Notes / Purpose (Optional)',
    impactExposureMitigationLabel: 'Exposure Mitigation Score (0-100)',
    impactIndoorIntegrityNote: 'Indoor safeguards (purifier/ventilation) mitigate respiratory PM2.5/PM10 lung intake; they do not claim vehicular CO2 reductions.',
    impactPreviewEmissions: 'Est. Emissions:',
    impactPreviewSavings: 'Est. CO2e Avoided:',
    impactSaveActivityBtn: 'Record Activity',
    impactSaving: 'Saving...',
    impactDeleteBtn: 'Delete',
    impactDeleting: 'Deleting...',
    impactCancelBtn: 'Cancel',
    impactMethodologyTitle: 'Calculation Methodology & Standards',
    impactMethodologySubtitle: 'Verified scientific benchmarks, grid factors, and transparent accounting rules',
    // Module 7 Family Profile & Personalization
    familyTabTitle: 'Family Profile & Personalization',
    familyHeaderSubtitle: 'Science-grounded exposure reduction tailored to your household members, alert sensitivity, and clean-air equipment.',
    householdSectionTitle: 'Household Structure & Demographics',
    householdSizeLabel: 'Household Size',
    householdSizeDesc: 'Number of individuals living in this home',
    demographicsTitle: 'Age Group Vulnerabilities',
    demographicsDesc: 'Select broad age categories present in your household to activate tailored exposure mitigation.',
    hasInfantsLabel: 'Infants (0–2 yrs)',
    hasChildrenLabel: 'Children (3–11 yrs)',
    hasTeensLabel: 'Teens (12–17 yrs)',
    hasAdultsLabel: 'Adults (18–59 yrs)',
    hasSeniorsLabel: 'Seniors (60+ yrs)',
    preferencesSectionTitle: 'Sensitivity & Environmental Preferences',
    alertThresholdTitle: 'AQI Alert Sensitivity Threshold',
    alertThresholdDesc: 'Threshold when elevated precautionary alerts and protective protocols are initiated.',
    thresholdSensitive: 'Sensitive (AQI > 100)',
    thresholdStandard: 'Standard (AQI > 200)',
    thresholdHighTolerance: 'High Tolerance (AQI > 300)',
    preferredTransitTitle: 'Preferred Transit Mode',
    equipmentTitle: 'Clean-Air Equipment Assets',
    equipmentDesc: 'Tell AirSaathi what equipment is installed in your home to receive realistic operation instructions.',
    hasHepaLabel: 'True HEPA Air Purifier',
    hasKitchenExhaustLabel: 'Kitchen Chimney / Exhaust Fan',
    hasIndoorMonitorLabel: 'Indoor Air Quality Monitor',
    activityWindowsTitle: 'Daily Exposure Windows',
    morningWindowLabel: 'Morning Outdoor Routine',
    schoolCommuteLabel: 'Daily School Commute',
    officeCommuteLabel: 'Daily Office Commute',
    eveningWindowLabel: 'Evening Outdoor Routine',
    advisorySectionTitle: 'Personalized Smog Advisory & Exposure Shield',
    advisorySectionDesc: 'Real-time, rule-governed atmospheric mitigation actions tailored to current local air quality.',
    telemetryActive: 'Live Telemetry Active',
    telemetryDemo: 'Demonstration Benchmark',
    telemetryUnavailable: 'Station Telemetry Unavailable',
    activeSafeguardsTitle: 'Active Household Safeguards',
    priorityUrgent: 'Urgent Action',
    priorityCaution: 'Caution Advised',
    priorityAdvisory: 'Advisory Guidance',
    priorityGood: 'Optimal Conditions',
    scientificRationaleLabel: 'Scientific Rationale',
    targetGroupLabel: 'Target Group',
    disclaimerLabel: 'Non-Medical Advisory Disclaimer',
    savePreferencesBtn: 'Save Family Preferences',
    preferencesSaved: 'Preferences Synced to Cloud',
    preferencesGuestNotice: 'In guest mode, preferences are retained in local session memory.',
    grapTitle: 'CAQM Graded Response Action Plan (GRAP)',
    grapIndicativeTag: 'Indicative AQI-Based (Delhi-NCR)',
    grapCurbsActive: 'Key Mitigation Measures & Curbs:',
    grapNonNcrNotice:
      'CAQM GRAP framework is statutory only for the National Capital Region (Delhi-NCR). Standard CPCB NAQI protocols apply.',
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
    rainfall: 'वर्षा / बारिश',
    weatherSource: 'मौसम टेलीमेट्री',
    weatherObserved: 'मौसम समय:',
    weatherLive: 'लाइव ओपन-मेटियो',
    weatherDemo: 'सिम्युलेटेड मौसम',
    signIn: 'साइन इन करें',
    signOut: 'साइन आउट',
    guestModeLabel: 'अतिथि मोड',
    cloudSynced: 'क्लाउड सिंक',
    cloudSaving: 'सिंक हो रहा है...',
    cloudError: 'ऑफ़लाइन',
    accountLabel: 'खाता',
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
    plannerTabTitle: 'AI दैनिक दिनचर्या नियोजक',
    dashboardTabTitle: 'वायु गुणवत्ता डैशबोर्ड',
    plannerHeaderSubtitle:
      'स्कूल, ऑफिस, कसरत और घरेलू कार्यों के लिए प्रदूषण-अनुकूलित व्यक्तिगत दैनिक समय-सारणी (जेमिनी AI व वायुमंडलीय मॉडल द्वारा संचालित)',
    aiEngineBadge: 'गूगल जेमिनी 2.5 फ्लैश',
    ruleEngineBadge: 'CPCB विशेषज्ञ नियम इंजन',
    timeOfDayMorning: 'प्रातःकालीन समय-सारणी (06:00 - 12:00)',
    timeOfDayAfternoon: 'दोपहर समय-सारणी (12:00 - 17:00)',
    timeOfDayEvening: 'सायंकाल व रात्रि समय-सारणी (17:00 - 22:00+)',
    keyActivitiesTitle: 'व्यक्तिगत दैनिक कार्य योजनाएं',
    schoolCommuteTitle: 'स्कूल का सफर व कक्षा तैयारी',
    officeCommuteTitle: 'दफ्तर आवागमन योजना',
    exerciseTitle: 'कसरत व व्यायाम समय-सारणी',
    choresTitle: 'घरेलू कार्य व खरीदारी',
    indoorAlternative: 'इनडोर सुरक्षित विकल्प',
    scientificRationale: 'वैज्ञानिक व वातावरणीय कारण',
    actionPrecautions: 'आवश्यक सुरक्षा सावधानियां',
    familyPrecautionsTitle: 'पारिवारिक स्वास्थ्य सुरक्षा अलर्ट',
    disclaimerTitle: 'चिकित्सीय व पर्यावरणीय अस्वीकरण',
    exercisePrefLabel: 'व्यायाम प्राथमिकता:',
    exerciseWalk: 'हल्की सैर / वॉक',
    exerciseRun: 'दौड़ (रनिंग)',
    exerciseGym: 'जिम वर्कआउट',
    exerciseYoga: 'योग व प्राणायाम',
    exerciseCycling: 'साइकिलिंग',
    regeneratePlanBtn: 'योजना अपडेट करें',
    regenerating: 'AI योजना तैयार हो रही है...',
    indoorTabTitle: 'इनडोर वायु गुणवत्ता सहायक',
    indoorSubtitle:
      'घरेलू प्रदूषण जोखिम का गुणात्मक मूल्यांकन, स्मार्ट खिड़की वेंटिलेशन, HEPA प्यूरीफायर CADR कैलकुलेटर व रसोई सुरक्षा',
    qualitativeRiskBadge: 'गुणात्मक जोखिम स्तर',
    riskScoreLabel: 'इनडोर जोखिम सूचकांक',
    sensorNoticeTitle: 'सेंसर प्रकटीकरण एवं शून्य सिंथेटिक भ्रम नीति',
    householdConfigTitle: 'घरेलू आदतें व कमरे का विन्यास',
    roomTypeLabel: 'कमरे का प्रकार:',
    roomBedroom: 'शयनकक्ष (Bedroom)',
    roomKitchen: 'रसोईघर (Kitchen)',
    roomLiving: 'लिविंग रूम (Living)',
    roomChildren: 'बच्चों का कमरा (Children)',
    roomStudy: 'अध्ययन कक्ष (Study/Office)',
    roomAreaLabel: 'कमरे का क्षेत्रफल:',
    heavyFryingLabel: 'तड़का व डीप फ्राइंग:',
    chimneyLabel: 'रसोई चिमनी:',
    exhaustLabel: 'एग्जॉस्ट पंखा:',
    incenseLabel: 'अगरबत्ती / धूप / क्वाइल:',
    smokingLabel: 'इनडोर धूम्रपान:',
    petsLabel: 'पालतू जानवर:',
    cleaningMethodLabel: 'सफाई की तकनीक:',
    wetMoppingOption: 'गीला माइक्रोफाइबर पोछा',
    dryBroomOption: 'सूखा झाड़ू लगाना',
    purifierPresentLabel: 'एयर प्यूरीफायर उपलब्ध:',
    hepaCertifiedLabel: 'सत्य HEPA (H13) फिल्टर:',
    purifierGuidanceTitle: 'HEPA एयर प्यूरीफायर आकार व CADR कैलकुलेटर',
    recommendedCadrLabel: 'लक्षित CADR आउटपुट:',
    targetAchLabel: 'प्रति घंटा वायु चक्र (ACH):',
    ventilationStrategyTitle: 'स्मार्ट खिड़की वेंटिलेशन रणनीति',
    kitchenManagementTitle: 'रसोई स्मॉग व गैस सुरक्षा प्रोटोकॉल',
    roomSpecificTitle: 'कक्ष-वार लक्षित सुरक्षा निर्देश',
    plantMythTitle: 'वैज्ञानिक तथ्य: इनडोर पौधे बनाम प्रमाणित HEPA फिल्टर',
    actionChecklistTitle: 'स्वच्छ वायु कार्य सूची (Checklist)',
    recalculateBtn: 'मूल्यांकन अपडेट करें',
    calculating: 'इनडोर जोखिम विश्लेषण जारी है...',
    // Module 4 Chatbot Translations
    chatTabTitle: 'पर्यावरण चैटबॉट',
    chatSubtitle: 'जेमिनी AI-संचालित वायु गुणवत्ता व स्मॉग सहायक',
    chatPlaceholder: 'स्मॉग सुरक्षा, AQI, मास्क, प्यूरीफायर या आदतों के बारे में पूछें...',
    chatSendBtn: 'भेजें',
    chatSending: 'एयरसाथी विचार कर रहा है...',
    chatClearTitle: 'बातचीत रीसेट करें',
    chatDisclaimerNote:
      'चिकित्सीय अस्वीकरण: एयरसाथी AI केवल पर्यावरणीय जोखिम न्यूनीकरण सुझाव देता है, चिकित्सीय परामर्श या दवा का नुस्खा नहीं। सांस संबंधी आपातकाल में डॉक्टर से मिलें।',
    chatStarterTitle: 'सुझाए गए प्रश्न',
    chatStarter1: 'PM2.5 और PM10 में क्या अंतर है?',
    chatStarter2: 'आज बच्चों को स्मॉग से कैसे बचाएं?',
    chatStarter3: 'क्या वर्तमान एक्यूआई में सुबह दौड़ना सुरक्षित है?',
    chatStarter4: 'क्या घर के पौधे HEPA एयर प्यूरीफायर की जगह ले सकते हैं?',
    chatContextBadge: 'CPCB डेटा संलग्न',
    chatAiBadge: 'गूगल जेमिनी 2.5 फ्लैश',
    chatRulesBadge: 'विशेषज्ञ नियम बैकअप',
    chatEmptyState: 'स्मॉग, मास्क, इनडोर वायु या परिवार की सुरक्षा को लेकर कोई भी प्रश्न पूछें।',
    // Module 5 Mobility Assistant Translations
    mobilityTabTitle: 'सतत गतिशीलता',
    mobilitySubtitle: 'AQI-सचेत आवागमन नियोजक व शहरी परिवहन कार्बन बेंचमार्क',
    commutePlannerTitle: 'सतत आवागमन प्राथमिकताएं',
    distanceKmLabel: 'एक तरफ की यात्रा दूरी (किमी):',
    currentModeLabel: 'वर्तमान आवागमन साधन:',
    commutePurposeLabel: 'यात्रा का उद्देश्य:',
    commuteFrequencyLabel: 'आवागमन आवृत्ति:',
    accessibilityLabel: 'शारीरिक सुगमता आवश्यकताएं:',
    vehicleOccupancyLabel: 'वाहन में यात्रियों की संख्या:',
    calculateMobilityBtn: 'गतिशीलता योजना का विश्लेषण करें',
    calculatingMobility: 'उत्सर्जन व AQI जोखिम का विश्लेषण जारी है...',
    recommendedModeTitle: 'सर्वोत्तम अनुशंसित टिकाऊ परिवहन साधन',
    activeMobilityAlertTitle: 'सक्रिय शारीरिक आवागमन व स्मॉग इनवर्जन चेतावनी',
    modeComparisonTitle: 'विभिन्न परिवहन साधनों के कार्बन उत्सर्जन की तुलना',
    carpoolWidgetTitle: 'कारपूलिंग से उत्सर्जन में बचत',
    carpoolWidgetSubtitle: 'अकेले कार चलाने की तुलना में साझा सफर से अनुमानित बचत',
    soloBaselineLabel: 'अकेले निजी कार का उत्सर्जन:',
    shared3PersonLabel: '3-व्यक्ति साझा कारपूलिंग:',
    dailyAvoidedLabel: 'दैनिक CO2e बचत:',
    annualAvoidedLabel: 'वार्षिक CO2e बचत (250 कार्य दिवस):',
    co2eSavingsLabel: 'कार्बन उत्सर्जन बचत:',
    perPassengerEmissionsLabel: 'प्रति-यात्री उत्सर्जन:',
    methodologyNotesTitle: 'वैज्ञानिक गणना पद्धति व उत्सर्जन मान्यताएं',
    mobilityDisclaimerTitle: 'पर्यावरणीय व स्वास्थ्य परामर्श अस्वीकरण',
    // Module 6 Impact Tracker Translations
    impactTabTitle: 'पर्यावरणीय प्रभाव',
    impactHeaderSubtitle: 'व्यक्तिगत कार्बन फुटप्रिंट, वायु उत्सर्जन बचत और सतत लक्ष्य',
    impactTimeframeDay: 'आज',
    impactTimeframeWeek: 'पिछले 7 दिन',
    impactTimeframeMonth: 'पिछले 30 दिन',
    impactTimeframeAll: 'कुल समय',
    impactTotalDistance: 'दर्ज स्वच्छ दूरी',
    impactModeledEmissions: 'अनुमानित उत्सर्जन',
    impactAvoidedEmissions: 'बचत हुआ CO2e (कार्बन कटौती)',
    impactTreeMonths: 'वृक्ष-माह समतुल्यता',
    impactTreeDisclaimer: 'शैक्षणिक संदर्भ: 1 परिपक्व पेड़ ~1.75 किग्रा CO2/माह अवशोषित करता है (US EPA)। यह प्रत्यक्ष कार्बन क्रेडिट नहीं है।',
    impactDailyTrendTitle: 'दैनिक प्रभाव व उत्सर्जन रुझान',
    impactDailyTrendSubtitle: 'समय के साथ वास्तविक आवागमन उत्सर्जन और बचाए गए बेसलाइन कार्बन की तुलना',
    impactModalSplitTitle: 'परिवहन साधन विभाजन व वितरण',
    impactModalSplitSubtitle: 'विभिन्न परिवहन साधनों में यात्रा की गई दूरी और उत्सर्जन का प्रतिशत',
    impactSuggestionsTitle: 'अनुकूलित सतत कार्य योजनाएं',
    impactSuggestionsSubtitle: 'कार्बन बचत को अधिकतम करने हेतु आपके यात्रा इतिहास पर आधारित व्यावहारिक सुझाव',
    impactLogActivityBtn: 'गतिविधि जोड़ें',
    impactMethodologyBtn: 'वैज्ञानिक कार्यप्रणाली',
    impactHistoryTitle: 'पर्यावरणीय गतिविधि इतिहास',
    impactHistorySubtitle: 'सफर, कारपूलिंग और इनडोर सुरक्षा उपायों का पारदर्शी लेखा-जोखा',
    impactNoActivities: 'इस समय सीमा में कोई गतिविधि दर्ज नहीं है। ट्रैकिंग प्रारंभ करने हेतु अपनी यात्रा या इनडोर उपाय दर्ज करें!',
    impactDeleteConfirmTitle: 'गतिविधि हटाने की पुष्टि करें',
    impactDeleteConfirmDesc: 'क्या आप वाकई इस गतिविधि को हटाना चाहते हैं? यह क्रिया पूर्ववत नहीं की जा सकती।',
    impactAddModalTitle: 'पर्यावरणीय गतिविधि दर्ज करें',
    impactAddModalSubtitle: 'सतत यात्रा, कारपूलिंग या इनडोर वायु सुरक्षा का रिकॉर्ड बनाएं',
    impactActivityTypeLabel: 'गतिविधि श्रेणी',
    impactTransportModeLabel: 'परिवहन साधन',
    impactDistanceLabel: 'सफर की दूरी (किमी)',
    impactPassengersLabel: 'सवारियों की संख्या',
    impactDateLabel: 'गतिविधि दिनांक',
    impactNotesLabel: 'सफर विवरण / उद्देश्य (वैकल्पिक)',
    impactExposureMitigationLabel: 'प्रदूषण बचाव स्कोर (0-100)',
    impactIndoorIntegrityNote: 'इनडोर प्यूरीफायर व वेंटिलेशन उपाय फेफड़ों में जाने वाले PM2.5/PM10 को कम करते हैं; वे ऑटोमोटिव CO2 कटौती का दावा नहीं करते।',
    impactPreviewEmissions: 'अनुमानित उत्सर्जन:',
    impactPreviewSavings: 'अनुमानित बचत:',
    impactSaveActivityBtn: 'गतिविधि सहेजें',
    impactSaving: 'सहेजा जा रहा है...',
    impactDeleteBtn: 'हटाएं',
    impactDeleting: 'हटाया जा रहा है...',
    impactCancelBtn: 'रद्द करें',
    impactMethodologyTitle: 'गणना कार्यप्रणाली व मानक',
    impactMethodologySubtitle: 'सत्यापित वैज्ञानिक मानक, ग्रिड कारक और पारदर्शी उत्सर्जन लेखा नियम',
    // Module 7 Family Profile & Personalization
    familyTabTitle: 'पारिवारिक प्रोफ़ाइल व अनुकूलन',
    familyHeaderSubtitle: 'परिवार के सदस्यों, संवेदनशीलता सीमा और वायु शोधन उपकरणों के आधार पर वैज्ञानिक जोखिम निवारण।',
    householdSectionTitle: 'पारिवारिक संरचना व जनसांख्यिकी',
    householdSizeLabel: 'परिवार में सदस्यों की संख्या',
    householdSizeDesc: 'घर में रहने वाले कुल सदस्यों की संख्या',
    demographicsTitle: 'आयु वर्ग संवेदनशीलता',
    demographicsDesc: 'अनुकूलित सुरक्षा मार्गदर्शन सक्रिय करने के लिए अपने परिवार में उपस्थित आयु वर्ग चुनें।',
    hasInfantsLabel: 'शिशु (0–2 वर्ष)',
    hasChildrenLabel: 'बच्चे (3–11 वर्ष)',
    hasTeensLabel: 'किशोर (12–17 वर्ष)',
    hasAdultsLabel: 'वयस्क (18–59 वर्ष)',
    hasSeniorsLabel: 'वरिष्ठ नागरिक (60+ वर्ष)',
    preferencesSectionTitle: 'संवेदनशीलता सीमा व पर्यावरणीय प्राथमिकताएं',
    alertThresholdTitle: 'AQI अलर्ट संवेदनशीलता सीमा',
    alertThresholdDesc: 'वह वायु गुणवत्ता सीमा जिस पर उन्नत चेतावनी और सुरक्षा प्रोटोकॉल सक्रिय होते हैं।',
    thresholdSensitive: 'अति संवेदनशील (AQI > 100)',
    thresholdStandard: 'मानक (AQI > 200)',
    thresholdHighTolerance: 'उच्च सहनशीलता (AQI > 300)',
    preferredTransitTitle: 'प्राथमिक परिवहन साधन',
    equipmentTitle: 'स्वच्छ वायु उपकरण संपत्ति',
    equipmentDesc: 'अपने घर में मौजूद उपकरणों का चयन करें ताकि सटीक उपयोग मार्गदर्शन मिल सके।',
    hasHepaLabel: 'सच्चा HEPA एयर प्यूरीफायर',
    hasKitchenExhaustLabel: 'रसोई चिमनी / एग्जॉस्ट फैन',
    hasIndoorMonitorLabel: 'इनडोर वायु गुणवत्ता मॉनिटर',
    activityWindowsTitle: 'दैनिक बाहरी जोखिम समय',
    morningWindowLabel: 'सुबह की बाहरी गतिविधि',
    schoolCommuteLabel: 'दैनिक स्कूल यात्रा',
    officeCommuteLabel: 'दैनिक ऑफिस यात्रा',
    eveningWindowLabel: 'शाम की बाहरी गतिविधि',
    advisorySectionTitle: 'व्यक्तिगत स्मॉग सुरक्षा व जोखिम निवारण परामर्श',
    advisorySectionDesc: 'वर्तमान स्थानीय वायु गुणवत्ता और आपकी प्रोफ़ाइल पर आधारित वास्तविक समय सुरक्षा परामर्श।',
    telemetryActive: 'लाइव टेलीमेट्री सक्रिय',
    telemetryDemo: 'प्रदर्शन बेंचमार्क डेटा',
    telemetryUnavailable: 'स्टेशन डेटा अनुपलब्ध',
    activeSafeguardsTitle: 'सक्रिय पारिवारिक सुरक्षा उपाय',
    priorityUrgent: 'तत्काल कार्रवाई',
    priorityCaution: 'सतर्कता आवश्यक',
    priorityAdvisory: 'परामर्श मार्गदर्शन',
    priorityGood: 'अनुकूल स्थिति',
    scientificRationaleLabel: 'वैज्ञानिक आधार',
    targetGroupLabel: 'लक्षित समूह',
    disclaimerLabel: 'गैर-चिकित्सीय परामर्श अस्वीकरण',
    savePreferencesBtn: 'प्राथमिकताएं सहेजें',
    preferencesSaved: 'प्राथमिकताएं क्लाउड पर सहेजी गईं',
    preferencesGuestNotice: 'अतिथि मोड में प्राथमिकताएं केवल वर्तमान सत्र के लिए स्थानीय मेमोरी में सुरक्षित रहेंगी।',
    grapTitle: 'सीएक्यूएम ग्रैप (GRAP) कार्ययोजना',
    grapIndicativeTag: 'वायु गुणवत्ता आधारित सांकेतिक स्थिति (दिल्ली-एनसीआर)',
    grapCurbsActive: 'प्रमुख रोकथाम उपाय एवं प्रतिबंध:',
    grapNonNcrNotice:
      'सीएक्यूएम ग्रैप (GRAP) केवल राष्ट्रीय राजधानी क्षेत्र (दिल्ली-एनसीआर) के लिए वैधानिक है। यहां मानक सीपीसीबी एनएक्यूआई दिशानिर्देश लागू हैं।',
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
