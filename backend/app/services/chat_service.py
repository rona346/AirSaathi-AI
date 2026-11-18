"""AirSaathi AI - Gemini-Powered Environmental Chatbot Service.

Provides context-aware, bilingual conversational intelligence on urban air pollution,
health protection, indoor air quality, and sustainable living.
Integrates live CPCB telemetry, routine planning context, and household safeguards
with strict zero-hallucination and medical safety guardrails.
"""

import json
import logging
import re
from datetime import datetime
from typing import Any, Dict, List, Optional
import httpx

from backend.app.core.config import settings
from backend.app.models.aqi import CurrentAqiResponse
from backend.app.models.chat import (
    ChatContextInfo,
    ChatMessage,
    ChatRequest,
    ChatResponse,
    ChatRole,
)
from backend.app.models.indoor import HouseholdInput
from backend.app.models.routine import FamilyVulnerabilityInput
from backend.app.services.live_aqi_provider import get_active_aqi_provider

logger = logging.getLogger(__name__)


class ChatService:
    """Orchestrates bilingual, context-aware environmental conversational intelligence."""

    @classmethod
    def process_chat_message(cls, request: ChatRequest) -> ChatResponse:
        """
        Process a user's conversational message:
        1. Queries verified CPCB telemetry for real-time station context.
        2. Ingests family vulnerability profile and household habits if available.
        3. Attempts structured generation via Google Gemini API if key is configured.
        4. Smoothly falls back to the domain expert chatbot engine on errors or missing key.
        """
        provider = get_active_aqi_provider()
        outdoor_aqi: CurrentAqiResponse = provider.get_current_aqi(request.station_id)

        language = "hi" if request.language.lower() == "hi" else "en"

        context_info = ChatContextInfo(
            station_id=outdoor_aqi.station.id,
            station_name=outdoor_aqi.station.name,
            city=outdoor_aqi.station.city,
            aqi=outdoor_aqi.aqi,
            category=outdoor_aqi.category.value,
            prominent_pollutant=outdoor_aqi.prominent_pollutant,
            is_demo_data=outdoor_aqi.is_demo_data,
            data_source=outdoor_aqi.data_source,
            observed_at=outdoor_aqi.last_updated,
        )

        # Attempt Gemini API if key is present
        if settings.GEMINI_API_KEY:
            try:
                gemini_res = cls._call_gemini_api(request, outdoor_aqi, context_info, language)
                if gemini_res:
                    return gemini_res
            except Exception as e:
                logger.warning(f"Gemini chat generation failed: {e}. Switching to expert fallback chatbot.")

        # Fallback to expert domain chatbot engine
        return cls._generate_expert_fallback(request, context_info, language)

    @classmethod
    def _call_gemini_api(
        cls,
        request: ChatRequest,
        outdoor: CurrentAqiResponse,
        context_info: ChatContextInfo,
        language: str,
    ) -> Optional[ChatResponse]:
        """Calls Google Gemini API with conversational history and ambient context."""
        model_id = getattr(settings, "GEMINI_MODEL_ID", "gemini-2.5-flash") or "gemini-2.5-flash"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:generateContent?key={settings.GEMINI_API_KEY}"
        headers = {"Content-Type": "application/json"}

        system_instruction = cls._build_system_instruction(outdoor, request.family_profile, request.household, language)

        # Convert bounded history (last 6 messages) into Gemini contents format
        contents = []
        bounded_history = request.history[-6:] if request.history else []

        # First user message includes system context
        is_first = True
        for msg in bounded_history:
            role = "model" if msg.role == ChatRole.ASSISTANT else "user"
            content_text = msg.content
            if is_first and role == "user":
                content_text = f"{system_instruction}\n\nUser: {content_text}"
                is_first = False
            contents.append({
                "role": role,
                "parts": [{"text": content_text}],
            })

        # Append current user message
        current_text = request.message
        if is_first:
            current_text = f"{system_instruction}\n\nUser: {current_text}"

        contents.append({
            "role": "user",
            "parts": [{"text": current_text}],
        })

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": 0.4,
                "maxOutputTokens": 1024,
            },
        }

        try:
            with httpx.Client(timeout=15.0) as client:
                res = client.post(url, json=payload, headers=headers)
                if res.status_code != 200:
                    logger.warning(f"Gemini Chat returned HTTP {res.status_code}: {res.text[:200]}")
                    return None

                data = res.json()
                candidates = data.get("candidates", [])
                if not candidates:
                    return None

                # Extract text across parts (handling reasoning/thinking parts)
                raw_text = ""
                for part in candidates[0].get("content", {}).get("parts", []):
                    if isinstance(part, dict) and "text" in part and part["text"]:
                        raw_text += part["text"]

                raw_text = raw_text.strip()
                if not raw_text:
                    return None

                # Generate follow-up suggestions
                followups = cls._generate_followups(request.message, language)

                disclaimer = (
                    "चिकित्सीय अस्वीकरण: यह चैटबॉट केवल पर्यावरणीय स्वास्थ्य जानकारी व जोखिम न्यूनीकरण सुझाव प्रदान करता है, चिकित्सीय परामर्श या बीमारी का उपचार नहीं। व्यक्तिगत स्वास्थ्य चिंताओं के लिए चिकित्सक से परामर्श लें।"
                    if language == "hi"
                    else "Medical Disclaimer: This assistant provides environmental health guidance and exposure reduction advice, not medical diagnosis or treatment. Sensitive individuals and patients should consult their physician."
                )

                return ChatResponse(
                    message=raw_text,
                    language=language,
                    ai_provider="google-gemini",
                    ai_generated=True,
                    context_used=context_info,
                    suggested_followups=followups,
                    disclaimer=disclaimer,
                    timestamp=datetime.utcnow(),
                )
        except Exception as e:
            logger.warning(f"Error calling Gemini Chat: {e}")
            return None

    @classmethod
    def _build_system_instruction(
        cls,
        outdoor: CurrentAqiResponse,
        family: Optional[FamilyVulnerabilityInput],
        household: Optional[HouseholdInput],
        language: str,
    ) -> str:
        """Constructs system instructions incorporating CPCB context and domain safety rules."""
        pollutants_str = ", ".join([f"{k}: {v.value} {v.unit}" for k, v in outdoor.pollutants.items()])
        demo_str = "Demonstration Baseline Data" if outdoor.is_demo_data else "Live CPCB CAAQMS Feed"

        fam_str = "Standard Healthy Adults"
        if family:
            fam_flags = []
            if family.has_children: fam_flags.append("Children (<12 yrs)")
            if family.has_seniors: fam_flags.append("Seniors (60+ yrs)")
            if family.has_respiratory_condition: fam_flags.append("Asthma/Respiratory Patients")
            if family.is_pregnant: fam_flags.append("Pregnant Member")
            if fam_flags: fam_str = ", ".join(fam_flags)

        lang_instr = (
            "You MUST reply in fluent, natural Hindi using Devanagari script. Use clear, compassionate language."
            if language == "hi"
            else "You MUST reply in fluent, clear English formatted with standard Markdown."
        )

        return f"""You are AirSaathi AI, a certified Environmental Health, Urban Meteorology, and Aerosol Assistant.

CURRENT AMBIENT CONTEXT:
- Station: {outdoor.station.name}, {outdoor.station.city}
- AQI: {outdoor.aqi} ({outdoor.category.value})
- Prominent Pollutant: {outdoor.prominent_pollutant}
- Pollutant Readings: {pollutants_str}
- Source: {outdoor.data_source} ({demo_str})
- Last Updated: {outdoor.last_updated}
- Family Sensitivity Profile: {fam_str}

CRITICAL RULES:
1. Always preserve verified data provenance. Whenever discussing AQI, state the exact station ({outdoor.station.name}), AQI value ({outdoor.aqi}), category ({outdoor.category.value}), and observation time ({outdoor.last_updated}).
2. NEVER claim demonstration data is live data. If is_demo_data is true, state that it represents a calibrated baseline.
3. NO MEDICAL DIAGNOSIS: Provide exposure reduction guidance, never medical treatment or disease diagnosis.
4. INDOOR PLANTS MYTH: Clarify that potted plants cannot replace mechanical True HEPA air purifiers or kitchen exhaust.
5. NO FABRICATED LOCAL INFORMATION: Never invent local facilities or fake transit lines.
6. NO 100% IMMUNITY CLAIMS: Air purifiers and N95 masks reduce particulate mass but do not provide complete health guarantees.

{lang_instr}"""

    @classmethod
    def _generate_expert_fallback(
        cls,
        request: ChatRequest,
        context: ChatContextInfo,
        language: str,
    ) -> ChatResponse:
        """
        Calibrated domain expert fallback engine that recognizes intent keywords
        and provides scientifically accurate answers in both English and Hindi.
        """
        hi = language == "hi"
        query = request.message.lower()

        station_ctx_en = f"**Current Ambient Context:** At **{context.station_name} ({context.city})**, the AQI is **{context.aqi} ({context.category})** with prominent pollutant **{context.prominent_pollutant}** (Observed: {context.observed_at.strftime('%d %b %Y, %I:%M %p')}; Source: {context.data_source} - {'Demo Mode' if context.is_demo_data else 'Live CPCB'})."
        station_ctx_hi = f"**वर्तमान परिवेश संदर्भ:** **{context.station_name} ({context.city})** पर वायु गुणवत्ता सूचकांक **{context.aqi} ({context.category})** है, जिसमें मुख्य प्रदूषक **{context.prominent_pollutant}** है (अवलोकन समय: {context.observed_at.strftime('%d %b %Y, %I:%M %p')}; स्रोत: {context.data_source} - {'डेमो मोड' if context.is_demo_data else 'CPCB लाइव'})."

        # 1. Intent: What is PM2.5 / PM10 / Pollutants
        if any(w in query for w in ["pm2.5", "pm10", "particulate", "प्रदूषक", "पीएम2.5", "पीएम10"]):
            if hi:
                reply = f"""{station_ctx_hi}

### PM2.5 एवं PM10 क्या हैं?

- **PM2.5 (अति-सूक्ष्म कण):** ये 2.5 माइक्रोन या उससे छोटे सूक्ष्म कण होते हैं (मानव बाल की मोटाई से 30 गुना पतले)। ये फेफड़ों की गहराई (एल्वियोली) और रक्तप्रवाह में प्रवेश कर सकते हैं। इनके मुख्य स्रोत वाहनों का धुआं, बायोमास/पराली दहन और औद्योगिक उत्सर्जन हैं।
- **PM10 (श्वसनीय कण):** 10 माइक्रोन तक के कण होते हैं, जिनमें मुख्य रूप से सड़क की धूल, निर्माण धूल और परागकण शामिल हैं।

**सुरक्षा उपाय:**
- बाहर निकलने पर प्रमाणित **N95 / KF94** मास्क का उपयोग करें।
- शयनकक्ष में **True HEPA (H13)** एयर प्यूरीफायर चलाएं।"""
            else:
                reply = f"""{station_ctx_en}

### Understanding PM2.5 and PM10 Particulates

- **PM2.5 (Fine Respirable Particulates):** Airborne particles <= 2.5 µm in aerodynamic diameter (roughly 30 times smaller than the width of a human hair). Because of their microscopic size, they bypass upper nasal cilia, penetrating deep into the pulmonary alveoli and crossing into the bloodstream. Major sources include combustion engines, stubble burning, and secondary sulfate/nitrate aerosols.
- **PM10 (Inhalable Coarse Particulates):** Particles up to 10 µm, primarily consisting of road dust, construction fly ash, and mechanical wear particles.

**Protective Measures:**
- Wear a certified, well-fitted **N95/KF94** respirator outdoors.
- Run a certified **True HEPA (H13)** purifier in sleeping quarters to remove >= 99.97% of particles down to 0.3 µm."""

        # 2. Intent: Protecting children / schools / pediatric care
        elif any(w in query for w in ["child", "kid", "baby", "infant", "school", "बच्च", "स्कूल", "शिशु"]):
            if hi:
                reply = f"""{station_ctx_hi}

### स्मॉग में बच्चों की सुरक्षा के लिए मुख्य दिशा-निर्देश:

1. **शारीरिक संवेदनशीलता:** बच्चे प्रति किलोग्राम शारीरिक वजन वयस्कों की तुलना में लगभग **50% अधिक हवा** अंदर खींचते हैं, और उनके फेफड़े विकासशील अवस्था में होते हैं।
2. **स्कूल आवागमन:** बच्चों के लिए बाल-अनुकूल प्रमाणित N95 मास्क अनिवार्य करें। स्कूल वैन या बस की खिड़कियां बंद रखें और खुले तिपहिया वाहनों से बचें।
3. **आउटडोर गतिविधियां:** अत्यधिक प्रदूषण (AQI > 300) के दौरान सुबह की आउटडोर असेंबली व खेलकूद स्थगित रखें; इनडोर पहेलियां और खेल खेलें।
4. **सफाई व स्वच्छता:** स्कूल से लौटने पर चेहरा, आंखें और हाथ गुनगुने पानी से धोएं और पर्याप्त तरल पदार्थ पिलाएं।"""
            else:
                reply = f"""{station_ctx_en}

### Protecting Children During Heavy Smog

1. **Physiological Vulnerability:** Children inhale ~50% more air per kilogram of body weight compared to adults, and their respiratory and immune systems are still developing.
2. **School Commute Safeguards:** Mandate certified, well-fitted pediatric N95/KF94 respirators during transit. Keep school bus/van windows tightly closed, and avoid open two-wheelers or e-rickshaws.
3. **Recess & Sports:** Request schools to suspend early morning outdoor assemblies and athletic drills when AQI exceeds $300$; substitute with indoor physical mobility activities.
4. **Post-Transit Hygiene:** Have children wash their face and rinse eyes with clean water upon returning home, and maintain regular hydration."""

        # 3. Intent: Exercise / Morning Walk / Jogging
        elif any(w in query for w in ["walk", "exercise", "jog", "run", "gym", "सैर", "वॉक", "कसरत", "व्यायाम", "दौड़"]):
            if hi:
                reply = f"""{station_ctx_hi}

### क्या आज बाहर सैर या कसरत करनी चाहिए?

- **वर्तमान स्थिति:** AQI **{context.aqi} ({context.category})** के स्तर पर सुबह बाहर दौड़ना, तेज चलना या एरोबिक व्यायाम करना **हानिकारक** हो सकता है।
- **कारण (थर्मल इनवर्जन):** सर्दियों में सुबह 5 से 9 बजे के बीच जमीनी तापमान व्युत्क्रमण के कारण प्रदूषण की सघन परत जमीन के करीब फंसी रहती है। तीव्र कसरत के दौरान फेफड़ों का वायु प्रवाह 10 गुना बढ़ जाता है।
- **सुरक्षित विकल्प:**
  - सुबह की सैर को घर के अंदर 20-30 मिनट के योगासन, स्ट्रेचिंग या ट्रेडमिल वॉक में बदलें।
  - यदि बाहर सैर करनी हो तो दोपहर 1 से 3 बजे के बीच करें जब धूप से प्रदूषण की परत ऊपर उठ चुकी हो।"""
            else:
                reply = f"""{station_ctx_en}

### Should You Exercise Outdoors Today?

- **Guidance:** Given the current AQI of **{context.aqi} ({context.category})**, outdoor running, brisk walking, or intense aerobic exertion is **strongly discouraged**.
- **Atmospheric Rationale (Thermal Inversion):** Winter morning hours (05:00 AM – 09:30 AM) trap fine particulate soot close to the ground beneath a cold air lid. Heavy exercise elevates pulmonary ventilation up to 10-fold, pulling toxic particles deep into alveolar lung tissues.
- **Actionable Alternatives:**
  - Shift workouts indoors: 30 minutes of gentle yoga, core bodyweight exercises, or treadmill walking in a HEPA-filtered room.
  - If outdoor walking is necessary, reschedule to mid-afternoon (01:00 PM – 03:00 PM) when solar convective heating raises the atmospheric boundary layer."""

        # 4. Intent: Indoor air / Air purifier / Plants / Kitchen
        elif any(w in query for w in ["indoor", "purifier", "plant", "kitchen", "chimney", "प्यूरीफायर", "इनडोर", "पौधे", "रसोई", "चिमनी"]):
            if hi:
                reply = f"""{station_ctx_hi}

### इनडोर वायु गुणवत्ता में सुधार के व्यावहारिक उपाय:

1. **HEPA प्यूरीफायर:** सत्य HEPA (H13) फिल्टर का उपयोग करें। कमरे के क्षेत्रफल के अनुसार पर्याप्त CADR वाला प्यूरीफायर चुनें। सोने के समय इसे शयनकक्ष में चलाएं।
2. **रसोई का तड़का व धुआं:** गैस जलाने से 2 मिनट पहले चिमनी/एग्जॉस्ट पंखा चालू करें और खाना पकने के 5 मिनट बाद तक चलाएं। तड़के के समय ढक्कन लगाएं।
3. **पौधों का मिथक:** वैज्ञानिक अध्ययनों के अनुसार इनडोर पौधे (जैसे स्नेक प्लांट) घर के वास्तविक प्रदूषण या PM2.5 को साफ नहीं कर सकते; ये यांत्रिक HEPA फिल्टर का विकल्प नहीं हैं।
4. **सफाई तकनीक:** सूखे झाड़ू से धूल फिर से हवा में उड़ती है; हमेशा गीले माइक्रोफाइबर कपड़े से पोछा लगाएं। अगरबत्ती या मच्छर क्वाइल न जलाएं।"""
            else:
                reply = f"""{station_ctx_en}

### Enhancing Indoor Air Quality

1. **HEPA Air Filtration:** Deploy a certified True HEPA (H13/H14) purifier sized to your room volume (target 4.5 Air Changes per Hour). Run continuously in sleeping quarters on sleep mode with doors closed.
2. **Kitchen Emission Protocol:** Indian tempering (tadka) produces indoor PM2.5 surges > 500 µg/m³. Turn on kitchen chimney/exhaust **2 minutes before** cooking and keep it on for **5 minutes after**.
3. **Potted Plant Myth:** Peer-reviewed atmospheric studies demonstrate that potted plants cannot overcome residential air exchange rates and cannot remove fine particulates or hazardous gases. They cannot replace mechanical HEPA filtration.
4. **Housekeeping:** Discontinue dry broom sweeping (which re-suspends settled PM10); switch exclusively to damp microfiber mopping. Avoid burning incense sticks (agarbatti) or mosquito coils indoors."""

        # 5. Intent: Today's AQI in simple Hindi / Explanation
        elif any(w in query for w in ["explain", "simple", "today", "hindi", "आज का", "सरल", "हिंदी"]):
            if hi:
                reply = f"""{station_ctx_hi}

### आज की वायु गुणवत्ता की सरल व्याख्या:

- **वर्तमान स्तर:** **{context.station_name}** पर आज का AQI **{context.aqi}** है, जो **'{context.category}'** श्रेणी में आता है।
- **इसका क्या अर्थ है?** इस स्तर पर हवा में सांस लेना संवेदनशील व्यक्तियों (बच्चों, बुजुर्गों और दमा के मरीजों) के लिए श्वसन संबंधी परेशानी पैदा कर सकता है। स्वस्थ वयस्कों को भी लंबे समय तक बाहर रहने पर गले में जलन या खांसी हो सकती है।
- **3 जरूरी काम:**
  1. बाहर निकलते समय N95 मास्क पहनें।
  2. सुबह की सैर घर के अंदर योग में बदलें।
  3. घर में खिड़कियां बंद रखें और रसोई में चिमनी का उपयोग करें।"""
            else:
                reply = f"""{station_ctx_en}

### Simple Breakdown of Today's Air Quality

- **Current Status:** At **{context.station_name}**, the air quality index is **{context.aqi}**, categorized as **'{context.category}'**.
- **What This Means:** Inhaling ambient air at this level can cause acute respiratory discomfort in sensitive groups (children, elderly, and patients with asthma/COPD). Healthy adults may experience throat irritation or coughing during prolonged outdoor exposure.
- **Top 3 Recommendations:**
  1. Wear a certified N95 mask during daily commute.
  2. Shift early morning outdoor walks indoors.
  3. Keep home windows sealed during morning inversion hours."""

        # 6. Default Fallback
        else:
            if hi:
                reply = f"""{station_ctx_hi}

मैं एयरसाथी AI का पर्यावरण सहायक हूं। मैं वायु प्रदूषण, दैनिक दिनचर्या, इनडोर वायु गुणवत्ता और स्वास्थ्य सावधानियों पर परामर्श दे सकता हूं।

**आप मुझसे पूछ सकते हैं:**
- *"आज की हवा में बच्चों की सुरक्षा कैसे करें?"*
- *"क्या सुबह की सैर पर जाना सुरक्षित है?"*
- *"इनडोर एयर प्यूरीफायर कैसे चुनें?"*
- *"PM2.5 का स्वास्थ्य पर क्या प्रभाव पड़ता है?"*"""
            else:
                reply = f"""{station_ctx_en}

I am AirSaathi AI's Environmental Assistant. I can assist you with real-time pollution insights, safe daily scheduling, indoor air filtration, and health exposure mitigation.

**Common questions you can ask me:**
- *"How should I protect children during peak smog?"*
- *"Is it safe to exercise or walk outdoors today?"*
- *"What CADR rating do I need for my bedroom purifier?"*
- *"How do PM2.5 particulates affect cardiovascular health?"*"""

        followups = cls._generate_followups(request.message, language)

        disclaimer = (
            "चिकित्सीय अस्वीकरण: यह चैटबॉट केवल पर्यावरणीय स्वास्थ्य जानकारी प्रदान करता है, चिकित्सीय सलाह नहीं। किसी भी स्वास्थ्य समस्या में अपने डॉक्टर से संपर्क करें।"
            if hi
            else "Medical Disclaimer: This assistant provides environmental exposure reduction guidance, not medical diagnosis or treatment. Consult a licensed physician for clinical healthcare."
        )

        return ChatResponse(
            message=reply,
            language=language,
            ai_provider="expert-rules-fallback",
            ai_generated=False,
            context_used=context,
            suggested_followups=followups,
            disclaimer=disclaimer,
            timestamp=datetime.utcnow(),
        )

    @classmethod
    def _generate_followups(cls, user_message: str, language: str) -> List[str]:
        """Generates relevant follow-up question pills based on context."""
        hi = language == "hi"
        q = user_message.lower()

        if any(w in q for w in ["child", "kid", "school", "बच्चे", "स्कूल"]):
            return (
                ["बच्चों के लिए N95 मास्क कैसे चुनें?", "स्कूल बस में क्या सावधानियां रखें?", "घर के अंदर वायु शुद्ध कैसे रखें?"]
                if hi
                else ["Which N95 mask fits children best?", "What precautions should school buses take?", "How to improve indoor air for kids?"]
            )
        elif any(w in q for w in ["walk", "exercise", "jog", "सैर", "कसरत"]):
            return (
                ["दोपहर में सैर का सबसे सुरक्षित समय क्या है?", "घर पर योग करने के क्या फायदे हैं?", "आज का AQI स्वास्थ्य को कैसे प्रभावित करेगा?"]
                if hi
                else ["What is the safest afternoon walk window?", "What are good indoor workout alternatives?", "How does current AQI affect lungs?"]
            )
        elif any(w in q for w in ["indoor", "purifier", "प्यूरीफायर", "इनडोर"]):
            return (
                ["कमरे के लिए सही CADR कैसे निकालें?", "क्या इनडोर पौधे हवा साफ कर सकते हैं?", "रसोई का धुआं कैसे रोकें?"]
                if hi
                else ["How do I calculate purifier CADR for my room?", "Do indoor plants really clean air?", "How to control kitchen tadka smoke?"]
            )
        else:
            return (
                ["क्या आज बाहर सैर करना सुरक्षित है?", "बच्चों को स्मॉग से कैसे बचाएं?", "आज के AQI की सरल व्याख्या क्या है?"]
                if hi
                else ["Should I exercise outdoors today?", "How to protect children during smog?", "Explain today's AQI in simple terms"]
            )
