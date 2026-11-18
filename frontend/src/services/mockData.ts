import { CurrentAqiData, ForecastData, StationInfo } from '../types/aqi';
import { ChatResponse } from '../types/chat';
import { MobilityPlanResponse, MobilityRequest, ModeEmissionDetail, TransportMode } from '../types/mobility';
import { getAqiCategory, concentrationFromSubindex, calculateSubindex } from '../utils/aqiUtils';

export const MOCK_STATIONS: StationInfo[] = [
  {
    id: 'delhi-anand-vihar',
    name: 'Anand Vihar',
    city: 'Delhi',
    state: 'Delhi',
    latitude: 28.6508,
    longitude: 77.3152,
    is_hotspot: true,
  },
  {
    id: 'delhi-punjabi-bagh',
    name: 'Punjabi Bagh',
    city: 'Delhi',
    state: 'Delhi',
    latitude: 28.6740,
    longitude: 77.1310,
    is_hotspot: true,
  },
  {
    id: 'delhi-rk-puram',
    name: 'RK Puram',
    city: 'Delhi',
    state: 'Delhi',
    latitude: 28.5660,
    longitude: 77.1767,
    is_hotspot: false,
  },
  {
    id: 'delhi-lodhi-road',
    name: 'Lodhi Road',
    city: 'Delhi',
    state: 'Delhi',
    latitude: 28.5918,
    longitude: 77.2273,
    is_hotspot: false,
  },
  {
    id: 'delhi-igi-airport',
    name: 'IGI Airport (T3)',
    city: 'Delhi',
    state: 'Delhi',
    latitude: 28.5562,
    longitude: 77.1000,
    is_hotspot: false,
  },
  {
    id: 'noida-sector-62',
    name: 'Sector 62',
    city: 'Noida',
    state: 'Uttar Pradesh',
    latitude: 28.6278,
    longitude: 77.3653,
    is_hotspot: true,
  },
  {
    id: 'gurugram-vikas-sadan',
    name: 'Vikas Sadan',
    city: 'Gurugram',
    state: 'Haryana',
    latitude: 28.4595,
    longitude: 77.0266,
    is_hotspot: false,
  },
  {
    id: 'mumbai-bandra-kurla',
    name: 'Bandra Kurla Complex',
    city: 'Mumbai',
    state: 'Maharashtra',
    latitude: 19.0657,
    longitude: 72.8687,
    is_hotspot: false,
  },
  {
    id: 'bengaluru-btm-layout',
    name: 'BTM Layout',
    city: 'Bengaluru',
    state: 'Karnataka',
    latitude: 12.9166,
    longitude: 77.6101,
    is_hotspot: false,
  },
];

export const getMockCurrentAqi = (stationId: string = 'delhi-anand-vihar'): CurrentAqiData => {
  const station = MOCK_STATIONS.find((s) => s.id === stationId) || MOCK_STATIONS[0];
  const aqiMap: Record<string, number> = {
    'delhi-anand-vihar': 368,
    'delhi-punjabi-bagh': 342,
    'delhi-rk-puram': 310,
    'delhi-lodhi-road': 275,
    'delhi-igi-airport': 295,
    'noida-sector-62': 352,
    'gurugram-vikas-sadan': 305,
    'mumbai-bandra-kurla': 164,
    'bengaluru-btm-layout': 88,
  };

  const aqi = aqiMap[station.id] || 320;
  const pm25Conc = concentrationFromSubindex('PM2.5', aqi);
  const pm10Sub = Math.min(500, Math.round(aqi * 0.88));
  const pm10Conc = concentrationFromSubindex('PM10', pm10Sub);
  const no2Sub = Math.min(300, Math.round(50 + aqi * 0.2));
  const no2Conc = concentrationFromSubindex('NO2', no2Sub);
  const so2Sub = Math.min(150, Math.round(20 + aqi * 0.08));
  const so2Conc = concentrationFromSubindex('SO2', so2Sub);
  const coSub = Math.min(200, Math.round(35 + aqi * 0.12));
  const coConc = concentrationFromSubindex('CO', coSub);
  const o3Sub = Math.min(150, Math.round(30 + aqi * 0.1));
  const o3Conc = concentrationFromSubindex('O3', o3Sub);

  return {
    station,
    aqi,
    category: getAqiCategory(aqi),
    prominent_pollutant: 'PM2.5',
    pollutants: {
      'PM2.5': {
        name: 'PM2.5',
        value: pm25Conc,
        unit: 'µg/m³',
        sub_index: calculateSubindex('PM2.5', pm25Conc),
        category: getAqiCategory(calculateSubindex('PM2.5', pm25Conc)),
        standard_limit: 60.0,
        who_limit: 15.0,
      },
      'PM10': {
        name: 'PM10',
        value: pm10Conc,
        unit: 'µg/m³',
        sub_index: calculateSubindex('PM10', pm10Conc),
        category: getAqiCategory(calculateSubindex('PM10', pm10Conc)),
        standard_limit: 100.0,
        who_limit: 45.0,
      },
      'NO2': {
        name: 'NO2',
        value: no2Conc,
        unit: 'µg/m³',
        sub_index: calculateSubindex('NO2', no2Conc),
        category: getAqiCategory(calculateSubindex('NO2', no2Conc)),
        standard_limit: 80.0,
        who_limit: 25.0,
      },
      'SO2': {
        name: 'SO2',
        value: so2Conc,
        unit: 'µg/m³',
        sub_index: calculateSubindex('SO2', so2Conc),
        category: getAqiCategory(calculateSubindex('SO2', so2Conc)),
        standard_limit: 80.0,
        who_limit: 40.0,
      },
      'CO': {
        name: 'CO',
        value: coConc,
        unit: 'mg/m³',
        sub_index: calculateSubindex('CO', coConc),
        category: getAqiCategory(calculateSubindex('CO', coConc)),
        standard_limit: 2.0,
        who_limit: 4.0,
      },
      'O3': {
        name: 'O3',
        value: o3Conc,
        unit: 'µg/m³',
        sub_index: calculateSubindex('O3', o3Conc),
        category: getAqiCategory(calculateSubindex('O3', o3Conc)),
        standard_limit: 100.0,
        who_limit: 100.0,
      },
    },
    health_advisory: {
      general_advice: 'Respiratory illness on prolonged exposure. Severe smog haze with reduced ambient visibility.',
      children_and_seniors: 'Stay indoors. Suspend all outdoor physical education, morning walks, and park play.',
      patients_with_respiratory_issues: 'Strict indoor stay. Keep emergency medication and nebulizer ready.',
      outdoor_activity: 'Strictly avoid all outdoor exercise, cycling, and walks during morning and night hours.',
      mask_recommendation: 'Strict N95/N99 mask requirement with airtight seal for any outdoor transit.',
      purifier_recommendation: 'Run HEPA filtration on medium-high mode. Seal window cracks with weatherstrips.',
      ventilation_window: 'Strictly do not open windows during inversion hours (early morning & late night).',
    },
    weather: {
      temperature_c: 19.5,
      humidity_percent: 74,
      wind_speed_kmh: 4.2,
      wind_direction: 'NW',
      visibility_km: 1.4,
      mixing_layer_height_m: 420,
    },
    data_source: 'Central Pollution Control Board (CPCB) - CAAQMS Mock Baseline',
    last_updated: new Date().toISOString(),
    is_demo_data: true,
  };
};

export const getMockForecast = (stationId: string = 'delhi-anand-vihar'): ForecastData => {
  const station = MOCK_STATIONS.find((s) => s.id === stationId) || MOCK_STATIONS[0];
  const current = getMockCurrentAqi(stationId);
  const baseAqi = current.aqi;
  
  const hourMultipliers = [
    0.98, 0.95, 0.92, 0.90, 0.95, 1.05, 1.18, 1.24, 1.20, 1.10, 0.98, 0.85,
    0.76, 0.72, 0.74, 0.80, 0.88, 0.98, 1.08, 1.15, 1.20, 1.18, 1.10, 1.02,
  ];

  const now = new Date();

  const points = hourMultipliers.map((mult, idx) => {
    const aqiVal = Math.round(baseAqi * mult);
    const date = new Date(now.getTime() + idx * 3600000);
    const hourLabel = date.toLocaleTimeString([], { hour: 'numeric', hour12: true });

    return {
      hour: hourLabel,
      time: date.toISOString(),
      aqi: aqiVal,
      category: getAqiCategory(aqiVal),
      pm25: concentrationFromSubindex('PM2.5', aqiVal),
      pm10: concentrationFromSubindex('PM10', Math.min(500, Math.round(aqiVal * 0.88))),
    };
  });

  return {
    station_id: station.id,
    station_name: station.name,
    forecast_24h: points,
    peak_aqi_window: '06:00 AM - 09:30 AM (Inversion Peak)',
    safest_outdoor_window: '01:30 PM - 04:00 PM (Higher Atmospheric Dispersion)',
    is_demo_data: true,
  };
};

export const getMockRoutinePlan = (
  stationId: string = 'delhi-anand-vihar',
  language: 'en' | 'hi' = 'en'
): any => {
  const station = MOCK_STATIONS.find((s) => s.id === stationId) || MOCK_STATIONS[0];
  const hi = language === 'hi';

  return {
    station_id: station.id,
    station_name: station.name,
    city: station.city,
    aqi: 368,
    category: 'Very Poor',
    prominent_pollutant: 'PM2.5',
    is_demo_data: true,
    data_source: 'Central Pollution Control Board (CPCB) - Offline Fallback Baseline',
    observed_at: new Date().toISOString(),
    language,
    ai_provider: 'expert-rules-fallback',
    ai_generated: false,
    morning: [
      {
        title: hi ? 'सुबह की सैर' : 'Early Morning Walk',
        recommended_time: '06:00 AM - 08:30 AM',
        status: 'Avoid',
        risk_level: 'Critical',
        advice: hi
          ? 'सुबह की सैर पूरी तरह से बंद रखें। घर पर ही योग व हल्का व्यायाम करें।'
          : 'Avoid outdoor morning walks entirely during heavy smog inversion.',
        rationale: hi
          ? 'सर्दियों में सुबह तापमान व्युत्क्रमण (थर्मल इनवर्जन) के कारण महीन कण सतह पर जमा रहते हैं।'
          : 'Ground-level thermal inversion traps toxic fine particulates near breathing height.',
        indoor_alternative: hi ? 'कमरे में 20 मिनट स्ट्रेचिंग व प्राणायाम' : '20 minutes indoor stretching or yoga',
        precautions: [hi ? 'खिड़कियां बंद रखें' : 'Keep windows shut during early morning'],
      },
      {
        title: hi ? 'स्कूल का सफर व कक्षा तैयारी' : 'School Commute & Transit',
        recommended_time: '07:30 AM - 08:30 AM',
        status: 'Caution',
        risk_level: 'High',
        advice: hi
          ? 'बच्चों के लिए फिट-परीक्षित N95 मास्क अनिवार्य करें। स्कूल बस की खिड़कियां बंद रखें।'
          : 'Mandate well-fitting certified N95 masks for children. Keep school bus windows tightly shut.',
        rationale: hi
          ? 'बच्चों का श्वसन दर वयस्कों से अधिक होता है जिससे वे प्रति किलोग्राम अधिक विषैले कण ग्रहण करते हैं।'
          : 'Children inhale more air per kg of body weight, increasing toxic absorption during transit.',
        indoor_alternative: hi ? 'ऑनलाइन क्लास विकल्प यदि उपलब्ध हो' : 'Online schooling if declared by authorities',
        precautions: [hi ? 'बाल-अनुकूल N95 मास्क पहनें' : 'Wear certified pediatric N95 mask'],
      },
      {
        title: hi ? 'दफ्तर आवागमन योजना' : 'Office Commute Planning',
        recommended_time: '09:00 AM - 10:30 AM',
        status: 'Caution',
        risk_level: 'High',
        advice: hi
          ? 'मेट्रो या बंद कार का उपयोग करें। कार में एयर रिसर्कुलेशन चालू रखें। दोपहिया वाहन से बचें।'
          : 'Prioritize Metro or closed car with AC recirculation mode enabled. Avoid two-wheelers.',
        rationale: hi
          ? 'सड़क किनारे वाहनों के धुएं में NO2 व पार्टिकुलेट का स्तर सामान्य से 4 गुना अधिक होता है।'
          : 'Roadside traffic corridors exhibit 4x higher NO2 and particulate density during peak hours.',
        indoor_alternative: hi ? 'घर से कार्य (Work From Home)' : 'Work-from-Home (WFH) if permitted',
        precautions: [hi ? 'कार में रिसर्कुलेशन मोड रखें' : 'Enable internal air recirculation in car'],
      },
    ],
    afternoon: [
      {
        title: hi ? 'प्राकृतिक वेंटिलेशन (खिड़की खोलने का समय)' : 'Natural Aeration Window',
        recommended_time: '01:00 PM - 03:00 PM',
        status: 'Recommended',
        risk_level: 'Moderate',
        advice: hi
          ? 'यदि धूप खिली हो तो 15-20 मिनट के लिए खिड़कियां खोलें ताकि कमरे की CO2 बाहर निकल सके।'
          : 'Open windows for a brief 15-20 min cross-ventilation flush if sun is shining to vent trapped CO2.',
        rationale: hi
          ? 'दोपहर में सौर विकिरण के कारण वायुमंडल की मिक्सिंग लेयर ऊपर उठती है जिससे स्मॉग कम होता है।'
          : 'Mid-afternoon solar heating raises the planetary boundary layer, diluting surface pollution.',
        indoor_alternative: null,
        precautions: [hi ? 'वेंटिलेशन के तुरंत बाद खिड़कियां बंद करें' : 'Close windows promptly after flush'],
      },
      {
        title: hi ? 'घरेलू कार्य व खरीदारी' : 'Outdoor Chores & Errand Planning',
        recommended_time: '01:00 PM - 03:30 PM',
        status: 'Caution',
        risk_level: 'High',
        advice: hi
          ? 'बाहर कपड़े सुखाने से बचें (धूल व कालिख चिपक जाती है)। जरूरी खरीदारी दोपहर 1 से 3 बजे के बीच निपटाएं।'
          : 'Avoid air-drying laundry on balconies as soot adheres to damp fabric. Bundle errands between 1 PM and 3 PM.',
        rationale: hi
          ? 'गीले कपड़ों पर विषैले कण जम जाते हैं और शाम को स्मॉग फिर से घना हो जाता है।'
          : 'Wet fabrics absorb airborne hydrocarbons, and cooling evening air traps renewed emissions.',
        indoor_alternative: hi ? 'कपड़े घर के अंदर सुखाएं' : 'Dry laundry in well-ventilated indoor space',
        precautions: [hi ? 'बाहर जाते समय N95 लगाएं' : 'Wear N95 on grocery runs'],
      },
    ],
    evening: [
      {
        title: hi ? 'शाम का घर वापसी का सफर' : 'Evening Return Transit',
        recommended_time: '06:00 PM - 07:30 PM',
        status: 'Caution',
        risk_level: 'High',
        advice: hi
          ? 'शाम के ट्रैफिक में N95 मास्क पहनें और चौराहों पर रुकने से बचें।'
          : 'Wear N95 on transit and avoid lingering near congested traffic intersections.',
        rationale: hi
          ? 'सूरज ढलने के साथ तापमान गिरता है और शाम के ट्रैफिक का धुआं वातावरण में फंस जाता है।'
          : 'Cooling nocturnal boundary layer traps rush-hour vehicular emissions near surface levels.',
        indoor_alternative: null,
        precautions: [hi ? 'मास्क का इस्तेमाल करें' : 'Keep mask on until safely indoors'],
      },
      {
        title: hi ? 'रात्रि इनडोर वायु शोधन' : 'Nighttime Indoor Air Purification',
        recommended_time: '09:00 PM - 06:00 AM',
        status: 'Recommended',
        risk_level: 'Low',
        advice: hi
          ? 'सोते समय शयनकक्ष में एयर प्यूरीफायर को ऑटो/स्लीप मोड पर रखें और खिड़कियां बंद रखें।'
          : 'Run bedroom HEPA purifier continuously on sleep/auto mode with closed doors and windows.',
        rationale: hi
          ? '8 घंटे की नींद के दौरान स्वच्छ हवा फेफड़ों के ऊतकों को ठीक होने में मदद करती है।'
          : '8 hours of clean air sleep allows mucosal clearance and respiratory tissue recovery.',
        indoor_alternative: null,
        precautions: [hi ? 'कमरे का दरवाजा बंद रखें' : 'Keep bedroom door closed'],
      },
    ],
    school_commute: {
      title: hi ? 'स्कूल का सफर व कक्षा तैयारी' : 'School Commute & Transit',
      recommended_time: '07:30 AM - 08:30 AM',
      status: 'Caution',
      risk_level: 'High',
      advice: hi
        ? 'बच्चों के लिए फिट-परीक्षित N95 मास्क अनिवार्य करें। स्कूल बस की खिड़कियां बंद रखें।'
        : 'Mandate well-fitting certified N95 masks for children. Keep school bus windows tightly shut.',
      rationale: hi
        ? 'बच्चों का श्वसन दर वयस्कों से अधिक होता है जिससे वे प्रति किलोग्राम अधिक विषैले कण ग्रहण करते हैं।'
        : 'Children inhale more air per kg of body weight, increasing toxic absorption during transit.',
      indoor_alternative: hi ? 'ऑनलाइन क्लास विकल्प यदि उपलब्ध हो' : 'Online schooling if declared by authorities',
      precautions: [hi ? 'बाल-अनुकूल N95 मास्क पहनें' : 'Wear certified pediatric N95 mask'],
    },
    office_commute: {
      title: hi ? 'दफ्तर आवागमन योजना' : 'Office Commute Planning',
      recommended_time: '09:00 AM - 10:30 AM',
      status: 'Caution',
      risk_level: 'High',
      advice: hi
        ? 'मेट्रो या बंद कार का उपयोग करें। कार में एयर रिसर्कुलेशन चालू रखें।'
        : 'Prioritize Metro or closed car with AC recirculation mode enabled.',
      rationale: hi
        ? 'सड़क किनारे NO2 व पार्टिकुलेट का स्तर सामान्य से 4 गुना अधिक होता है।'
        : 'Roadside traffic corridors exhibit 4x higher NO2 and particulate density.',
      indoor_alternative: hi ? 'घर से कार्य (Work From Home)' : 'Work-from-Home (WFH) if permitted',
      precautions: [hi ? 'कार में रिसर्कुलेशन मोड रखें' : 'Enable internal air recirculation in car'],
    },
    exercise_plan: {
      title: hi ? 'कसरत व व्यायाम समय-सारणी' : 'Physical Exercise Scheduling',
      recommended_time: '12:30 PM - 03:30 PM',
      status: 'Indoor Alternative',
      risk_level: 'Critical',
      advice: hi
        ? 'बाहर दौड़ना या सैर पूरी तरह से स्थगित करें। इनडोर योग या एयर प्यूरीफायर वाले कमरे में कसरत करें।'
        : 'Strictly avoid outdoor jogging, running, and cycling. Shift all workouts indoors.',
      rationale: hi
        ? 'तीव्र व्यायाम के दौरान फेफड़ों का वायु प्रवाह 10 गुना बढ़ जाता है।'
        : 'Intense aerobic exertion increases pulmonary minute ventilation up to 10-fold.',
      indoor_alternative: hi ? 'घर के अंदर 30 मिनट का योगासन' : '30 minutes of indoor yoga or bodyweight exercise',
      precautions: [hi ? 'सुबह 5 से 9 बजे के बीच सैर न करें' : 'Never jog between 5:00 AM and 9:00 AM in smog'],
    },
    chores_plan: {
      title: hi ? 'घरेलू कार्य व खरीदारी' : 'Outdoor Chores & Errand Planning',
      recommended_time: '01:00 PM - 03:30 PM',
      status: 'Caution',
      risk_level: 'High',
      advice: hi
        ? 'बाहर कपड़े सुखाने से बचें। जरूरी खरीदारी दोपहर 1 से 3 बजे के बीच निपटाएं।'
        : 'Avoid air-drying laundry on balconies. Consolidate errands between 1 PM and 3:30 PM.',
      rationale: hi
        ? 'गीले कपड़ों पर विषैले कण जम जाते हैं।'
        : 'Wet fabrics absorb airborne hydrocarbons.',
      indoor_alternative: hi ? 'कपड़े घर के अंदर सुखाएं' : 'Dry laundry in indoor space',
      precautions: [hi ? 'बाहर जाते समय N95 लगाएं' : 'Wear N95 on grocery runs'],
    },
    family_precautions: [
      hi
        ? 'बच्चों के लिए: आउटडोर खेल रोकें; कमरे में इनडोर खेल खेलें।'
        : 'For Children: Suspend outdoor recess and physical training; replace with indoor reading and games.',
      hi
        ? 'बुजुर्गों के लिए: सुबह 8 बजे से पहले बालकनी में न जाएं; दवाएं समय पर लें।'
        : 'For Seniors: Avoid step-outs before 8:00 AM; monitor resting pulse and maintain cardiovascular medications.',
      hi
        ? 'अस्थमा मरीजों के लिए: इनहेलर हमेशा पास रखें; बाहर निकलने पर N95 अनिवार्य है।'
        : 'For Respiratory Patients: Keep bronchodilator inhalers accessible at all times; mandate N95 outdoors.',
    ],
    disclaimer: hi
      ? 'चिकित्सीय अस्वीकरण: यह दैनिक दिनचर्या योजना केवल पर्यावरणीय जोखिम न्यूनीकरण सुझाव प्रदान करती है, चिकित्सकीय सलाह नहीं।'
      : "Medical Disclaimer: This daily routine plan provides environmental exposure mitigation guidance, not medical diagnosis or treatment. Sensitive individuals should follow their physician's medical action plan.",
    generated_at: new Date().toISOString(),
  };
};

export const getMockIndoorAssessment = (
  stationId: string = 'delhi-anand-vihar',
  language: 'en' | 'hi' = 'en',
  household?: any
): any => {
  const station = MOCK_STATIONS.find((s) => s.id === stationId) || MOCK_STATIONS[0];
  const hi = language === 'hi';
  const area = household?.room_area_sqft || 150;
  const volumeM3 = area * 10 * 0.0283168;
  const cadrM3h = Math.round(volumeM3 * 4.5);
  const cadrCfm = Math.round(cadrM3h / 1.699);

  return {
    station_id: station.id,
    station_name: station.name,
    city: station.city,
    outdoor_aqi: 368,
    outdoor_category: 'Very Poor',
    outdoor_is_demo: true,
    outdoor_data_source: 'Central Pollution Control Board (CPCB) - Offline Fallback Baseline',
    outdoor_observed_at: new Date().toISOString(),
    language,
    ai_provider: 'expert-rules-fallback',
    ai_generated: false,
    has_connected_indoor_sensor: false,
    qualitative_risk: 'High',
    risk_score_numeric: 68,
    risk_summary: hi
      ? 'उच्च इनडोर जोखिम: रसोई का तड़का/धुआं और बाहरी स्मॉग का रिसाव इनडोर हवा पर प्रतिकूल प्रभाव डाल रहा है।'
      : 'High Indoor Risk: Cooking aerosols and outdoor smog infiltration are elevating indoor particulate levels.',
    sensor_notice: hi
      ? 'सेंसर प्रकटीकरण: यह मूल्यांकन आपकी घरेलू आदतों और बाहरी CPCB प्रदूषण के आधार पर एक अनुमानित गुणात्मक जोखिम विश्लेषण है। बिना प्रमाणित इनडोर सेंसर के वास्तविक इनडोर AQI संख्या प्रदर्शित नहीं की जाती है।'
      : 'Sensor Disclosure: This qualitative risk evaluation is modeled from reported household practices and outdoor CPCB ambient infiltration. Without physical in-situ air sensors, AirSaathi AI never fabricates synthetic indoor AQI numbers.',
    ventilation: {
      action: hi ? 'खिड़कियां बंद रखें (सीमित वेंटिलेशन)' : 'Seal / Restrict',
      optimal_window: hi ? 'दोपहर 01:30 बजे से 02:30 बजे' : '01:30 PM - 02:30 PM',
      duration_minutes: 15,
      rationale: hi
        ? 'दोपहर के समय सौर विकिरण से स्मॉग की सघनता सबसे कम होती है। केवल 15 मिनट का फ्लश करें।'
        : 'Solar convective heating raises the planetary boundary layer during mid-afternoon. Limit window opening to a brief 15-minute flush.',
      precautions: [
        hi ? 'सुबह 5 से 10 बजे के बीच खिड़की बिल्कुल न खोलें' : 'Keep all windows sealed tight between 5:00 AM and 10:00 AM',
        hi ? 'वेंटिलेशन के तुरंत बाद खिड़कियां बंद करें' : 'Close windows promptly after flush and run purifier',
      ],
    },
    purifier_guidance: {
      room_area_sqft: area,
      recommended_min_cadr_m3h: cadrM3h,
      recommended_min_cadr_cfm: cadrCfm,
      target_ach: 4.5,
      filter_type_guidance: hi
        ? 'सत्य HEPA H13/H14 प्रमाणित फिल्टर चुनें जो 0.3 माइक्रोन के 99.97% कण रोकता है।'
        : 'Select certified True HEPA (H13/H14) capable of capturing 99.97% of particles down to 0.3 microns. Avoid standalone ozone/ionizer devices.',
      placement_tips: [
        hi ? 'दीवार और पर्दों से कम से कम 1.5 से 2 फीट दूर रखें' : 'Position at least 1.5 - 2 feet away from walls and heavy drapery',
        hi ? 'कमरे के केंद्र में खुली हवा के प्रवाह की दिशा में रखें' : 'Orient towards central living breathing zone for unhindered airflow',
        hi ? 'कमरे के दरवाजे व खिड़कियां बंद रखकर चलाएं' : 'Keep doors and external windows closed during operation',
      ],
      maintenance_schedule: hi
        ? 'प्री-फिल्टर को हर 2-3 सप्ताह में वैक्यूम करें। मुख्य HEPA फिल्टर को 6-12 महीने में बदलें।'
        : 'Vacuum or wash external mesh pre-filter every 2-3 weeks in winter. Replace main True HEPA core every 6-12 months.',
    },
    kitchen_guidance: {
      risk_summary: hi
        ? 'भारतीय तड़का और डीप फ्राइंग से PM2.5 का स्तर 500 µg/m³ के पार जा सकता है।'
        : 'Indian spices, dry chili tempering (tadka) and deep frying cause rapid indoor PM2.5 spikes exceeding 500 µg/m³.',
      chimney_exhaust_guidance: hi
        ? 'गैस जलाने से 2 मिनट पहले एग्जॉस्ट/चिमनी चालू करें और खाना पकने के 5 मिनट बाद तक चालू रखें।'
        : 'Turn on kitchen chimney or exhaust fan 2 minutes BEFORE lighting stove, and run for 5 minutes post-cooking.',
      cooking_habits_advice: [
        hi ? 'तड़के और छौंक के समय पैन पर ढक्कन लगाएं' : 'Cover pans with lids or splatter mesh during tempering/frying',
        hi ? 'रसोई का दरवाजा अन्य कमरों से अलग रखें' : 'Keep kitchen door closed to isolate cooking aerosols from bedrooms',
      ],
      combustion_safety: hi
        ? 'गैस स्टोव की लौ हमेशा नीली होनी चाहिए। पीली लौ कार्बन मोनोऑक्साइड का संकेत है।'
        : 'Ensure gas burner produces crisp blue flame. Yellow flame signals incomplete combustion and toxic carbon monoxide.',
    },
    room_recommendations: {
      bedroom: {
        room_name: hi ? 'शयनकक्ष (Bedroom)' : 'Bedroom',
        primary_threats: [
          hi ? 'बिस्तर के धूल कण (Dust Mites)' : 'Dust mites & settled bedding particulates',
          hi ? 'खिड़की व बालकनी से बाहरी स्मॉग का रिसाव' : 'Nighttime outdoor smog infiltration through gaps',
        ],
        immediate_actions: [
          hi ? 'दरवाजे के नीचे ड्राफ्ट स्टॉपर लगाएं' : 'Install door draft stoppers to block living room corridor air',
          hi ? 'सोते समय खिड़की पूरी तरह बंद रखें' : 'Keep windows locked shut throughout sleep hours',
        ],
        night_protocol: hi
          ? 'सोने से 30 मिनट पहले एयर प्यूरीफायर को स्लीप मोड पर चालू करें।'
          : 'Power on HEPA purifier 30 minutes before bedtime on sleep/auto mode for 8 hours of clean respiratory recovery.',
        lifestyle_adjustments: [
          hi ? 'कमरे में अगरबत्ती या मच्छर क्वाइल बिल्कुल न जलाएं' : 'Never burn mosquito coils or incense sticks in sleeping quarters',
        ],
      },
      kitchen: {
        room_name: hi ? 'रसोईघर (Kitchen)' : 'Kitchen',
        primary_threats: [
          hi ? 'तड़के और तेल का धुआं (PM2.5 > 500 µg/m³)' : 'Ultra-fine cooking aerosols from oil & chili tempering',
        ],
        immediate_actions: [
          hi ? 'खाना बनाते समय चिमनी का पूरा उपयोग करें' : 'Run ducted chimney on medium/high speed during all frying',
        ],
        night_protocol: null,
        lifestyle_adjustments: [
          hi ? 'तड़के के दौरान पैन को ढंक कर रखें' : 'Cover hot oil vessels with splatter screens',
        ],
      },
      living_room: {
        room_name: hi ? 'लिविंग रूम (Living Room)' : 'Living Room',
        primary_threats: [
          hi ? 'मुख्य दरवाजे से जूतों की धूल और बाहरी प्रदूषण' : 'Tracked-in street dust, soot and heavy footfall re-suspension',
        ],
        immediate_actions: [
          hi ? 'बाहर के जूते दरवाजे के बाहर ही उतारें' : 'Enforce a strict no outdoor shoes inside policy',
          hi ? 'सूखे झाड़ू की जगह गीला पोछा लगाएं' : 'Switch completely from dry brooms to microfiber wet mopping',
        ],
        night_protocol: null,
        lifestyle_adjustments: [
          hi ? 'अगरबत्ती की जगह इलेक्ट्रॉनिक दीया चुनें' : 'Substitute combustion incense with electric diffusers or brass lamps',
        ],
      },
    },
    actionable_checklist: [
      hi
        ? 'सप्ताह में कम से कम 3 बार गीले माइक्रोफाइबर कपड़े से पोछा लगाएं (सूखी झाड़ू न लगाएं)'
        : 'Switch exclusively to damp microfiber mopping (dry brooms re-suspend hazardous PM10 into the breathing zone)',
      hi
        ? 'तड़के और छौंक से 2 मिनट पहले रसोई का एग्जॉस्ट/चिमनी चालू करें'
        : 'Turn on kitchen chimney or exhaust fan 2 minutes before cooking begins and maintain for 5 minutes after',
      hi
        ? 'घर के अंदर अगरबत्ती, धूप या मच्छर क्वाइल जलाने से बचें'
        : 'Eliminate daily burning of incense sticks (agarbatti), dhoop, and mosquito coils in enclosed living spaces',
      hi
        ? 'शयनकक्ष में HEPA H13 एयर प्यूरीफायर को रात भर ऑटो मोड पर चलाएं'
        : 'Operate True HEPA (H13) air purifier in bedrooms throughout sleep hours with doors closed',
    ],
    plant_myth_clarification: hi
      ? 'वैज्ञानिक स्पष्टीकरण (पौधों का मिथक): वास्तविक घरों में हवा का आदान-प्रदान पौधों की शोधन क्षमता से 100 गुना अधिक होता है। पौधे सुंदर हैं, परंतु वे भारी PM2.5, NO2 या तड़के के धुएं को साफ नहीं कर सकते। इसके लिए प्रमाणित HEPA फिल्टर और एग्जॉस्ट ही आवश्यक हैं।'
      : 'Scientific Clarification on Indoor Plants: Potted plants are often marketed as natural air purifiers citing the 1989 NASA study. However, real-world residential air exchange rates overpower plant phytoremediation by more than 100-fold. Potted plants cannot replace mechanical True HEPA filtration or kitchen exhaust systems.',
    disclaimer: hi
      ? 'चिकित्सीय अस्वीकरण: यह इनडोर वायु सहायक केवल पर्यावरणीय जोखिम न्यूनीकरण सुझाव प्रदान करता है, बीमारी का निदान या उपचार नहीं। HEPA प्यूरीफायर या N95 मास्क 100% सुरक्षा की गारंटी नहीं देते।'
      : 'Medical Disclaimer: This indoor air assistant provides environmental hazard reduction guidance, not medical diagnosis or treatment. Air purifiers and N95 masks reduce particulate mass but do not provide absolute immunity.',
    generated_at: new Date().toISOString(),
  };
};

export const getMockChatResponse = (
  message: string,
  stationId: string = 'delhi-anand-vihar',
  language: string = 'en'
): ChatResponse => {
  const isHi = language === 'hi';
  const query = (message || '').toLowerCase();
  const station = MOCK_STATIONS.find((s) => s.id === stationId) || MOCK_STATIONS[0];
  const current = getMockCurrentAqi(stationId);

  let replyText = '';
  let followups: string[] = [];

  if (query.includes('pm2.5') || query.includes('pm10') || query.includes('पार्टिकुलेट') || query.includes('कण')) {
    if (isHi) {
      replyText = `**PM2.5 और PM10 में मुख्य अंतर:**\n\n- **PM10** (व्यास <= 10 µm): धूल, पराग और निर्माण कण। ये नाक और ऊपरी श्वसन तंत्र में फंसते हैं।\n- **PM2.5** (व्यास <= 2.5 µm): दहन धुआं, वाहन उत्सर्जन और पराली का धुआं। यह सीधे फेफड़ों की गहराई (एल्वियोली) और रक्तप्रवाह में पहुंचता है।\n\nवर्तमान में **${station.name}** पर प्रमुख प्रदूषक **${current.prominent_pollutant}** (AQI: ${current.aqi}) है।`;
      followups = ['क्या कपड़े का मास्क PM2.5 रोकता है?', 'घर में PM2.5 कैसे कम करें?', 'N95 मास्क कितने दिन चलता है?'];
    } else {
      replyText = `**Key differences between PM2.5 and PM10:**\n\n- **PM10** (<= 10 µm aerodynamic diameter): Coarse dust, pollen, and construction debris. Filtered largely by upper respiratory nasal passages.\n- **PM2.5** (<= 2.5 µm): Ultra-fine combustion aerosols, vehicular exhaust, and secondary nitrates. Bypasses ciliated airways directly into alveolar air-sacs and systemic bloodstream.\n\nCurrently at **${station.name}**, the prominent pollutant is **${current.prominent_pollutant}** with an AQI of **${current.aqi}** (${current.category}).`;
      followups = ['Does a surgical or cloth mask block PM2.5?', 'How can I lower PM2.5 indoors?', 'How many hours does an N95 mask last?'];
    }
  } else if (query.includes('child') || query.includes('kid') || query.includes('pediatric') || query.includes('बच्च') || query.includes('शिशु')) {
    if (isHi) {
      replyText = `**बच्चों की स्मॉग से सुरक्षा:**\n\n1. **शारीरिक संवेदनशीलता:** बच्चे प्रति किलोग्राम शरीर वजन वयस्कों की तुलना में दोगुनी तेजी से सांस लेते हैं।\n2. **सुबह का समय:** जब तक एक्यूआई 200 से अधिक हो, सुबह की आउटडोर खेलकूद या असेंबली पूरी तरह टालें।\n3. **मास्क:** यदि बच्चा 4 वर्ष से बड़ा है, तो बाल-आकार (kid-sized) का प्रमाणित N95 मास्क पहनाएं जिसमें नाक के पास कोई गैप न हो।\n4. **आहार:** पर्याप्त गुनगुना पानी और ताजे फल दें। किसी गंभीर खांसी पर डॉक्टर से सलाह लें।`;
      followups = ['क्या बच्चों के लिए N95 मास्क सुरक्षित है?', 'स्कूल बस में खिड़कियां बंद रखनी चाहिए?', 'कमरे में एयर प्यूरीफायर की गति क्या रखें?'];
    } else {
      replyText = `**Pediatric Protection Guidelines during High AQI:**\n\n1. **Biological Vulnerability:** Children inhale ~50% more air per kilogram of body weight compared to adults, accelerating toxin absorption.\n2. **Morning Outdoor Restrictions:** Postpone early outdoor physical activities, school assemblies, and sports when AQI exceeds 200.\n3. **Pediatric Fit Masks:** Cloth and surgical masks leak heavily. Use properly sized pediatric N95/FFP2 respirators without exhalation valves for children over 4 years.\n4. **Hydration & Vigilance:** Maintain consistent hydration and seek clinical attention if dry barking cough or wheezing develops.`;
      followups = ['Are N95 masks safe for school-age children?', 'Should school bus windows remain shut in winter?', 'What purifier setting is optimal for a nursery?'];
    }
  } else if (query.includes('exercise') || query.includes('walk') || query.includes('run') || query.includes('व्यायाम') || query.includes('दौड़') || query.includes('टहल')) {
    if (isHi) {
      replyText = `**व्यायाम और मॉर्निंग वॉक संबंधी सलाह:**\n\n- **वर्तमान AQI:** ${station.name} पर AQI **${current.aqi}** (${current.category}) है।\n- **निर्णय:** जब AQI बहुत खराब (300+) या गंभीर हो, तो बाहर दौड़ना या तेज चलना स्वास्थ्य के लिए हानिकारक हो सकता है क्योंकि गहरी सांस लेने से फेफड़ों में 10 गुना अधिक जहरीले कण जाते हैं।\n- **सुझाव:** सुबह 5 से 8 बजे के बजाय दोपहर 12 से 4 बजे हल्की चहलकदमी करें, या घर के अंदर योग/स्ट्रेचिंग करें।`;
      followups = ['क्या N95 मास्क पहनकर दौड़ना सुरक्षित है?', 'दोपहर में धूप निकलने पर स्मॉग कम क्यों होता है?', 'घर में कौन सा व्यायाम सुरक्षित है?'];
    } else {
      replyText = `**Exercise & Morning Walk Advisory:**\n\n- **Current AQI Context:** ${station.name} is recording an AQI of **${current.aqi}** (${current.category}).\n- **Impact:** Intense outdoor cardiovascular workouts during high AQI cause mouth breathing, bypassing nasal filtration and increasing deep alveolar particulate deposition by up to 10-fold.\n- **Action:** Shift strenuous workouts indoors (yoga, bodyweight, treadmill). If walking outside, postpone to 12:00 PM – 4:00 PM during solar inversion lift, wearing an N95 respirator.`;
      followups = ['Is running with an N95 mask safe?', 'Why does afternoon solar heating reduce smog near ground?', 'What are safe indoor cardio alternatives?'];
    }
  } else if (query.includes('plant') || query.includes('पौध') || query.includes('money plant') || query.includes('snake plant')) {
    if (isHi) {
      replyText = `**पौधों द्वारा वायु शुद्धिकरण का वैज्ञानिक सच:**\n\n- **नासा अध्ययन (1989):** यह प्रयोग एक सीलबंद छोटे कांच के डिब्बे (sealed chamber) में किया गया था, वास्तविक घर में नहीं।\n- **वास्तविकता:** एक सामान्य घर में प्राकृतिक वायु रिसाव (air exchange) पौधों की गति से 100 गुना अधिक होता है। पौधे सुंदर हैं और मानसिक शांति देते हैं, परंतु वे भारी PM2.5, NO2 या धुएं को साफ नहीं कर सकते।\n- **समाधान:** वास्तविक पार्टिकुलेट प्रदूषण के लिए प्रमाणित True HEPA फिल्टर आवश्यक है।`;
      followups = ['क्या स्नेक प्लांट रात में ऑक्सीजन देता है?', 'HEPA H13 और साधारण फिल्टर में क्या अंतर है?', 'कमरे के आकार के अनुसार प्यूरीफायर कैसे चुनें?'];
    } else {
      replyText = `**Scientific Truth on Indoor Plants & Air Quality:**\n\n- **The 1989 NASA Experiment:** NASA studied plants in sealed, airtight chambers with artificial lighting—conditions entirely detached from residential homes.\n- **Real-World Physics:** Standard homes experience natural air exchange rates (0.5 to 2.0 air changes/hour) that overwhelm plant bio-filtration by over 100x.\n- **Verdict:** While indoor plants are aesthetically pleasant and support mental well-being, they cannot remove PM2.5, sulfur dioxide, or cooking aerosols. Mechanical True HEPA filtration and exhaust ventilation remain essential.`;
      followups = ['Does snake plant generate enough oxygen to matter?', 'What is CADR in air purifiers?', 'Can carbon filters remove cooking smells?'];
    }
  } else {
    if (isHi) {
      replyText = `**नमस्ते! मैं एयरसाथी AI सहायक हूँ।**\n\nवर्तमान में **${station.name}** पर AQI **${current.aqi}** (${current.category}) दर्ज है।\n\nमैं आपकी कैसे मदद कर सकता हूँ?\n- बच्चों व बुजुर्गों के लिए स्मॉग सावधानियां\n- N95 मास्क का सही चुनाव और उपयोग\n- घर और रसोई में इनडोर प्रदूषण कम करने के उपाय\n- व्यायाम और आवागमन के लिए सुरक्षित समय`;
      followups = ['PM2.5 और PM10 में क्या अंतर है?', 'आज बच्चों को स्कूल भेजते समय क्या सावधानी बरतें?', 'कमरे में एयर प्यूरीफायर कैसे रखें?'];
    } else {
      replyText = `**Hello! I am your AirSaathi AI Environmental Assistant.**\n\nCurrently, **${station.name}** is reporting an AQI of **${current.aqi}** (${current.category}) with prominent pollutant **${current.prominent_pollutant}**.\n\nHere is how I can assist you:\n- Smog precautions for children, seniors, and sensitive individuals\n- Selecting and fitting certified N95 respirators\n- Lowering indoor particulate matter and kitchen emissions\n- Optimal timing for outdoor commutes and physical activities`;
      followups = ['What is the difference between PM2.5 and PM10?', 'How should I protect children during peak morning smog?', 'Can indoor plants replace a HEPA air purifier?'];
    }
  }

  return {
    message: replyText,
    language,
    ai_provider: 'expert-rules-fallback',
    ai_generated: false,
    context_used: {
      station_id: station.id,
      station_name: station.name,
      city: station.city,
      aqi: current.aqi,
      category: current.category,
      prominent_pollutant: current.prominent_pollutant,
      is_demo_data: true,
      data_source: 'AirSaathi Baseline Demo',
      observed_at: new Date().toISOString(),
    },
    suggested_followups: followups,
    disclaimer: isHi
      ? 'चिकित्सीय अस्वीकरण: एयरसाथी AI केवल पर्यावरणीय दिशानिर्देश प्रदान करता है, कोई चिकित्सकीय परामर्श या दवा का नुस्खा नहीं।'
      : 'Medical Disclaimer: AirSaathi AI provides environmental risk guidance, not medical diagnosis or prescription. Consult a qualified physician for respiratory distress.',
    timestamp: new Date().toISOString(),
  };
};

export const getMockMobilityPlan = (request: MobilityRequest): MobilityPlanResponse => {
  const stationId = request.station_id || 'delhi-anand-vihar';
  const language = request.language || 'en';
  const isHi = language === 'hi';
  const distance = Math.max(0.1, request.distance_km || 10.0);
  const currentMode = request.current_mode || 'petrol_car';
  const station = MOCK_STATIONS.find((s) => s.id === stationId) || MOCK_STATIONS[0];
  const current = getMockCurrentAqi(stationId);
  const aqi = current.aqi;

  const tripsPerDay = request.frequency === 'one_way' || request.frequency === 'occasional' ? 1.0 : 2.0;

  // Emission factors (g CO2e / km per passenger)
  const factors: Record<TransportMode, { direct: number; grid: number; perP: number; labelEn: string; labelHi: string }> = {
    metro: { direct: 0.0, grid: 22.0 * distance, perP: 22.0 * distance, labelEn: 'Urban Metro Rail', labelHi: 'मेट्रो रेल' },
    electric_bus: { direct: 0.0, grid: 24.5 * distance, perP: 24.5 * distance, labelEn: 'Electric City Bus (e-Bus)', labelHi: 'इलेक्ट्रिक बस (e-Bus)' },
    public_bus: { direct: 31.4 * distance, grid: 0.0, perP: 31.4 * distance, labelEn: 'Public City Bus', labelHi: 'पब्लिक सिटी बस' },
    carpool: { direct: 55.0 * distance, grid: 0.0, perP: 55.0 * distance, labelEn: 'Shared Carpooling (3-person)', labelHi: 'कारपूलिंग (3-व्यक्ति)' },
    electric_car: { direct: 0.0, grid: 71.6 * distance, perP: 71.6 * distance, labelEn: 'Electric Car (EV)', labelHi: 'इलेक्ट्रिक कार (EV)' },
    electric_two_wheeler: { direct: 0.0, grid: 25.1 * distance, perP: 25.1 * distance, labelEn: 'Electric Scooter (e-2W)', labelHi: 'इलेक्ट्रिक स्कूटर (e-2W)' },
    cng_auto: { direct: 36.0 * distance, grid: 0.0, perP: 36.0 * distance, labelEn: 'Shared CNG Auto', labelHi: 'सीएनजी ऑटो' },
    two_wheeler: { direct: 52.0 * distance, grid: 0.0, perP: 52.0 * distance, labelEn: 'Petrol Two-Wheeler', labelHi: 'पेट्रोल दोपहिया' },
    petrol_car: { direct: 165.0 * distance, grid: 0.0, perP: 165.0 * distance, labelEn: 'Private Petrol Car', labelHi: 'निजी पेट्रोल कार' },
    diesel_car: { direct: 175.0 * distance, grid: 0.0, perP: 175.0 * distance, labelEn: 'Private Diesel Car', labelHi: 'निजी डीजल कार' },
    cycling: { direct: 0.0, grid: 0.0, perP: 0.0, labelEn: 'Active Cycling', labelHi: 'साइकिल चलाना' },
    walking: { direct: 0.0, grid: 0.0, perP: 0.0, labelEn: 'Active Walking', labelHi: 'पैदल चलना' },
  };

  const basePerP = 165.0 * distance;

  const modeComparisons: ModeEmissionDetail[] = (Object.keys(factors) as TransportMode[]).map((mode) => {
    const f = factors[mode];
    const savingsG = Math.max(0, Math.round((basePerP - f.perP) * 10) / 10);
    const savingsPct = basePerP > 0 ? Math.round((savingsG / basePerP) * 1000) / 10 : 0;

    let suitability = isHi ? 'अनुशंसित' : 'Recommended';
    let verdict = isHi ? 'सुचारु यात्रा विकल्प।' : 'Viable transit option.';
    let exposure = 'Low';
    let precautions: string[] = [];

    if (aqi >= 301) {
      if (mode === 'walking' || mode === 'cycling') {
        suitability = isHi ? 'आज वर्जित' : 'Not Advised Today';
        verdict = isHi
          ? 'अत्यधिक स्मॉग जोखिम: गहरी सांस लेने से PM2.5 फेफड़ों में गहराई तक समा जाता है।'
          : 'Critical Smog Hazard: Deep inhalation bypasses upper airways during severe pollution.';
        exposure = 'Severe';
        precautions = isHi ? ['सक्रिय यात्रा टालें', 'मेट्रो या वातानुकूलित बस चुनें'] : ['Avoid outdoor active travel', 'Choose enclosed AC transit'];
      } else if (mode === 'metro') {
        suitability = isHi ? 'सर्वोत्तम' : 'Optimal Today';
        verdict = isHi ? 'भूमिगत व वातानुकूलित कोच सड़क स्तर के जहरीले स्मॉग से बचाते हैं।' : 'Grade-separated air-conditioned electric transit bypasses surface smog.';
        exposure = 'Low';
        precautions = isHi ? ['स्टेशन पर N95 मास्क पहनें'] : ['Wear N95 mask at station gates'];
      } else if (mode === 'two_wheeler' || mode === 'electric_two_wheeler') {
        suitability = isHi ? 'सावधानी' : 'Caution - High Exposure';
        verdict = isHi ? 'सड़क स्तर पर अत्यधिक धुआं। बिना मास्क यात्रा न करें।' : 'High roadside soot exposure. Do not travel unmasked.';
        exposure = 'High';
        precautions = isHi ? ['N95 मास्क अनिवार्य रूप से लगाएं'] : ['Wear certified N95 respirator'];
      }
    } else if (aqi >= 201) {
      if (mode === 'walking' && distance > 1.5) {
        suitability = isHi ? 'वर्जित' : 'Not Advised';
        verdict = isHi ? 'लंबी पैदल दूरी फेफड़ों पर प्रदूषण का भार बढ़ाती है।' : 'Long walking increases cumulative PM2.5 lung load.';
        exposure = 'High';
      } else if (mode === 'cycling') {
        suitability = isHi ? 'सावधानी' : 'Caution';
        verdict = isHi ? 'साइकिल चलाते समय सांस की गति तेज होती है।' : 'Aerobic effort accelerates particulate inhalation.';
        exposure = 'Moderate';
      }
    }

    return {
      mode,
      label: isHi ? f.labelHi : f.labelEn,
      direct_emissions_g: Math.round(f.direct * 10) / 10,
      grid_indirect_emissions_g: Math.round(f.grid * 10) / 10,
      total_emissions_g: Math.round((f.direct + f.grid) * 10) / 10,
      per_passenger_emissions_g: Math.round(f.perP * 10) / 10,
      co2e_savings_vs_baseline_g: savingsG,
      co2e_savings_pct: savingsPct,
      suitability_score: suitability,
      aqi_safety_verdict: verdict,
      exposure_level: exposure,
      precautions,
    };
  });

  // Current mode metrics
  const currentFact = factors[currentMode] || factors.petrol_car;
  const currentTripG = Math.round(currentFact.perP * 10) / 10;
  const currentDailyG = Math.round(currentTripG * tripsPerDay * 10) / 10;

  // Carpool potential
  const soloG = Math.round(165.0 * distance * 10) / 10;
  const shared3G = Math.round((soloG / 3.0) * 10) / 10;
  const dailySaveKg = Math.round(((soloG - shared3G) * tripsPerDay / 1000.0) * 100) / 100;
  const annualSaveKg = Math.round(dailySaveKg * 250.0 * 10) / 10;

  // Recommendation logic
  let recMode: TransportMode = 'metro';
  let recLabel = isHi ? 'मेट्रो रेल' : 'Urban Metro Rail';
  let recReason = isHi
    ? 'लंबी दूरी के लिए मेट्रो 86% कार्बन उत्सर्जन घटाती है और सड़क स्तर के स्मॉग से बचाती है।'
    : 'Electrified rail cuts per-passenger emissions by ~86% and shields from surface smog.';

  if (aqi <= 200 && distance <= 2.0) {
    recMode = 'walking';
    recLabel = isHi ? 'पैदल चलना' : 'Active Walking';
    recReason = isHi ? '2 किमी से कम दूरी में पैदल चलना शून्य उत्सर्जन और स्वास्थ्यवर्धक है।' : 'Under 2 km with moderate AQI: 100% zero emissions with cardiovascular fitness.';
  } else if (aqi <= 200 && distance <= 6.0) {
    recMode = 'cycling';
    recLabel = isHi ? 'साइकिल चलाना' : 'Active Cycling';
    recReason = isHi ? 'मध्यम दूरी के लिए साइकिल सबसे टिकाऊ और शून्य-उत्सर्जन साधन है।' : 'Zero tailpipe emissions and zero grid reliance for trips under 6 km.';
  } else if (distance < 5.0) {
    recMode = 'carpool';
    recLabel = isHi ? 'कारपूलिंग (3-व्यक्ति)' : 'Shared Carpool';
    recReason = isHi ? 'साझा कारपूल से व्यक्तिगत उत्सर्जन में 67% की सीधी कटौती होती है।' : '3-person carpool cuts personal carbon emissions by 67% without route transfers.';
  }

  const activeAdvisory = aqi >= 301
    ? (isHi
        ? 'चेतावनी: वायु गुणवत्ता गंभीर (AQI > 300) है। पैदल या साइकिल से यात्रा करने पर गहरी सांस लेने से PM2.5 फेफड़ों में गहराई तक पहुंचता है। आज सक्रिय आउटडोर आवागमन पूरी तरह टालें।'
        : 'Critical Warning: AQI is Severe (> 300). Strenuous walking or cycling induces high minute-ventilation, depositing toxic PM2.5 deep into alveoli. Avoid outdoor active commuting today.')
    : (isHi
        ? 'सावधानी: वायु गुणवत्ता बहुत खराब है। 1.5 किमी से अधिक सक्रिय यात्रा न करें और N95 मास्क पहनें।'
        : 'Caution: AQI is elevated. Restrict active travel to short trips and wear a certified N95 respirator.');

  const aiText = isHi
    ? `### सतत गतिशीलता परामर्श (${station.name})\n\n- **वर्तमान उत्सर्जन:** आपकी ${distance} किमी की यात्रा में प्रतिदिन लगभग **${currentDailyG} ग्राम CO2e** उत्सर्जित होता है।\n- **सर्वोत्तम अनुशंसित साधन:** **${recLabel}**\n  - *कारण:* ${recReason}\n- **वायु गुणवत्ता व स्वास्थ्य सावधानी:** वर्तमान में AQI **${aqi}** (${current.category}) है। ${activeAdvisory}\n- **कारपूलिंग व सार्वजनिक परिवहन:** मेट्रो या 3-व्यक्ति कारपूलिंग अपनाने से यात्रा का कार्बन फुटप्रिंट 67% से 85% तक घट जाता है।\n- **वाहन केबिन प्रोटोकॉल:** सड़क यात्रा के दौरान वाहन की खिड़कियां बंद रखें और एयर कंडीशनर को **रीसर्क्युलेशन मोड** पर रखें।`
    : `### Sustainable Mobility Strategy (${station.name})\n\n- **Current Carbon Baseline:** Your ${distance} km commute generates approximately **${currentDailyG} g CO2e** per day.\n- **Recommended Mode:** **${recLabel}**\n  - *Rationale:* ${recReason}\n- **AQI Exposure Safeguard:** Currently, AQI is **${aqi}** (${current.category}). ${activeAdvisory}\n- **Public Transit & Ridesharing:** Switching to electrified rail (Metro) or a 3-person carpool reduces per-passenger carbon emissions by 67% to 86%.\n- **Vehicle Cabin Protocol:** Keep car windows closed in congested corridors and switch ventilation to **Air Recirculation Mode** to keep out toxic roadside particulates.`;

  return {
    station_id: station.id,
    station_name: station.name,
    city: station.city,
    aqi,
    category: current.category,
    prominent_pollutant: current.prominent_pollutant,
    is_demo_data: true,
    data_source: 'AirSaathi Baseline Demo',
    observed_at: new Date().toISOString(),
    language,
    distance_km: distance,
    frequency: request.frequency || 'daily_round_trip',
    current_mode: currentMode,
    current_trip_emissions_g: currentTripG,
    current_daily_emissions_g: currentDailyG,
    mode_comparisons: modeComparisons,
    recommended_mode: recMode,
    recommended_mode_label: recLabel,
    recommended_mode_reason: recReason,
    active_mobility_advisory: activeAdvisory,
    carpool_potential: {
      solo_trip_emissions_g: soloG,
      shared_2_person_emissions_g: Math.round((soloG / 2.0) * 10) / 10,
      shared_3_person_emissions_g: shared3G,
      shared_4_person_emissions_g: Math.round((soloG / 4.0) * 10) / 10,
      daily_savings_kg: dailySaveKg,
      annual_savings_kg: annualSaveKg,
    },
    ai_recommendation: aiText,
    ai_provider: 'expert-rules-fallback',
    ai_generated: false,
    methodology_notes: [
      'Modeled emissions are calculated based on India Central Electricity Authority (CEA v19) national grid baseline: ~716 g CO2/kWh and ARAI standard vehicle test figures.',
      'Private petrol car baseline: ~165 g CO2e/km direct tailpipe emissions.',
      'Electric vehicles (EVs) have zero direct tailpipe exhaust; upstream power-grid emissions are modeled at ~107 g CO2e/km (4W) and ~25 g CO2e/km (2W).',
      'Public bus (average 35 passengers) and Metro Rail (~22 g CO2e/passenger-km) yield high passenger-kilometer efficiency.',
      'Active travel (walking/cycling) is modeled as zero-emission but carries respiratory exposure risks during high AQI episodes.',
    ],
    disclaimer: isHi
      ? 'चिकित्सीय व पर्यावरणीय अस्वीकरण: प्रदर्शित कार्बन गणना मॉडल्ड अनुमानों पर आधारित है। वायु प्रदूषण के दिनों में शारीरिक यात्रा (पैदल/साइकिल) की तुलना में श्वसन सुरक्षा को प्राथमिकता दें।'
      : 'Medical & Environmental Disclaimer: Emission metrics represent engineering models based on standardized parameters, not measured tailpipe tests. During elevated AQI, prioritize respiratory protection over active travel.',
    generated_at: new Date().toISOString(),
  };
};
