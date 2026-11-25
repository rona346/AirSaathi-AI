"""AirSaathi AI - Indoor Air Quality Assistant Service.

Provides qualitative household air risk evaluation, smart ventilation advice,
HEPA air purifier sizing (CADR), kitchen pollution mitigation, and room-specific protocols.
Adheres strictly to the Zero Synthetic Hallucination policy: never fabricates indoor AQI numbers
without physical in-situ sensors.
"""

import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional

from backend.app.core.config import settings
from backend.app.core.gemini import generate_gemini_text, sanitize_json_output
from backend.app.models.aqi import CurrentAqiResponse
from backend.app.models.indoor import (
    CadrRecommendation,
    HouseholdInput,
    IndoorAssessmentRequest,
    IndoorAssessmentResponse,
    KitchenGuidance,
    QualitativeRiskLevel,
    RoomSpecificRecommendation,
    RoomType,
    VentilationAdvice,
    VentilationStatus,
)
from backend.app.services.live_aqi_provider import get_active_aqi_provider

logger = logging.getLogger(__name__)


class IndoorAirService:
    """Orchestrates qualitative indoor air assessments and smart guidance."""

    # Backward-compatible alias delegating to shared core utility
    _sanitize_json_text = staticmethod(sanitize_json_output)

    @classmethod
    def evaluate_indoor_air(cls, request: IndoorAssessmentRequest) -> IndoorAssessmentResponse:
        """
        Main entry point for indoor air quality assessment:
        1. Ingests ambient CPCB outdoor data for infiltration context.
        2. Computes qualitative risk score from household factors.
        3. Attempts structured generation via Google Gemini API if key is present.
        4. Gracefully falls back to calibrated domain expert rules on missing key or API limits.
        """
        provider = get_active_aqi_provider()
        outdoor_aqi_data: CurrentAqiResponse = provider.get_current_aqi(request.station_id)

        household = request.household or HouseholdInput()
        language = "hi" if request.language.lower() == "hi" else "en"

        # Attempt Gemini AI generation if key is configured
        if settings.GEMINI_API_KEY:
            try:
                gemini_res = cls._call_gemini_api(outdoor_aqi_data, household, language)
                if gemini_res:
                    return gemini_res
            except Exception as e:
                logger.warning(f"Gemini indoor evaluation failed: {e}. Switching to expert rule fallback.")

        # Expert rule-based fallback
        return cls._generate_expert_rule_assessment(outdoor_aqi_data, household, language)

    @classmethod
    def _call_gemini_api(
        cls,
        outdoor: CurrentAqiResponse,
        household: HouseholdInput,
        language: str,
    ) -> Optional[IndoorAssessmentResponse]:
        """Calls Google GenAI Interactions API requesting strict structured JSON."""
        prompt = cls._build_gemini_prompt(outdoor, household, language)

        try:
            raw_text = generate_gemini_text(prompt)
            if not raw_text or not raw_text.strip():
                return None

            clean_json = sanitize_json_output(raw_text)
            parsed = json.loads(clean_json)

            if not isinstance(parsed, dict):
                return None

            # Inject verified outdoor provenance and disclosure
            parsed["station_id"] = outdoor.station.id
            parsed["station_name"] = outdoor.station.name
            parsed["city"] = outdoor.station.city
            parsed["outdoor_aqi"] = outdoor.aqi
            parsed["outdoor_category"] = outdoor.category.value
            parsed["outdoor_is_demo"] = outdoor.is_demo_data
            parsed["outdoor_data_source"] = outdoor.data_source
            parsed["outdoor_observed_at"] = outdoor.last_updated.isoformat()
            parsed["language"] = language
            parsed["ai_provider"] = "google-gemini"
            parsed["ai_generated"] = True
            parsed["has_connected_indoor_sensor"] = False
            parsed["generated_at"] = datetime.now(timezone.utc).isoformat()

            parsed["sensor_notice"] = (
                "सेंसर प्रकटीकरण: यह मूल्यांकन आपकी घरेलू आदतों और बाहरी CPCB प्रदूषण के आधार पर एक अनुमानित गुणात्मक जोखिम विश्लेषण है। बिना प्रमाणित इनडोर सेंसर के वास्तविक इनडोर AQI संख्या प्रदर्शित नहीं की जाती है।"
                if language == "hi"
                else "Sensor Disclosure: This qualitative risk evaluation is modeled from reported household practices and outdoor CPCB ambient infiltration. Without physical in-situ air sensors, AirSaathi AI never fabricates synthetic indoor AQI numbers."
            )

            parsed["disclaimer"] = (
                "चिकित्सीय अस्वीकरण: यह इनडोर वायु सहायक जोखिम न्यूनीकरण सुझाव प्रदान करता है, बीमारी का निदान या उपचार नहीं। HEPA प्यूरीफायर या N95 मास्क 100% सुरक्षा की गारंटी नहीं देते।"
                if language == "hi"
                else "Medical Disclaimer: This indoor air assistant provides environmental hazard reduction guidance, not medical diagnosis or treatment. Air purifiers and N95 masks reduce particulate mass but do not provide absolute immunity."
            )

            return IndoorAssessmentResponse.model_validate(parsed)
        except Exception as e:
            logger.warning(f"Error parsing Gemini indoor response: {e}")
            return None

    @classmethod
    def _build_gemini_prompt(
        cls,
        outdoor: CurrentAqiResponse,
        household: HouseholdInput,
        language: str,
    ) -> str:
        """Constructs prompt for Gemini structured indoor evaluation."""
        lang_note = (
            "You MUST output all titles, advice, rationale, summaries, and checklists in natural, fluent Hindi (Devanagari script)."
            if language == "hi"
            else "You MUST output all text, advice, rationale, summaries, and checklists in fluent English."
        )

        return f"""You are the Lead Indoor Environmental Quality & Aerosol Scientist for AirSaathi AI.
Perform a qualitative household air risk evaluation and generate room-wise recommendations based on reported household practices and ambient CPCB telemetry.

OUTDOOR AMBIENT CONTEXT:
- Station: {outdoor.station.name}, {outdoor.station.city}
- Outdoor AQI: {outdoor.aqi} ({outdoor.category.value})
- Prominent Pollutant: {outdoor.prominent_pollutant}
- Data Provenance: {outdoor.data_source} (Demo: {outdoor.is_demo_data})

HOUSEHOLD REPORTED PARAMETERS:
- Room Type: {household.room_type.value}
- Room Area: {household.room_area_sqft} sq ft (Ceiling: {household.ceiling_height_ft} ft)
- Cooking Fuel: {household.cooking_fuel.value}
- Heavy Frying / Tadka: {household.heavy_frying_or_tadka}
- Kitchen Chimney: {household.has_kitchen_chimney}
- Kitchen Exhaust Fan: {household.has_kitchen_exhaust}
- Ventilation Habits: {household.ventilation_status.value}
- Cleaning Method: {household.cleaning_method.value}
- Incense / Agarbatti / Dhoop / Coil: {household.burns_agarbatti_or_dhoop}
- Pets: {household.has_pets}
- Indoor Smoking: {household.indoor_smoking}
- Air Purifier Present: {household.has_air_purifier} (True HEPA: {household.purifier_has_hepa})

CRITICAL SCIENTIFIC & SAFETY PRINCIPLES:
1. NO FABRICATED INDOOR AQI: Do NOT invent numerical indoor AQI readings. Provide a qualitative risk rating (Low, Moderate, High, Severe) and a composite risk score (0-100).
2. NO INDOOR PLANT SUBSTITUTE: Explicitly debunk the myth that potted plants can clean high indoor PM2.5 or VOCs in real homes. Plants cannot replace mechanical HEPA air filtration.
3. INDIAN COOKING DYNAMICS: Tadka and deep frying generate immense PM2.5 spikes (>500 µg/m³) and acrolein. Mandate running exhaust/chimney 2 minutes before and 5 minutes after cooking.
4. VENTILATION TIMING: Do NOT invent universally safe window times. In Severe/Very Poor outdoor AQI, windows should remain sealed except for a brief 10-15 min midday flush during peak boundary layer dispersion.
5. CADR REQUIREMENT: Calculate minimum CADR for the room area based on 4.5 Air Changes per Hour (ACH) for smog season.

{lang_note}

Output a strictly valid JSON object matching this schema:
{{
  "qualitative_risk": "Low | Moderate | High | Severe",
  "risk_score_numeric": 65,
  "risk_summary": "string",
  "ventilation": {{
    "action": "Seal | Restrict | Open",
    "optimal_window": "string (e.g. 01:00 PM - 02:30 PM)",
    "duration_minutes": 15,
    "rationale": "string",
    "precautions": ["string", "string"]
  }},
  "purifier_guidance": {{
    "room_area_sqft": {household.room_area_sqft},
    "recommended_min_cadr_m3h": 250,
    "recommended_min_cadr_cfm": 150,
    "target_ach": 4.5,
    "filter_type_guidance": "string",
    "placement_tips": ["string", "string"],
    "maintenance_schedule": "string"
  }},
  "kitchen_guidance": {{
    "risk_summary": "string",
    "chimney_exhaust_guidance": "string",
    "cooking_habits_advice": ["string", "string"],
    "combustion_safety": "string"
  }},
  "room_recommendations": {{
    "bedroom": {{
      "room_name": "Bedroom",
      "primary_threats": ["string"],
      "immediate_actions": ["string"],
      "night_protocol": "string",
      "lifestyle_adjustments": ["string"]
    }},
    "kitchen": {{
      "room_name": "Kitchen",
      "primary_threats": ["string"],
      "immediate_actions": ["string"],
      "night_protocol": null,
      "lifestyle_adjustments": ["string"]
    }},
    "living_room": {{
      "room_name": "Living Room",
      "primary_threats": ["string"],
      "immediate_actions": ["string"],
      "night_protocol": null,
      "lifestyle_adjustments": ["string"]
    }},
    "childrens_room": {{
      "room_name": "Children's Room",
      "primary_threats": ["string"],
      "immediate_actions": ["string"],
      "night_protocol": "string",
      "lifestyle_adjustments": ["string"]
    }},
    "study_room": {{
      "room_name": "Study Room",
      "primary_threats": ["string"],
      "immediate_actions": ["string"],
      "night_protocol": null,
      "lifestyle_adjustments": ["string"]
    }}
  }},
  "actionable_checklist": ["string", "string", "string", "string"],
  "plant_myth_clarification": "string"
}}"""

    @classmethod
    def _generate_expert_rule_assessment(
        cls,
        outdoor: CurrentAqiResponse,
        household: HouseholdInput,
        language: str,
    ) -> IndoorAssessmentResponse:
        """
        Calibrated expert rule-based fallback engine implementing real-world
        indoor aerosol physics and CPCB guidelines in both English and Hindi.
        """
        hi = language == "hi"

        # 1. Compute Qualitative Risk Score (0 - 100)
        risk_score = 20  # Base baseline

        # Outdoor infiltration influence
        if outdoor.aqi > 400:
            risk_score += 25
        elif outdoor.aqi > 300:
            risk_score += 18
        elif outdoor.aqi > 200:
            risk_score += 12

        # Infiltration multiplier if windows left open in smog
        if outdoor.aqi > 200 and household.ventilation_status == VentilationStatus.CONTINUOUS_OPEN:
            risk_score += 20

        # Indoor emission factors
        if household.indoor_smoking:
            risk_score += 35
        if household.burns_agarbatti_or_dhoop:
            risk_score += 20
        if household.heavy_frying_or_tadka and not household.has_kitchen_chimney and not household.has_kitchen_exhaust:
            risk_score += 25
        elif household.heavy_frying_or_tadka and (household.has_kitchen_chimney or household.has_kitchen_exhaust):
            risk_score += 10

        if household.cleaning_method == "dry_broom":
            risk_score += 10
        if household.has_pets:
            risk_score += 8

        # Protective mitigations
        if household.has_air_purifier and household.purifier_has_hepa:
            risk_score -= 28
        elif household.has_air_purifier and not household.purifier_has_hepa:
            risk_score -= 8

        # Bound score between 5 and 98
        risk_score = max(5, min(98, risk_score))

        if risk_score >= 75:
            qualitative_risk = QualitativeRiskLevel.SEVERE
        elif risk_score >= 50:
            qualitative_risk = QualitativeRiskLevel.HIGH
        elif risk_score >= 25:
            qualitative_risk = QualitativeRiskLevel.MODERATE
        else:
            qualitative_risk = QualitativeRiskLevel.LOW

        # Risk summary description
        if hi:
            if qualitative_risk == QualitativeRiskLevel.SEVERE:
                risk_summary = "गंभीर इनडोर प्रदूषण जोखिम: इनडोर धुआं (अगरबत्ती/तड़का/धूम्रपान) और बाहरी स्मॉग के रिसाव से इनडोर हवा अत्यंत दूषित हो सकती है।"
            elif qualitative_risk == QualitativeRiskLevel.HIGH:
                risk_summary = "उच्च इनडोर जोखिम: रसोई का धुआं और बाहरी प्रदूषकों का प्रवेश श्वसन तंत्र पर प्रतिकूल प्रभाव डाल सकता है।"
            elif qualitative_risk == QualitativeRiskLevel.MODERATE:
                risk_summary = "मध्यम जोखिम: सामान्य इनडोर प्रदूषण है जिसे रसोई वेंटिलेशन और नम पोछा लगाकर काफी कम किया जा सकता है।"
            else:
                risk_summary = "संतोषजनक इनडोर स्थिति: वर्तमान आदतें इनडोर वायु प्रदूषण को न्यूनतम रखने में सहायक हैं।"
        else:
            if qualitative_risk == QualitativeRiskLevel.SEVERE:
                risk_summary = "Severe Indoor Risk: A combination of heavy internal emission sources (incense/cooking/smoke) and ambient smog infiltration creates high particulate accumulation."
            elif qualitative_risk == QualitativeRiskLevel.HIGH:
                risk_summary = "High Indoor Risk: Inadequate kitchen extraction combined with ambient particulate infiltration is stressing indoor air quality."
            elif qualitative_risk == QualitativeRiskLevel.MODERATE:
                risk_summary = "Moderate Indoor Risk: Noticeable indoor particulate sources present; manageable with disciplined ventilation and wet cleaning."
            else:
                risk_summary = "Low Indoor Risk: Sound mitigation practices and air filtration keep indoor particulate accumulation minimal."

        # 2. Sizing CADR (Clean Air Delivery Rate)
        # Volume in m³ = Area (sq ft) * Height (ft) * 0.0283168
        volume_m3 = household.room_area_sqft * household.ceiling_height_ft * 0.0283168
        target_ach = 4.5  # 4.5 ACH during winter smog
        cadr_m3h = int(volume_m3 * target_ach)
        cadr_cfm = int(cadr_m3h / 1.699)

        purifier_guidance = CadrRecommendation(
            room_area_sqft=household.room_area_sqft,
            recommended_min_cadr_m3h=cadr_m3h,
            recommended_min_cadr_cfm=cadr_cfm,
            target_ach=target_ach,
            filter_type_guidance=(
                "सत्य HEPA H13/H14 प्रमाणित फिल्टर चुनें जो 0.3 माइक्रोन के 99.97% कण रोकता है। ओजोन या आयनाइज़र वाले प्यूरीफायर से बचें।"
                if hi
                else "Select certified True HEPA (H13/H14) capable of capturing 99.97% of particles down to 0.3 microns. Avoid standalone ionizers or ozone-generating electronic precipitators."
            ),
            placement_tips=[
                "दीवार और पर्दों से कम से कम 1.5 से 2 फीट दूर रखें" if hi else "Position at least 1.5 - 2 feet away from walls and heavy drapery",
                "कमरे के केंद्र में खुली हवा के प्रवाह की दिशा में रखें" if hi else "Orient towards central living breathing zone for unhindered airflow",
                "खिड़की के ठीक नीचे न रखें ताकि साफ हवा बाहर न जाए" if hi else "Avoid placing directly beneath drafty windows to prevent clean air leakage",
                "कमरे के दरवाजे व खिड़कियां बंद रखकर चलाएं" if hi else "Keep doors and external windows closed during operation",
            ],
            maintenance_schedule=(
                "शीतकालीन स्मॉग में प्री-फिल्टर को हर 2-3 सप्ताह में वैक्यूम या धोएं। मुख्य HEPA फिल्टर को 6 से 12 महीने में बदलें।"
                if hi
                else "Vacuum or wash external mesh pre-filter every 2-3 weeks in winter smog. Replace the main True HEPA core every 6 to 12 months."
            ),
        )

        # 3. Smart Ventilation Advice
        if outdoor.aqi > 300:
            ventilation = VentilationAdvice(
                action="Seal / Restrict" if not hi else "खिड़कियां बंद रखें (सीमित वेंटिलेशन)",
                optimal_window="01:30 PM - 02:30 PM" if not hi else "दोपहर 01:30 बजे से 02:30 बजे",
                duration_minutes=15,
                rationale=(
                    "दोपहर के समय सौर ताप से वायुमंडल की बाउंड्री लेयर ऊपर उठती है जिससे स्मॉग सबसे कम होता है। केवल 15 मिनट का क्रॉस-वेंटिलेशन करें।"
                    if hi
                    else "Solar convective heating raises the planetary boundary layer during mid-afternoon. Limit window opening to a brief 15-minute flush."
                ),
                precautions=[
                    "सुबह 5 से 10 बजे के बीच खिड़की बिल्कुल न खोलें" if hi else "Keep all windows sealed tight between 5:00 AM and 10:00 AM",
                    "वेंटिलेशन के तुरंत बाद खिड़की बंद कर प्यूरीफायर तेज करें" if hi else "Close windows promptly after flush and boost purifier speed for 20 mins",
                ],
            )
        else:
            ventilation = VentilationAdvice(
                action="Controlled Cross-Ventilation" if not hi else "नियंत्रित क्रॉस-वेंटिलेशन",
                optimal_window="12:00 PM - 03:30 PM" if not hi else "दोपहर 12:00 बजे से 03:30 बजे",
                duration_minutes=30,
                rationale=(
                    "मध्यम बाहरी वायु में दोपहर की ताजा हवा कमरे की बंद CO2 और गंध को बाहर निकालने के लिए सुरक्षित है।"
                    if hi
                    else "Moderate outdoor levels allow safe cross-aeration during afternoon dispersion hours to vent indoor CO2 and moisture."
                ),
                precautions=[
                    "ट्रैफिक पीक आवर्स (शाम 6-8 बजे) में खिड़कियां बंद रखें" if hi else "Close windows before evening rush hour (6:00 PM - 8:00 PM)",
                ],
            )

        # 4. Kitchen Guidance
        kitchen_guidance = KitchenGuidance(
            risk_summary=(
                "भारतीय तड़का और डीप फ्राइंग से PM2.5 का स्तर 500 µg/m³ के पार जा सकता है। एलपीजी स्टोव से NO2 और कार्बन मोनोऑक्साइड भी निकलती है।"
                if hi
                else "Indian spices, dry chili tempering (tadka) and high-heat frying cause rapid indoor PM2.5 spikes exceeding 500 µg/m³, alongside NO2 and CO from gas stoves."
            ),
            chimney_exhaust_guidance=(
                "गैस जलाने से 2 मिनट पहले चिमनी/एग्जॉस्ट फैन चालू करें ताकि हवा का खिंचाव बन सके, और खाना पकने के 5 मिनट बाद तक चालू रखें।"
                if hi
                else "Turn on kitchen chimney or exhaust fan 2 minutes BEFORE lighting the stove to establish negative draft, and keep it running for 5 minutes post-cooking."
            ),
            cooking_habits_advice=[
                "तड़के और छौंक के समय पैन पर ढक्कन या स्प्लैटर स्क्रीन लगाएं" if hi else "Cover pans with lids or splatter mesh during tempering/chili frying",
                "रसोई का दरवाजा अन्य कमरों से अलग रखें ताकि धुआं शयनकक्ष में न जाए" if hi else "Keep kitchen door closed to isolate cooking aerosols from bedrooms",
                "संभव हो तो इंडक्शन कुकटॉप का उपयोग करें" if hi else "Consider induction cooktops to eliminate gas combustion by-products",
            ],
            combustion_safety=(
                "गैस स्टोव की लौ हमेशा नीली होनी चाहिए। पीली लौ अपूर्ण दहन और कार्बन मोनोऑक्साइड उत्सर्जन का संकेत है।"
                if hi
                else "Ensure gas burner produces crisp blue flame. A yellow or orange flame signals incomplete combustion and toxic carbon monoxide release."
            ),
        )

        # 5. Room-Specific Recommendations
        room_recommendations: Dict[str, RoomSpecificRecommendation] = {
            "bedroom": RoomSpecificRecommendation(
                room_name="शयनकक्ष (Bedroom)" if hi else "Bedroom",
                primary_threats=[
                    "बिस्तर के धूल कण (Dust Mites)" if hi else "Dust mites & settled bedding particulates",
                    "खिड़की व बालकनी से बाहरी स्मॉग का रिसाव" if hi else "Nighttime outdoor smog infiltration through gaps",
                    "अगरबत्ती व मच्छर क्वाइल का धुआं" if hi else "Mosquito coil / agarbatti aerosol entrapment",
                ],
                immediate_actions=[
                    "दरवाजे के नीचे ड्राफ्ट स्टॉपर या कपड़ा लगाएं" if hi else "Install door draft stoppers to block living room corridor air",
                    "सोते समय खिड़की पूरी तरह बंद रखें" if hi else "Keep windows locked shut throughout sleep hours",
                    "धूप में गद्दों और चादरों को सुखाएं" if hi else "Sun-dry bedding and wash linens in warm water weekly",
                ],
                night_protocol=(
                    "सोने से 30 मिनट पहले एयर प्यूरीफायर को 'ऑटो' या 'स्लीप' मोड पर चालू करें ताकि 8 घंटे स्वच्छ हवा मिले।"
                    if hi
                    else "Power on HEPA purifier 30 minutes before bedtime on sleep/auto mode for 8 hours of clean respiratory recovery."
                ),
                lifestyle_adjustments=[
                    "कमरे में अगरबत्ती या मच्छर क्वाइल बिल्कुल न जलाएं" if hi else "Never burn mosquito coils or incense sticks in sleeping quarters",
                ],
            ),
            "kitchen": RoomSpecificRecommendation(
                room_name="रसोईघर (Kitchen)" if hi else "Kitchen",
                primary_threats=[
                    "तड़के और तेल का धुआं (PM2.5 > 500 µg/m³)" if hi else "Ultra-fine cooking aerosols from oil & chili tempering",
                    "एलपीजी दहन से NO2 व CO गैस" if hi else "Combustion gases (NO2, CO) from unvented burners",
                ],
                immediate_actions=[
                    "खाना बनाते समय चिमनी का पूरा उपयोग करें" if hi else "Run ducted chimney on medium/high speed during all frying",
                    "रसोई की खिड़की को क्रॉस-वेंटिलेशन के लिए खुला रखें" if hi else "Ensure direct exhaust to outdoor duct without recirculation",
                ],
                night_protocol=None,
                lifestyle_adjustments=[
                    "तड़के के दौरान पैन को ढंक कर रखें" if hi else "Cover hot oil vessels with splatter screens",
                ],
            ),
            "living_room": RoomSpecificRecommendation(
                room_name="लिविंग रूम (Living Room)" if hi else "Living Room",
                primary_threats=[
                    "मुख्य दरवाजे से जूतों की धूल और बाहरी प्रदूषण" if hi else "Tracked-in street dust, soot and heavy footfall re-suspension",
                    "धूपबत्ती और अगरबत्ती का धुआं" if hi else "Pooja corner incense smoke dispersing into seating areas",
                ],
                immediate_actions=[
                    "बाहर के जूते दरवाजे के बाहर ही उतारें" if hi else "Enforce a strict 'no outdoor shoes inside' entryway policy",
                    "सूखे झाड़ू की जगह गीला पोछा लगाएं" if hi else "Switch completely from dry brooms to microfiber wet mopping",
                ],
                night_protocol=None,
                lifestyle_adjustments=[
                    "अगरबत्ती की जगह इलेक्ट्रॉनिक दीया या आवश्यक तेल चुनें" if hi else "Substitute combustion incense with electric diffusers or brass lamps",
                ],
            ),
            "childrens_room": RoomSpecificRecommendation(
                room_name="बच्चों का कमरा (Children's Room)" if hi else "Children's Room",
                primary_threats=[
                    "कमरे में जमीन के करीब महीन धूल (बच्चे फर्श पर खेलते हैं)" if hi else "Ground-level particulate accumulation where toddlers play",
                    "कठोर रासायनिक क्लीनर और रूम फ्रेशनर" if hi else "Synthetic VOCs from aerosol air fresheners and harsh disinfectants",
                ],
                immediate_actions=[
                    "खिलौनों और फर्श को केवल पानी या सिरके से साफ करें" if hi else "Clean play mats with hypoallergenic damp microfiber",
                    "कमरे में प्यूरीफायर को बच्चे की पहुंच से सुरक्षित ऊंचाई पर रखें" if hi else "Place HEPA unit securely on stable surface with child-lock enabled",
                ],
                night_protocol=(
                    "रात भर प्यूरीफायर स्लीप मोड में चलाएं ताकि विकासशील फेफड़ों को शुद्ध हवा मिले।"
                    if hi
                    else "Continuous ultra-quiet sleep mode operation throughout nighttime sleep hours."
                ),
                lifestyle_adjustments=[
                    "कमरे में स्प्रे, डिओडोरेंट या रासायनिक रूम फ्रेशनर न छिड़कें" if hi else "Prohibit aerosol room fresheners and synthetic synthetic fragrances",
                ],
            ),
            "study_room": RoomSpecificRecommendation(
                room_name="अध्ययन कक्ष / होम ऑफिस (Study Room)" if hi else "Study Room / Home Office",
                primary_threats=[
                    "बंद कमरे में CO2 का उच्च स्तर (नींद और थकान)" if hi else "Carbon dioxide buildup causing cognitive fatigue and drowsiness",
                    "प्रिंटर और इलेक्ट्रॉनिक्स से ओजोन व टोनर धूल" if hi else "Ultrafine toner particles from laser printers",
                ],
                immediate_actions=[
                    "दोपहर के समय 10 मिनट के लिए दरवाजा खोलकर ताजा हवा लें" if hi else "Take 10-minute fresh air dilution breaks during mid-day",
                    "लेजर प्रिंटर को अध्ययन की मुख्य मेज से दूर रखें" if hi else "Isolate laser printers away from direct breathing workspace",
                ],
                night_protocol=None,
                lifestyle_adjustments=[
                    "पर्याप्त हाइड्रेशन और आंखों को नियमित धोएं" if hi else "Maintain ergonomic hydration and regular screen breaks",
                ],
            ),
        }

        # 6. Actionable Checklist
        if hi:
            actionable_checklist = [
                "सप्ताह में कम से कम 3 बार गीले माइक्रोफाइबर कपड़े से पोछा लगाएं (सूखी झाड़ू न लगाएं)",
                "तड़के और छौंक से 2 मिनट पहले रसोई का एग्जॉस्ट/चिमनी चालू करें",
                "घर के अंदर अगरबत्ती, धूप या मच्छर क्वाइल जलाने से बचें; इनकी जगह इलेक्ट्रॉनिक विकल्प चुनें",
                "शयनकक्ष में HEPA H13 एयर प्यूरीफायर को रात भर ऑटो मोड पर चलाएं",
                "सुबह के स्मॉग के दौरान खिड़कियां बंद रखें; दोपहर 1:30 बजे केवल 15 मिनट वेंटिलेशन करें",
            ]
        else:
            actionable_checklist = [
                "Switch exclusively to damp microfiber mopping (dry brooms re-suspend hazardous PM10 into the breathing zone)",
                "Turn on kitchen chimney or exhaust fan 2 minutes before cooking begins and maintain for 5 minutes after",
                "Eliminate daily burning of incense sticks (agarbatti), dhoop, and mosquito coils in enclosed living spaces",
                "Operate True HEPA (H13) air purifier in bedrooms throughout sleep hours with doors closed",
                "Seal windows during cold morning smog; limit fresh air ventilation to a 15-minute midday window",
            ]

        # 7. Plant Myth Clarification
        plant_myth = (
            "वैज्ञानिक स्पष्टीकरण (पौधों का मिथक): नासा के 1989 के अध्ययन का हवाला देकर अक्सर इनडोर पौधों को एयर प्यूरीफायर का विकल्प बताया जाता है। हालांकि, वास्तविक घरों में हवा का आदान-प्रदान पौधों की शोधन क्षमता से 100 गुना अधिक होता है। पौधे सुंदर हैं और मानसिक शांति देते हैं, परंतु वे भारी PM2.5, NO2 या तड़के के धुएं को साफ नहीं कर सकते। इसके लिए प्रमाणित HEPA फिल्टर और एग्जॉस्ट ही आवश्यक हैं।"
            if hi
            else "Scientific Clarification on Indoor Plants: Potted plants (such as Snake Plants or Areca Palms) are often marketed as natural air purifiers citing the 1989 NASA Clean Air Study. However, real-world residential air exchange rates overpower plant phytoremediation by more than 100-fold. While plants enhance biophilic wellness, they cannot filter hazardous PM2.5 particulates, combustion soot, or toxic gases. They cannot replace mechanical True HEPA filtration or kitchen exhaust systems."
        )

        # 8. Sensor Notice & Medical Disclaimer
        sensor_notice = (
            "सेंसर प्रकटीकरण: यह मूल्यांकन आपकी घरेलू आदतों और बाहरी CPCB प्रदूषण के आधार पर एक अनुमानित गुणात्मक जोखिम विश्लेषण है। बिना प्रमाणित इनडोर सेंसर के वास्तविक इनडोर AQI संख्या प्रदर्शित नहीं की जाती है।"
            if hi
            else "Sensor Disclosure: This qualitative risk evaluation is modeled from reported household practices and outdoor CPCB ambient infiltration. Without physical in-situ air sensors, AirSaathi AI never fabricates synthetic indoor AQI numbers."
        )

        disclaimer = (
            "चिकित्सीय अस्वीकरण: यह इनडोर वायु सहायक केवल पर्यावरणीय जोखिम न्यूनीकरण सुझाव प्रदान करता है, बीमारी का निदान या उपचार नहीं। HEPA प्यूरीफायर या N95 मास्क 100% सुरक्षा की गारंटी नहीं देते। किसी भी स्वास्थ्य समस्या में अपने चिकित्सक से परामर्श लें।"
            if hi
            else "Medical Disclaimer: This indoor air assistant provides environmental hazard reduction guidance, not medical diagnosis or treatment. Air purifiers and N95 masks reduce particulate mass but do not provide absolute immunity. Consult a qualified physician for clinical care."
        )

        return IndoorAssessmentResponse(
            station_id=outdoor.station.id,
            station_name=outdoor.station.name,
            city=outdoor.station.city,
            outdoor_aqi=outdoor.aqi,
            outdoor_category=outdoor.category.value,
            outdoor_is_demo=outdoor.is_demo_data,
            outdoor_data_source=outdoor.data_source,
            outdoor_observed_at=outdoor.last_updated,
            language=language,
            ai_provider="expert-rules-fallback",
            ai_generated=False,
            has_connected_indoor_sensor=False,
            qualitative_risk=qualitative_risk,
            risk_score_numeric=risk_score,
            risk_summary=risk_summary,
            sensor_notice=sensor_notice,
            ventilation=ventilation,
            purifier_guidance=purifier_guidance,
            kitchen_guidance=kitchen_guidance,
            room_recommendations=room_recommendations,
            actionable_checklist=actionable_checklist,
            plant_myth_clarification=plant_myth,
            disclaimer=disclaimer,
            generated_at=datetime.now(timezone.utc),
        )
