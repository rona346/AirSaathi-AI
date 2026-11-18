import json
import logging
from datetime import datetime
from typing import List, Optional, Tuple
import httpx

from backend.app.core.config import settings
from backend.app.models.aqi import CurrentAqiResponse
from backend.app.models.mobility import (
    AccessibilityNeed,
    CommuteFrequency,
    MobilityPlanResponse,
    MobilityRequest,
    ModeEmissionDetail,
    TransportMode,
)
from backend.app.services.emissions_service import EmissionsService
from backend.app.services.live_aqi_provider import get_active_aqi_provider

logger = logging.getLogger(__name__)


class MobilityService:
    """Intelligent Sustainable Mobility Assistant service with AQI-aware recommendations,

    transparent emissions modeling, and Google Gemini integration with an expert-rule fallback.
    """

    @classmethod
    def generate_mobility_plan(cls, request: MobilityRequest) -> MobilityPlanResponse:
        """Processes a commute mobility planning request, evaluating emissions, health risk, and sustainable transit alternatives."""
        # 1. Fetch ambient CPCB context
        provider = get_active_aqi_provider()
        cpcb_reading = provider.get_current_aqi(request.station_id)

        # 2. Compute emissions comparison across all 12 modes
        mode_comparisons = EmissionsService.compare_all_modes(
            distance_km=request.distance_km,
            current_mode=request.current_mode,
            aqi=cpcb_reading.aqi,
            language=request.language,
            accessibility=request.accessibility,
            occupancy=request.occupancy,
        )

        # 3. Calculate current mode emissions for trip and daily frequency
        trips_per_day = 2.0 if request.frequency in (
            CommuteFrequency.DAILY_ROUND_TRIP,
            CommuteFrequency.WEEKDAYS_ONLY,
        ) else 1.0

        _, _, current_trip_g, per_p_g = EmissionsService.calculate_trip_emissions(
            request.current_mode, request.distance_km, occupancy=request.occupancy
        )
        current_daily_g = round(per_p_g * trips_per_day, 1)

        # 4. Compute carpooling potential
        carpool_est = EmissionsService.calculate_carpooling_potential(
            distance_km=request.distance_km, round_trips_per_day=trips_per_day
        )

        # 5. Determine optimal recommended mode based on distance, AQI, and accessibility
        rec_mode, rec_label, rec_reason, active_advisory = cls._determine_recommended_mode(
            request=request,
            aqi=cpcb_reading.aqi,
            mode_comparisons=mode_comparisons,
        )

        # 6. Try Google Gemini API for personalized recommendation, with expert fallback
        ai_text = None
        ai_provider = "expert-rules-fallback"
        ai_generated = False

        if settings.GEMINI_API_KEY:
            try:
                ai_text = cls._call_gemini_mobility(
                    request=request,
                    outdoor=cpcb_reading,
                    rec_mode=rec_mode,
                    rec_reason=rec_reason,
                    active_advisory=active_advisory,
                    current_daily_g=current_daily_g,
                )
                if ai_text:
                    ai_provider = "google-gemini"
                    ai_generated = True
            except Exception as e:
                logger.warning(f"Gemini Mobility call failed, switching to expert rule engine: {e}")

        if not ai_text:
            ai_text = cls._generate_expert_fallback_text(
                request=request,
                outdoor=cpcb_reading,
                rec_mode=rec_mode,
                rec_label=rec_label,
                rec_reason=rec_reason,
                active_advisory=active_advisory,
                current_daily_g=current_daily_g,
            )

        # 7. Document transparent calculation methodology notes
        methodology_notes = [
            "Modeled emissions are calculated based on India Central Electricity Authority (CEA v19) national grid baseline: ~716 g CO2/kWh and ARAI standard vehicle test figures.",
            "Private petrol car baseline: ~165 g CO2e/km direct tailpipe emissions.",
            "Electric vehicles (EVs) have zero direct tailpipe exhaust; upstream power-grid emissions are modeled at ~107 g CO2e/km (4W) and ~25 g CO2e/km (2W).",
            "Public bus (average 35 passengers) and Metro Rail (~22 g CO2e/passenger-km) yield high passenger-kilometer efficiency.",
            "Active travel (walking/cycling) is modeled as zero-emission but carries respiratory exposure risks during high AQI episodes.",
        ]

        disclaimer = (
            "चिकित्सीय व पर्यावरणीय अस्वीकरण: प्रदर्शित कार्बन गणना मॉडल्ड अनुमानों पर आधारित है। वायु प्रदूषण के दिनों में शारीरिक यात्रा (पैदल/साइकिल) की तुलना में श्वसन सुरक्षा को प्राथमिकता दें।"
            if request.language == "hi"
            else "Medical & Environmental Disclaimer: Emission metrics represent engineering models based on standardized parameters, not measured tailpipe tests. During elevated AQI, prioritize respiratory protection over active travel."
        )

        return MobilityPlanResponse(
            station_id=cpcb_reading.station.id,
            station_name=cpcb_reading.station.name,
            city=cpcb_reading.station.city,
            aqi=cpcb_reading.aqi,
            category=cpcb_reading.category.value,
            prominent_pollutant=cpcb_reading.prominent_pollutant,
            is_demo_data=cpcb_reading.is_demo_data,
            data_source=cpcb_reading.data_source,
            observed_at=cpcb_reading.last_updated,
            language=request.language,
            distance_km=request.distance_km,
            frequency=request.frequency.value,
            current_mode=request.current_mode,
            current_trip_emissions_g=per_p_g,
            current_daily_emissions_g=current_daily_g,
            mode_comparisons=mode_comparisons,
            recommended_mode=rec_mode,
            recommended_mode_label=rec_label,
            recommended_mode_reason=rec_reason,
            active_mobility_advisory=active_advisory,
            carpool_potential=carpool_est,
            ai_recommendation=ai_text,
            ai_provider=ai_provider,
            ai_generated=ai_generated,
            methodology_notes=methodology_notes,
            disclaimer=disclaimer,
            generated_at=datetime.utcnow(),
        )

    @classmethod
    def _determine_recommended_mode(
        cls,
        request: MobilityRequest,
        aqi: int,
        mode_comparisons: List[ModeEmissionDetail],
    ) -> Tuple[TransportMode, str, str, str]:
        """Calculates the optimal mode and smog health advisory based on distance, accessibility, and ambient AQI."""
        is_hi = request.language == "hi"
        dist = request.distance_km
        labels = EmissionsService.MODE_LABELS_HI if is_hi else EmissionsService.MODE_LABELS_EN

        # Active Mobility Advisory (Walking / Cycling)
        if aqi >= 301:
            active_advisory = (
                "चेतावनी: वायु गुणवत्ता गंभीर (AQI > 300) है। पैदल या साइकिल से यात्रा करने पर गहरी सांस लेने से PM2.5 फेफड़ों में गहराई तक पहुंचता है। आज सक्रिय आउटडोर आवागमन पूरी तरह टालें।"
                if is_hi
                else "Critical Warning: AQI is Severe (> 300). Strenuous walking or cycling induces high minute-ventilation, depositing toxic PM2.5 deep into alveoli. Avoid outdoor active commuting today."
            )
        elif aqi >= 201:
            active_advisory = (
                "सावधानी: वायु गुणवत्ता बहुत खराब (AQI 201-300) है। 1.5 किमी से अधिक पैदल या साइकिल यात्रा न करें। बाहर निकलने पर प्रमाणित N95 मास्क अवश्य पहनें।"
                if is_hi
                else "Caution: AQI is Poor/Very Poor (201-300). Restrict active travel to short trips (< 1.5 km). Wear an N95 respirator and avoid morning inversion hours."
            )
        else:
            active_advisory = (
                "अनुकूल: वायु गुणवत्ता स्वीकार्य है। 2-3 किमी तक पैदल चलना या 8 किमी तक साइकिल चलाना शून्य-उत्सर्जन के साथ स्वास्थ्यवर्धक है।"
                if is_hi
                else "Favorable: AQI is in the acceptable range. Active walking (< 2.5 km) or cycling (< 8 km) achieves 100% zero tailpipe emissions with cardiovascular benefits."
            )

        # Accessibility checks
        if request.accessibility in (AccessibilityNeed.WHEELCHAIR, AccessibilityNeed.LOW_WALKING, AccessibilityNeed.SENIOR_FRIENDLY):
            if dist >= 4.0:
                rec_mode = TransportMode.METRO
                rec_reason = (
                    "सुलभ लिफ्ट सुविधाओं और बिना झटके की यात्रा के लिए मेट्रो सर्वोत्तम है।"
                    if is_hi
                    else "Accessible step-free elevators and grade-separated comfort make Metro the optimal choice."
                )
            else:
                rec_mode = TransportMode.ELECTRIC_CAR
                rec_reason = (
                    "शारीरिक सुगमता और सीधे गंतव्य तक पहुंचने हेतु इलेक्ट्रिक कैब/कार सबसे उपयुक्त है।"
                    if is_hi
                    else "Door-to-door accessible transport with reduced emissions via EV/electric cab."
                )
            return rec_mode, labels.get(rec_mode, rec_mode.value), rec_reason, active_advisory

        # Distance & AQI Decision Matrix
        if aqi <= 200 and dist <= 2.0:
            rec_mode = TransportMode.WALKING
            rec_reason = (
                "2 किमी से कम दूरी और मध्यम एक्यूआई में पैदल चलना 100% प्रदूषण-मुक्त और स्वास्थ्यवर्धक है।"
                if is_hi
                else "Short commute under 2 km with moderate AQI: 100% zero emissions with health benefits."
            )
        elif aqi <= 200 and dist <= 6.0:
            rec_mode = TransportMode.CYCLING
            rec_reason = (
                "शून्य टेलपाइप उत्सर्जन और मध्यम दूरी के लिए साइकिल सबसे टिकाऊ साधन है।"
                if is_hi
                else "Zero tailpipe emissions and optimal efficiency for short-to-medium trips under 6 km."
            )
        elif dist >= 8.0:
            rec_mode = TransportMode.METRO
            rec_reason = (
                "लंबी दूरी के लिए मेट्रो 86% कार्बन उत्सर्जन घटाती है और सड़क स्तर के स्मॉग से बचाती है।"
                if is_hi
                else "High-capacity electrified transit reduces emissions by ~86% and bypasses road-level smog."
            )
        elif dist >= 4.0:
            rec_mode = TransportMode.ELECTRIC_BUS
            rec_reason = (
                "इलेक्ट्रिक सिटी बस प्रति यात्री उत्सर्जन को न्यूनतम रखती है और सड़क की भीड़भाड़ कम करती है।"
                if is_hi
                else "e-Bus delivers 85% per-passenger carbon reduction and eases urban congestion."
            )
        else:
            rec_mode = TransportMode.CARPOOL
            rec_reason = (
                "साझा यात्रा (कारपूल) से प्रति व्यक्ति उत्सर्जन में 67% तक की सीधी कटौती होती है।"
                if is_hi
                else "Shared ride (3-person carpool) cuts personal emissions by 67% without route transfers."
            )

        return rec_mode, labels.get(rec_mode, rec_mode.value), rec_reason, active_advisory

    @classmethod
    def _call_gemini_mobility(
        cls,
        request: MobilityRequest,
        outdoor: CurrentAqiResponse,
        rec_mode: TransportMode,
        rec_reason: str,
        active_advisory: str,
        current_daily_g: float,
    ) -> Optional[str]:
        """Invokes Google Gemini API with commute parameters and AQI telemetry."""
        model_id = getattr(settings, "GEMINI_MODEL_ID", "gemini-2.5-flash") or "gemini-2.5-flash"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:generateContent?key={settings.GEMINI_API_KEY}"
        headers = {"Content-Type": "application/json"}

        lang_instr = "Respond in fluent Hindi (Devanagari script)" if request.language == "hi" else "Respond in fluent English"

        system_instruction = (
            f"You are AirSaathi AI's Sustainable Mobility Specialist. {lang_instr}.\n"
            f"Task: Provide actionable, concise, and pollution-aware commuting advice.\n"
            f"COMMUTE PARAMETERS:\n"
            f"- Distance: {request.distance_km} km (One-way)\n"
            f"- Current Mode: {request.current_mode.value}\n"
            f"- Frequency: {request.frequency.value}\n"
            f"- Purpose: {request.purpose.value}\n"
            f"- Accessibility Need: {request.accessibility.value}\n"
            f"- Estimated Current Daily Emissions: {current_daily_g} g CO2e\n"
            f"AMBIENT AIR QUALITY CONTEXT:\n"
            f"- Station: {outdoor.station.name}, {outdoor.station.city}\n"
            f"- AQI: {outdoor.aqi} ({outdoor.category.value})\n"
            f"- Prominent Pollutant: {outdoor.prominent_pollutant}\n"
            f"- Recommended Mode: {rec_mode.value} ({rec_reason})\n"
            f"- Active Mobility Caution: {active_advisory}\n\n"
            f"STRICT RULES:\n"
            f"1. Do NOT invent specific transit route numbers, bus schedules, or platform details.\n"
            f"2. Never recommend outdoor walking or cycling without stating AQI exposure precautions.\n"
            f"3. Acknowledge that EVs reduce tailpipe emissions to zero but rely on upstream grid power.\n"
            f"4. Provide 3-4 structured bullet points on: Mode switch savings, In-transit respiratory protection, and Carpooling feasibility.\n"
            f"5. End with a short medical disclaimer."
        )

        prompt = f"Please advise on sustainable, clean-air commuting for a {request.distance_km} km commute under current {outdoor.category.value} air quality."

        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": f"{system_instruction}\n\nUser: {prompt}"}],
                }
            ],
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 800,
            },
        }

        with httpx.Client(timeout=15.0) as client:
            res = client.post(url, json=payload, headers=headers)
            if res.status_code != 200:
                logger.warning(f"Gemini Mobility returned HTTP {res.status_code}")
                return None

            data = res.json()
            candidates = data.get("candidates", [])
            if not candidates:
                return None

            text = ""
            for part in candidates[0].get("content", {}).get("parts", []):
                if isinstance(part, dict) and "text" in part and part["text"]:
                    text += part["text"]

            return text.strip() if text.strip() else None

    @classmethod
    def _generate_expert_fallback_text(
        cls,
        request: MobilityRequest,
        outdoor: CurrentAqiResponse,
        rec_mode: TransportMode,
        rec_label: str,
        rec_reason: str,
        active_advisory: str,
        current_daily_g: float,
    ) -> str:
        """Deterministic expert rule generator for sustainable mobility recommendations."""
        is_hi = request.language == "hi"

        if is_hi:
            return (
                f"### सतत गतिशीलता परामर्श ({outdoor.station.name})\n\n"
                f"- **वर्तमान उत्सर्जन:** आपकी {request.distance_km} किमी की यात्रा में वर्तमान में लगभग **{current_daily_g} ग्राम CO2e** प्रतिदिन उत्सर्जित होता है।\n"
                f"- **सर्वोत्तम अनुशंसित साधन:** **{rec_label}**\n"
                f"  - *कारण:* {rec_reason}\n"
                f"- **वायु गुणवत्ता व स्वास्थ्य सावधानी:** वर्तमान में AQI **{outdoor.aqi}** ({outdoor.category.value}) है। {active_advisory}\n"
                f"- **कारपूलिंग व सार्वजनिक परिवहन:** मेट्रो या 3-व्यक्ति कारपूलिंग अपनाने से यात्रा का कार्बन फुटप्रिंट 67% से 85% तक घट जाता है।\n"
                f"- **वाहन केबिन प्रोटोकॉल:** सड़क यात्रा के दौरान वाहन की खिड़कियां बंद रखें और एयर कंडीशनर को **रीसर्क्युलेशन मोड** पर रखें।"
            )
        else:
            return (
                f"### Sustainable Mobility Strategy ({outdoor.station.name})\n\n"
                f"- **Current Carbon Baseline:** Your {request.distance_km} km commute generates approximately **{current_daily_g} g CO2e** per day.\n"
                f"- **Recommended Mode:** **{rec_label}**\n"
                f"  - *Rationale:* {rec_reason}\n"
                f"- **AQI Exposure Safeguard:** Currently, AQI is **{outdoor.aqi}** ({outdoor.category.value}). {active_advisory}\n"
                f"- **Public Transit & Ridesharing:** Switching to electrified rail (Metro) or a 3-person carpool reduces per-passenger carbon emissions by 67% to 86%.\n"
                f"- **Vehicle Cabin Protocol:** Keep car windows closed in congested corridors and switch ventilation to **Air Recirculation Mode** to keep out toxic roadside particulates."
            )
