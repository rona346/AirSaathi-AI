"""AirSaathi AI - AI Daily Routine Planner Service.

Generates personalized, pollution-aware daily schedules for families and communities
integrating real-time CPCB telemetry, meteorological factors, family vulnerability profiles,
and Google Gemini structured JSON outputs with an intelligent rule-based fallback engine.
"""

import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from backend.app.core.config import settings
from backend.app.core.gemini import generate_gemini_text, sanitize_json_output
from backend.app.models.aqi import CurrentAqiResponse
from backend.app.models.routine import (
    ActivityTimeWindow,
    FamilyVulnerabilityInput,
    RoutinePlanRequest,
    RoutinePlanResponse,
    RoutinePreferencesInput,
)
from backend.app.services.live_aqi_provider import get_active_aqi_provider

logger = logging.getLogger(__name__)


class RoutinePlannerService:
    """Orchestrates AI-powered daily routine generation with fallback resilience."""

    # Backward-compatible alias delegating to shared core utility
    _sanitize_json_text = staticmethod(sanitize_json_output)

    @classmethod
    def generate_routine_plan(cls, request: RoutinePlanRequest) -> RoutinePlanResponse:
        """
        Main entry point for generating daily routine plans:
        1. Queries verified AQI telemetry via active provider.
        2. Gathers weather and pollutant context.
        3. Attempts structured generation via Google Gemini API if GEMINI_API_KEY is configured.
        4. Seamlessly falls back to calibrated domain rule engine on quota/API limits or missing key.
        """
        provider = get_active_aqi_provider()
        aqi_data: CurrentAqiResponse = provider.get_current_aqi(request.station_id)

        family_profile = request.family_profile or FamilyVulnerabilityInput()
        preferences = request.preferences or RoutinePreferencesInput()
        language = "hi" if request.language.lower() == "hi" else "en"

        # Attempt Gemini API generation if key is present
        if settings.GEMINI_API_KEY:
            try:
                gemini_res = cls._call_gemini_api(aqi_data, family_profile, preferences, language)
                if gemini_res:
                    return gemini_res
            except Exception as e:
                logger.warning(f"Gemini API generation failed: {e}. Switching to calibrated expert fallback.")

        # Expert rule-based fallback
        return cls._generate_expert_rule_plan(aqi_data, family_profile, preferences, language)

    @classmethod
    def _call_gemini_api(
        cls,
        aqi_data: CurrentAqiResponse,
        family: FamilyVulnerabilityInput,
        preferences: RoutinePreferencesInput,
        language: str,
    ) -> Optional[RoutinePlanResponse]:
        """Calls Google GenAI Interactions API requesting strict structured JSON."""
        prompt = cls._build_gemini_prompt(aqi_data, family, preferences, language)

        try:
            raw_text = generate_gemini_text(prompt)
            if not raw_text or not raw_text.strip():
                logger.warning("Gemini response contained no text content.")
                return None

            # Strip optional markdown JSON fences before json.loads
            clean_json_str = sanitize_json_output(raw_text)
            parsed_json = json.loads(clean_json_str)

            if not isinstance(parsed_json, dict):
                logger.warning(f"Gemini output is not a JSON object (got {type(parsed_json).__name__}).")
                return None

            # Inject metadata to enforce data provenance
            parsed_json["station_id"] = aqi_data.station.id
            parsed_json["station_name"] = aqi_data.station.name
            parsed_json["city"] = aqi_data.station.city
            parsed_json["aqi"] = aqi_data.aqi
            parsed_json["category"] = aqi_data.category.value
            parsed_json["prominent_pollutant"] = aqi_data.prominent_pollutant
            parsed_json["is_demo_data"] = aqi_data.is_demo_data
            parsed_json["data_source"] = aqi_data.data_source
            parsed_json["observed_at"] = aqi_data.last_updated.isoformat()
            parsed_json["language"] = language
            parsed_json["ai_provider"] = "google-gemini"
            parsed_json["ai_generated"] = True
            parsed_json["generated_at"] = datetime.now(timezone.utc).isoformat()

            # Ensure disclaimer is always present and medically conservative
            parsed_json["disclaimer"] = (
                "चिकित्सीय अस्वीकरण: यह योजना पर्यावरणीय जोखिम न्यूनीकरण सुझाव प्रदान करती है, चिकित्सकीय परामर्श नहीं।"
                if language == "hi"
                else "Medical Disclaimer: This routine plan provides environmental exposure mitigation guidance, not medical diagnosis or treatment. Sensitive individuals should follow their physician's action plan."
            )

            return RoutinePlanResponse.model_validate(parsed_json)
        except json.JSONDecodeError as jde:
            logger.warning(f"Failed to decode JSON from Gemini output: {jde}")
            return None
        except Exception as e:
            logger.warning(f"Error calling or validating Gemini plan: {e}")
            return None

    @classmethod
    def _build_gemini_prompt(
        cls,
        aqi_data: CurrentAqiResponse,
        family: FamilyVulnerabilityInput,
        preferences: RoutinePreferencesInput,
        language: str,
    ) -> str:
        """Constructs a scientifically grounded prompt for the Gemini model."""
        pollutants_summary = {
            name: f"{p.value} {p.unit} (Sub-index: {p.sub_index})"
            for name, p in aqi_data.pollutants.items()
        }

        lang_instruction = (
            "You MUST output all titles, advice, rationale, indoor alternatives, and precautions entirely in natural, fluent Hindi (Devanagari script)."
            if language == "hi"
            else "You MUST output all titles, advice, rationale, indoor alternatives, and precautions in fluent English."
        )

        return f"""You are the Lead Environmental Health & Smog Protection Specialist for AirSaathi AI.
Generate a personalized, pollution-aware daily routine schedule for an urban Indian family based on verified CPCB air quality telemetry.

AIR QUALITY CONTEXT:
- Station: {aqi_data.station.name}, {aqi_data.station.city}
- Overall AQI: {aqi_data.aqi} ({aqi_data.category.value})
- Prominent Pollutant: {aqi_data.prominent_pollutant}
- Pollutants Breakdown: {json.dumps(pollutants_summary)}
- Observation Timestamp: {aqi_data.last_updated}
- Is Demonstration Data: {aqi_data.is_demo_data}
- Data Provenance: {aqi_data.data_source}
- Weather: {json.dumps(aqi_data.weather)}

FAMILY VULNERABILITY PROFILE:
- Has Children (<12 yrs): {family.has_children}
- Has Elderly Members (60+ yrs): {family.has_seniors}
- Has Respiratory/Asthma Patient: {family.has_respiratory_condition}
- Has Pregnant Member: {family.is_pregnant}

LIFESTYLE PREFERENCES:
- Early Riser: {preferences.wakes_up_early}
- Office Commuter: {preferences.commutes_to_office}
- School Going Children: {preferences.school_going_kids}
- Daily Exercise: {preferences.exercises_daily} (Preferred: {preferences.preferred_exercise_type})

SAFETY AND DOMAIN PRINCIPLES:
1. DIURNAL ATMOSPHERIC INVERSION: Winter morning hours (06:00 - 09:30 AM) trap toxic particulates near the surface. Advise avoiding vigorous outdoor exercise during early mornings when AQI is Poor/Very Poor/Severe.
2. MID-DAY MIXING HEIGHT: Solar radiation lifts the planetary boundary layer between 12:00 PM and 04:00 PM, typically lowering surface PM concentrations.
3. COMMUTE SAFETY: Recommend transit modes (Metro / AC Bus / closed car with cabin air recirculation) over open 2-wheelers or autos in hazardous smog.
4. INDOOR ALTERNATIVES: Always provide actionable indoor exercise or recreational alternatives.
5. SENSITIVE GROUPS: Emphasize pediatric airway protection, asthma action plans, and elderly cardiovascular care.
6. NO MEDICAL DIAGNOSIS: Provide exposure reduction, never promise complete health immunity.

{lang_instruction}

Output a strictly valid JSON object matching this schema:
{{
  "morning": [
    {{
      "title": "string",
      "recommended_time": "string (e.g. 06:30 AM - 08:00 AM)",
      "status": "Recommended | Caution | Avoid | Indoor Alternative",
      "risk_level": "Low | Moderate | High | Critical",
      "advice": "string",
      "rationale": "string",
      "indoor_alternative": "string or null",
      "precautions": ["string", "string"]
    }}
  ],
  "afternoon": [
    {{
      "title": "string",
      "recommended_time": "string (e.g. 12:00 PM - 02:00 PM)",
      "status": "Recommended | Caution | Avoid | Indoor Alternative",
      "risk_level": "Low | Moderate | High | Critical",
      "advice": "string",
      "rationale": "string",
      "indoor_alternative": "string or null",
      "precautions": ["string"]
    }}
  ],
  "evening": [
    {{
      "title": "string",
      "recommended_time": "string (e.g. 06:00 PM - 08:00 PM)",
      "status": "Recommended | Caution | Avoid | Indoor Alternative",
      "risk_level": "Low | Moderate | High | Critical",
      "advice": "string",
      "rationale": "string",
      "indoor_alternative": "string or null",
      "precautions": ["string"]
    }}
  ],
  "school_commute": {{
    "title": "string",
    "recommended_time": "string",
    "status": "Recommended | Caution | Avoid",
    "risk_level": "Low | Moderate | High | Critical",
    "advice": "string",
    "rationale": "string",
    "indoor_alternative": "string or null",
    "precautions": ["string"]
  }},
  "office_commute": {{
    "title": "string",
    "recommended_time": "string",
    "status": "Recommended | Caution | Avoid",
    "risk_level": "Low | Moderate | High | Critical",
    "advice": "string",
    "rationale": "string",
    "indoor_alternative": "string or null",
    "precautions": ["string"]
  }},
  "exercise_plan": {{
    "title": "string",
    "recommended_time": "string",
    "status": "Recommended | Caution | Avoid | Indoor Alternative",
    "risk_level": "Low | Moderate | High | Critical",
    "advice": "string",
    "rationale": "string",
    "indoor_alternative": "string",
    "precautions": ["string"]
  }},
  "chores_plan": {{
    "title": "string",
    "recommended_time": "string",
    "status": "Recommended | Caution | Avoid",
    "risk_level": "Low | Moderate | High | Critical",
    "advice": "string",
    "rationale": "string",
    "indoor_alternative": "string or null",
    "precautions": ["string"]
  }},
  "family_precautions": ["string", "string", "string"]
}}"""

    @classmethod
    def _generate_expert_rule_plan(
        cls,
        aqi_data: CurrentAqiResponse,
        family: FamilyVulnerabilityInput,
        preferences: RoutinePreferencesInput,
        language: str,
    ) -> RoutinePlanResponse:
        """
        Expert rules-based fallback engine calibrated to official CPCB health advisories
        and atmospheric boundary layer behavior in both Hindi and English.
        """
        aqi = aqi_data.aqi
        is_severe = aqi > 400
        is_very_poor = 300 < aqi <= 400
        is_poor = 200 < aqi <= 300
        is_moderate = 100 < aqi <= 200
        is_good_or_sat = aqi <= 100

        hi = language == "hi"

        # Determine overall risk level
        if is_severe:
            general_risk = "Critical"
        elif is_very_poor:
            general_risk = "High"
        elif is_poor:
            general_risk = "Moderate"
        else:
            general_risk = "Low"

        # 1. School Commute
        if is_severe or is_very_poor:
            school_commute = ActivityTimeWindow(
                title="स्कूल का सफर व कक्षा तैयारी" if hi else "School Commute & Transit",
                recommended_time="07:30 AM - 08:30 AM",
                status="Caution" if not is_severe else "Avoid",
                risk_level="Critical" if is_severe else "High",
                advice=(
                    "बच्चों के लिए फिट-परीक्षित N95/KF94 मास्क अनिवार्य करें। स्कूल बस की खिड़कियां बंद रखें और खुले तिपहिया वाहनों से बचें।"
                    if hi
                    else "Mandate well-fitting certified N95/KF94 masks for children. Keep school bus windows tightly shut and avoid open e-rickshaws."
                ),
                rationale=(
                    "सर्दियों की सुबह जमीनी तापमान व्युत्क्रमण (थर्मल इनवर्जन) के कारण महीन कण सतह पर जमा रहते हैं। बच्चों का श्वसन दर वयस्कों से अधिक होता है।"
                    if hi
                    else "Ground-level thermal inversion traps toxic fine particulates near breathing height during early hours. Children inhale more air per kg of body weight."
                ),
                indoor_alternative=(
                    "यदि स्कूल में हाइब्रिड या ऑनलाइन विकल्प उपलब्ध हो, तो अत्यधिक गंभीर स्मॉग में घर से पढ़ाई चुनें।"
                    if hi
                    else "Opt for online/hybrid schooling if declared by municipal education authorities during Severe+ episodes."
                ),
                precautions=[
                    "बाल-अनुकूल N95 मास्क पहनें" if hi else "Wear certified pediatric N95 mask",
                    "स्कूल के बाद आंखें व चेहरा धोएं" if hi else "Wash eyes and nasal passage after return",
                    "आउटडोर असेंबली व खेल स्थगित करें" if hi else "Suspend outdoor morning assemblies and sports",
                ],
            )
        else:
            school_commute = ActivityTimeWindow(
                title="स्कूल का सफर" if hi else "School Commute",
                recommended_time="07:30 AM - 08:30 AM",
                status="Recommended",
                risk_level="Low" if is_good_or_sat else "Moderate",
                advice=(
                    "नियमित आवागमन सुरक्षित है। सामान्य स्वच्छता और स्वच्छ वायु वेंटिलेशन बनाए रखें।"
                    if hi
                    else "Standard transit is safe. Maintain vehicle air filtration and standard hygiene."
                ),
                rationale=(
                    "वर्तमान वायु गुणवत्ता बच्चों के लिए सुरक्षित सीमा में है।"
                    if hi
                    else "Current ambient air quality is within acceptable national threshold ranges."
                ),
                precautions=["साफ पेयजल साथ रखें" if hi else "Carry clean drinking water"],
            )

        # 2. Office Commute
        if is_severe or is_very_poor:
            office_commute = ActivityTimeWindow(
                title="दफ्तर आवागमन योजना" if hi else "Office Commute Planning",
                recommended_time="09:00 AM - 10:30 AM",
                status="Caution",
                risk_level="High" if not is_severe else "Critical",
                advice=(
                    "मेट्रो, एसी बस या बंद कार का उपयोग करें। यदि कार में हैं तो केबिन एयर रिसर्कुलेशन (Recirculation Mode) चालू रखें। दोपहिया वाहन से बचें।"
                    if hi
                    else "Prioritize Metro, AC electric buses, or closed cars. Switch car AC to recirculation mode to prevent tunnel soot intake. Avoid two-wheelers."
                ),
                rationale=(
                    "सड़क किनारे वाहनों के धुएं में NO2 और अल्ट्रा-फाइन पार्टिकुलेट (PM0.1) का घनत्व 4 गुना अधिक होता है।"
                    if hi
                    else "Roadside traffic corridors exhibit 4x higher NO2 and ultrafine PM0.1 concentrations during morning choke hours."
                ),
                indoor_alternative=(
                    "यदि कंपनी की नीति अनुमति दे, तो घर से कार्य (WFH) का अनुरोध करें।"
                    if hi
                    else "Request Work-from-Home (WFH) on Severe smog days under GRAP-IV guidelines."
                ),
                precautions=[
                    "सड़क पर N95 मास्क पहनें" if hi else "Wear N95 mask on transit routes",
                    "कार में रिसर्कुलेशन मोड रखें" if hi else "Enable internal air recirculation in car",
                    "ट्रैफिक जाम में सीधे शीशा न खोलें" if hi else "Keep vehicle windows closed at intersections",
                ],
            )
        else:
            office_commute = ActivityTimeWindow(
                title="दफ्तर आवागमन" if hi else "Office Commute",
                recommended_time="08:30 AM - 09:30 AM",
                status="Recommended",
                risk_level="Low" if is_good_or_sat else "Moderate",
                advice=(
                    "सामान्य आवागमन सुरक्षित है। सार्वजनिक परिवहन या कारपूलिंग को प्राथमिकता दें।"
                    if hi
                    else "Standard commuting is safe. Prioritize shared transit or electric mobility."
                ),
                rationale="वायु गुणवत्ता स्तर सामान्य जनजीवन के लिए अनुकूल हैं।" if hi else "Ambient conditions support regular commute without respiratory stress.",
                precautions=["पर्यावरण अनुकूल यात्रा विकल्प चुनें" if hi else "Prefer green transit alternatives"],
            )

        # 3. Exercise & Workout Scheduling
        if is_severe or is_very_poor:
            exercise_plan = ActivityTimeWindow(
                title="कसरत व व्यायाम समय-सारणी" if hi else "Physical Exercise Scheduling",
                recommended_time="12:30 PM - 03:30 PM",
                status="Indoor Alternative",
                risk_level="Critical",
                advice=(
                    "बाहर दौड़ना, साइकिल चलाना या सुबह की सैर पूरी तरह से स्थगित करें। इनडोर योग, स्ट्रेचिंग या एयर प्यूरीफायर वाले कमरे में हल्का व्यायाम करें।"
                    if hi
                    else "Strictly avoid outdoor jogging, running, and cycling. Shift all workouts indoors using HEPA-purified rooms or yoga."
                ),
                rationale=(
                    "तीव्र एरोबिक व्यायाम के दौरान फेफड़ों का वायु प्रवाह 10 गुना बढ़ जाता है, जिससे विषैले कण फेफड़ों की गहराई (एल्वियोली) तक पहुंच जाते हैं।"
                    if hi
                    else "Intense aerobic exertion increases pulmonary minute ventilation up to 10-fold, pulling deep particulate mass into alveolar regions."
                ),
                indoor_alternative=(
                    "घर के अंदर 30 मिनट का योगासन, सूर्य नमस्कार या ट्रेडमिल वॉक।"
                    if hi
                    else "30 minutes of indoor gentle yoga, pranayama (in clean air), or light home bodyweight exercises."
                ),
                precautions=[
                    "सुबह 5 से 9 बजे के बीच सैर न करें" if hi else "Never jog between 5:00 AM and 9:00 AM in smog",
                    "कमरे में प्यूरीफायर चालू रखें" if hi else "Run HEPA air purifier on medium/high during workout",
                    "सांस फूलने पर तुरंत रुकें" if hi else "Halt immediately if experiencing chest tightness",
                ],
            )
        elif is_poor:
            exercise_plan = ActivityTimeWindow(
                title="कसरत व व्यायाम समय-सारणी" if hi else "Physical Exercise Scheduling",
                recommended_time="01:00 PM - 04:00 PM",
                status="Caution",
                risk_level="Moderate",
                advice=(
                    "सुबह जल्दी की जगह दोपहर के समय हल्की सैर करें जब सूरज की गर्मी से प्रदूषण की परत ऊपर उठ चुकी हो। अधिक ज़ोरदार कसरत घर में करें।"
                    if hi
                    else "Shift brisk walks to mid-day (1:00 PM - 4:00 PM) when boundary layer expands. Keep vigorous workouts indoors."
                ),
                rationale=(
                    "दोपहर में धूप निकलने से थर्मल मिक्सिंग बढ़ती है, जिससे सतह पर प्रदूषण का घनत्व कम होता है।"
                    if hi
                    else "Afternoon solar insolation drives vertical convective mixing, diluting surface particulate density."
                ),
                indoor_alternative="होम वर्कआउट या इंडोर जिम।" if hi else "Home calisthenics or indoor gym.",
                precautions=["अस्थमा के मरीज इनहेलर साथ रखें" if hi else "Asthma patients keep rescue inhalers handy"],
            )
        else:
            exercise_plan = ActivityTimeWindow(
                title="कसरत व व्यायाम" if hi else "Physical Exercise",
                recommended_time="06:00 AM - 08:30 AM",
                status="Recommended",
                risk_level="Low",
                advice=(
                    "आउटडोर सैर, दौड़ और खेल के लिए बेहतरीन समय है।"
                    if hi
                    else "Ideal conditions for outdoor running, brisk walking, and community sports."
                ),
                rationale="संतोषजनक वायु गुणवत्ता फेफड़ों के लिए सुरक्षित है।" if hi else "Good air exchange supports healthy aerobic training.",
                precautions=["पर्याप्त पानी पिएं" if hi else "Maintain hydration"],
            )

        # 4. Outdoor Chores & Household Tasks
        if is_severe or is_very_poor:
            chores_plan = ActivityTimeWindow(
                title="घरेलू कार्य व खरीदारी" if hi else "Outdoor Chores & Errand Planning",
                recommended_time="01:00 PM - 03:30 PM",
                status="Caution",
                risk_level="High",
                advice=(
                    "बाहर कपड़े सुखाने से बचें (धूल व कालिख चिपक जाती है)। बाहर के जरूरी काम दोपहर 1 से 3 बजे के बीच निपटाएं और खिड़की-दरवाजे बंद रखें।"
                    if hi
                    else "Avoid air-drying laundry on balconies as soot adheres to damp fabric. Consolidate outdoor errands between 1:00 PM and 3:30 PM."
                ),
                rationale=(
                    "गीले कपड़ों पर जहरीले कण जम जाते हैं और शाम को तापमान गिरने के साथ स्मॉग फिर से घना हो जाता है।"
                    if hi
                    else "Wet fabrics absorb airborne polycyclic aromatic hydrocarbons (PAHs), and cooling evening air traps renewed emissions."
                ),
                indoor_alternative=(
                    "कपड़े घर के अंदर सुखाएं और ऑनलाइन डिलीवरी सेवाओं का उपयोग करें।"
                    if hi
                    else "Dry laundry in well-ventilated indoor rooms and bundle grocery trips."
                ),
                precautions=[
                    "बाहर जाते समय N95 लगाएं" if hi else "Wear N95 on grocery runs",
                    "खिड़कियों को टेप या सील से सुरक्षित रखें" if hi else "Keep external doors and drafty windows sealed",
                ],
            )
        else:
            chores_plan = ActivityTimeWindow(
                title="घरेलू कार्य व खरीदारी" if hi else "Outdoor Chores & Errands",
                recommended_time="10:00 AM - 05:00 PM",
                status="Recommended",
                risk_level="Low" if is_good_or_sat else "Moderate",
                advice="सामान्य घरेलू कार्य व खरीदारी की जा सकती है।" if hi else "Standard errands and outdoor activities can proceed safely.",
                rationale="वायुमंडल सामान्य सीमा में है।" if hi else "Atmospheric levels are benign.",
                precautions=[],
            )

        # Build chronological sections: Morning, Afternoon, Evening
        morning = [
            ActivityTimeWindow(
                title="सुबह की सैर / वॉक" if hi else "Early Morning Walk",
                recommended_time="06:00 AM - 08:30 AM",
                status="Avoid" if (is_severe or is_very_poor) else ("Caution" if is_poor else "Recommended"),
                risk_level="Critical" if is_severe else ("High" if is_very_poor else "Low"),
                advice=(
                    "सुबह की सैर पूरी तरह से बंद रखें। घर पर ही हल्के आसन व प्राणायाम करें।"
                    if (is_severe or is_very_poor)
                    else "सामान्य सैर की जा सकती है।"
                ) if hi else (
                    "Avoid morning outdoor walks entirely during heavy smog inversion."
                    if (is_severe or is_very_poor)
                    else "Safe for outdoor walking."
                ),
                rationale=(
                    "सर्दियों में सुबह 6 से 9 बजे के बीच वायु प्रदूषण चरम पर होता है।"
                    if hi
                    else "Morning diurnal peak traps fine pollutants within the lowest 100 meters of the atmosphere."
                ),
                indoor_alternative="कमरे में 20 मिनट स्ट्रेचिंग" if hi else "20 minutes indoor mobility drills",
                precautions=["खिड़कियां बंद रखें" if hi else "Keep windows shut during early morning"],
            ),
            school_commute,
            office_commute,
        ]

        afternoon = [
            ActivityTimeWindow(
                title="प्राकृतिक वेंटिलेशन (खिड़की खोलने का समय)" if hi else "Natural Aeration Window",
                recommended_time="01:00 PM - 03:00 PM",
                status="Recommended" if not is_severe else "Caution",
                risk_level="Moderate" if not is_severe else "High",
                advice=(
                    "यदि धूप खिली हो तो 15-20 मिनट के लिए क्रॉस-वेंटिलेशन करें ताकि कमरे की CO2 बाहर निकल सके।"
                    if hi
                    else "Open windows for a brief 15-20 min cross-ventilation flush if sun is shining, to vent trapped indoor CO2."
                ),
                rationale=(
                    "दोपहर में सौर विकिरण के कारण स्मॉग की सघनता सबसे कम होती है।"
                    if hi
                    else "Peak diurnal boundary layer height occurs at mid-afternoon, offering the lowest ambient PM density."
                ),
                indoor_alternative=None,
                precautions=["वेंटिलेशन के तुरंत बाद खिड़कियां बंद करें" if hi else "Close windows promptly after flush"],
            ),
            chores_plan,
        ]

        evening = [
            ActivityTimeWindow(
                title="शाम का घर वापसी का सफर" if hi else "Evening Return Transit",
                recommended_time="06:00 PM - 07:30 PM",
                status="Caution" if (is_severe or is_very_poor) else "Recommended",
                risk_level="High" if (is_severe or is_very_poor) else "Low",
                advice=(
                    "शाम के ट्रैफिक में N95 मास्क पहनें और व्यस्त चौराहों पर रुकने से बचें।"
                    if hi
                    else "Wear N95 on transit and avoid lingering near traffic congestion nodes."
                ),
                rationale=(
                    "सूरज ढलने के साथ तापमान गिरता है और शाम के ट्रैफिक का धुआं वातावरण में फंस जाता है।"
                    if hi
                    else "Cooling nocturnal boundary layer traps rush-hour vehicular emissions near surface levels."
                ),
                indoor_alternative=None,
                precautions=["मास्क का इस्तेमाल करें" if hi else "Keep mask on until safely indoors"],
            ),
            ActivityTimeWindow(
                title="रात्रि इनडोर वायु शोधन" if hi else "Nighttime Indoor Air Purification",
                recommended_time="09:00 PM - 06:00 AM",
                status="Recommended",
                risk_level="Low",
                advice=(
                    "सोते समय शयनकक्ष में एयर प्यूरीफायर को 'ऑटो' या 'स्लीप' मोड पर रखें और सभी खिड़कियां बंद रखें।"
                    if hi
                    else "Run bedroom HEPA purifier continuously on auto/sleep mode with bedroom doors and windows closed."
                ),
                rationale=(
                    "8 घंटे की नींद के दौरान स्वच्छ हवा फेफड़ों के ऊतकों को ठीक होने में मदद करती है।"
                    if hi
                    else "8 hours of clean air sleep allows mucosal clearance and respiratory tissue recovery."
                ),
                indoor_alternative=None,
                precautions=["दरवाजों के नीचे की दरारें सील रखें" if hi else "Place draft stopper under bedroom door"],
            ),
        ]

        # Family-specific precautions
        family_precautions: List[str] = []
        if family.has_children:
            family_precautions.append(
                "बच्चों के लिए: आउटडोर शारीरिक गतिविधियों और स्कूल असेंबली को रोकें; घर में इनडोर पहेलियां और खेल खेलें।"
                if hi
                else "For Children: Suspend outdoor recess and physical training; replace with indoor reading and games."
            )
        if family.has_seniors:
            family_precautions.append(
                "बुजुर्गों के लिए: सुबह 8 बजे से पहले बालकनी या पार्क में न जाएं; रक्तचाप और ऑक्सीजन स्तर की नियमित जांच करें।"
                if hi
                else "For Seniors: Avoid step-outs before 8:00 AM; monitor resting pulse and maintain cardiovascular medications."
            )
        if family.has_respiratory_condition:
            family_precautions.append(
                "अस्थमा/सांस के मरीजों के लिए: डॉक्टर द्वारा निर्धारित इनहेलर हमेशा साथ रखें; स्मॉग में निकलते ही N95 अनिवार्य है।"
                if hi
                else "For Respiratory Patients: Keep bronchodilator/corticosteroid inhalers accessible at all times; mandate N95 outdoors."
            )
        if family.is_pregnant:
            family_precautions.append(
                "गर्भवती महिलाओं के लिए: उच्च प्रदूषण घंटों में बाहर निकलने से बचें; घर के अंदर स्वच्छ वायु बनाए रखें।"
                if hi
                else "For Expectant Mothers: Minimize high-AQI transit to prevent fine particulate systemic exposure; hydrate frequently."
            )

        if not family_precautions:
            family_precautions.append(
                "सामान्य वयस्क: भारी व्यायाम को इनडोर शिफ्ट करें और हाइड्रेटेड रहें।"
                if hi
                else "Healthy Adults: Shift intense aerobic workouts indoors and maintain generous hydration."
            )

        disclaimer = (
            "चिकित्सीय अस्वीकरण: यह दैनिक दिनचर्या योजना केवल पर्यावरणीय जोखिम न्यूनीकरण सुझाव प्रदान करती है, चिकित्सकीय सलाह या बीमारी का इलाज नहीं। किसी भी स्वास्थ्य समस्या में अपने चिकित्सक से परामर्श लें।"
            if hi
            else "Medical Disclaimer: This daily routine plan provides environmental exposure mitigation guidance, not medical diagnosis or treatment. Sensitive individuals should follow their physician's medical action plan."
        )

        return RoutinePlanResponse(
            station_id=aqi_data.station.id,
            station_name=aqi_data.station.name,
            city=aqi_data.station.city,
            aqi=aqi_data.aqi,
            category=aqi_data.category.value,
            prominent_pollutant=aqi_data.prominent_pollutant,
            is_demo_data=aqi_data.is_demo_data,
            data_source=aqi_data.data_source,
            observed_at=aqi_data.last_updated,
            language=language,
            ai_provider="expert-rules-fallback",
            ai_generated=False,
            morning=morning,
            afternoon=afternoon,
            evening=evening,
            school_commute=school_commute,
            office_commute=office_commute,
            exercise_plan=exercise_plan,
            chores_plan=chores_plan,
            family_precautions=family_precautions,
            disclaimer=disclaimer,
            generated_at=datetime.now(timezone.utc),
        )
