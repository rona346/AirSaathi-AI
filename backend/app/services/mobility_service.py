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
from backend.app.services.aqi_service import AqiService
from backend.app.services.emissions_service import EmissionsService
from backend.app.services.live_aqi_provider import get_active_aqi_provider
from backend.app.services.transit_service import TransitAvailabilityStatus, TransitService

logger = logging.getLogger(__name__)


class MobilityService:
    """Intelligent Sustainable Mobility Assistant service with city-aware recommendations,

    transparent emissions modeling, and Google Gemini integration with an expert-rule fallback.
    """

    @classmethod
    def generate_mobility_plan(cls, request: MobilityRequest) -> MobilityPlanResponse:
        """Processes a commute mobility planning request, evaluating emissions, health risk,

        and sustainable transit alternatives tailored to the specific city and air quality context.
        """
        # 1. Resolve target station and city context
        station_query = request.station_id
        if request.city and (not request.station_id or request.station_id == "delhi-anand-vihar"):
            matched = AqiService.get_station_by_id_or_city(request.city)
            if matched:
                station_query = matched.id
            else:
                station_query = request.city.lower().replace(" ", "-")

        provider = get_active_aqi_provider()
        cpcb_reading = provider.get_current_aqi(station_query)
        effective_city = request.city or cpcb_reading.station.city

        # 2. Compute emissions comparison across all 12 modes with city-aware transit checks
        mode_comparisons = EmissionsService.compare_all_modes(
            distance_km=request.distance_km,
            current_mode=request.current_mode,
            aqi=cpcb_reading.aqi,
            city=effective_city,
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

        # 5. Determine optimal recommended mode based on city availability, distance, AQI, and accessibility
        rec_mode, rec_label, rec_reason, active_advisory = cls._determine_recommended_mode(
            request=request,
            aqi=cpcb_reading.aqi,
            city=effective_city,
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
                    city=effective_city,
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
                city=effective_city,
                rec_mode=rec_mode,
                rec_label=rec_label,
                rec_reason=rec_reason,
                active_advisory=active_advisory,
                current_daily_g=current_daily_g,
            )

        # 7. Document transparent calculation methodology notes with credible source references
        methodology_notes = [
            "1. Grid Electricity Intensity: Modeled using Central Electricity Authority (CEA v19) National CO2 Baseline Database for the Indian Power Sector (~716 g CO2/kWh). Reference: https://cea.nic.in/cdm-co2-baseline-database/",
            "2. Vehicle Direct Emission Factors: Modeled using ARAI & BEE vehicle test standards. Petrol Car: ~165 g CO2e/km (tailpipe, 14.0 km/L); Diesel Car: ~175 g CO2e/km (tailpipe, 15.3 km/L); Petrol 2W: ~52 g CO2e/km (45 km/L); CNG Auto: ~72 g CO2e/km (30 km/kg). Reference: https://www.araiindia.com",
            "3. Electric Vehicles (EVs): 4W EV: ~0.15 kWh/km (107.4 g CO2e/km); 2W EV: ~0.035 kWh/km (25.1 g CO2e/km); e-Bus: ~1.20 kWh/km (859.2 g CO2e/km). EVs eliminate tailpipe exhaust but produce upstream grid emissions; they do not have zero lifecycle emissions.",
            "4. Occupancy Benchmarks: Private Car solo (1.0 default); Carpooling (3.0 default); CNG Auto (2.0); City Bus & e-Bus (35.0 passengers, MoHUA Comprehensive Mobility Plan benchmarks); Metro Rail (~636 passengers/train average, yielding ~22.0 g CO2e/passenger-km, DMRC Annual Sustainability Report 2023-24, https://www.delhimetrorail.com).",
            "5. Active Commuting (Walking/Cycling): Modeled as zero tailpipe emissions. Does NOT imply zero health risk; minute ventilation during aerobic exercise increases inhaled particulate dose during elevated AQI.",
            "6. City Transit Infrastructure: High-capacity urban rail (Metro) is evaluated only where operational infrastructure exists. For cities without metro (such as Udaipur) or unverified regions, recommendations prioritize verified road-based public or shared transit.",
        ]

        disclaimer = (
            "चिकित्सीय व पर्यावरणीय अस्वीकरण: प्रदर्शित कार्बन गणना इंजीनियरिंग मॉडलों पर आधारित है। बंद केबिन या वातानुकूलित कोच सीधे धुएं के संपर्क को कम करते हैं परंतु शून्य जोखिम की गारंटी नहीं देते। उच्च AQI में शारीरिक यात्रा (पैदल/साइकिल) की तुलना में श्वसन सुरक्षा को प्राथमिकता दें।"
            if request.language == "hi"
            else "Medical & Environmental Disclaimer: Emission metrics represent engineering models based on standardized parameters, not physical tailpipe tests. Enclosed cabins and transit reduce particulate inhalation relative to open roads, but do not provide zero exposure. During elevated AQI, prioritize respiratory protection over active travel."
        )

        return MobilityPlanResponse(
            station_id=cpcb_reading.station.id,
            station_name=cpcb_reading.station.name,
            city=effective_city,
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
        city: Optional[str],
        mode_comparisons: List[ModeEmissionDetail],
    ) -> Tuple[TransportMode, str, str, str]:
        """Calculates the optimal mode and smog health advisory based on city transit availability,

        distance, accessibility, and ambient CPCB AQI categories.
        """
        is_hi = request.language == "hi"
        dist = request.distance_km
        labels = EmissionsService.MODE_LABELS_HI if is_hi else EmissionsService.MODE_LABELS_EN

        # Check local Metro Rail operational availability in the specified city
        has_metro, metro_status, metro_reason_en, metro_reason_hi = TransitService.check_metro_availability(city)
        city_display = city.strip() if city and city.strip() else ("शहर" if is_hi else "the city")

        # Active Mobility Advisory based on official CPCB NAQI breakpoints
        if aqi >= 401:  # Severe
            active_advisory = (
                "चेतावनी: वायु गुणवत्ता गंभीर (AQI > 400) है। पैदल या साइकिल से यात्रा करने पर गहरी सांस लेने से PM2.5 फेफड़ों में गहराई तक पहुंचता है। आज सक्रिय आउटडोर आवागमन पूरी तरह टालें।"
                if is_hi
                else "Critical Warning: AQI is Severe (> 400). Strenuous walking or cycling induces high minute-ventilation, depositing toxic PM2.5 deep into alveoli. Avoid outdoor active commuting today."
            )
        elif aqi >= 301:  # Very Poor
            active_advisory = (
                "सावधानी: वायु गुणवत्ता बहुत खराब (AQI 301-400) है। सक्रिय आवागमन टालें; बाहर निकलने पर प्रमाणित N95 मास्क अनिवार्य रूप से लगाएं।"
                if is_hi
                else "Caution: AQI is Very Poor (301-400). Strenuous active travel increases particulate inhalation. Avoid walking or cycling; wear an airtight N95 respirator if stepping out."
            )
        elif aqi >= 201:  # Poor
            active_advisory = (
                "सावधानी: वायु गुणवत्ता खराब (AQI 201-300) है। 1.5 किमी से अधिक पैदल या साइकिल यात्रा न करें। बाहर निकलने पर N95 मास्क पहनें।"
                if is_hi
                else "Caution: AQI is Poor (201-300). Restrict active travel to short trips (< 1.5 km). Wear an N95 respirator and avoid morning rush-hour thermal inversion."
            )
        elif aqi >= 101:  # Moderate
            active_advisory = (
                "मध्यम वायु गुणवत्ता: 2-3 किमी तक पैदल चलना या 6 किमी तक साइकिल चलाना स्वीकार्य है। संवेदनशील व्यक्ति (अस्थमा/हृदय) अत्यधिक श्रम से बचें।"
                if is_hi
                else "Moderate Air Quality: Active walking (< 2.5 km) or cycling (< 6 km) achieves zero tailpipe emissions. Sensitive individuals should avoid heavy exertion."
            )
        else:  # Satisfactory / Good
            active_advisory = (
                "अनुकूल वायु गुणवत्ता: सक्रिय यात्रा स्वास्थ्यवर्धक है और शून्य टेलपाइप उत्सर्जन प्राप्त करती है।"
                if is_hi
                else "Favorable Air Quality: Low pollution exposure risk. Active walking or cycling achieves zero tailpipe emissions with cardiovascular fitness benefits."
            )

        # Accessibility checks
        if request.accessibility in (
            AccessibilityNeed.WHEELCHAIR,
            AccessibilityNeed.LOW_WALKING,
            AccessibilityNeed.SENIOR_FRIENDLY,
        ):
            if dist >= 4.0 and has_metro:
                rec_mode = TransportMode.METRO
                rec_reason = (
                    "सुलभ लिफ्ट सुविधाओं और झटके-रहित यात्रा के लिए मेट्रो रेल उपयुक्त विकल्प है।"
                    if is_hi
                    else "Accessible step-free elevators and grade-separated comfort make Metro a suitable choice."
                )
            else:
                rec_mode = TransportMode.ELECTRIC_CAR
                metro_note = (
                    f" ({city_display} में मेट्रो रेल अनुपलब्ध)"
                    if not has_metro and is_hi
                    else (f" (Metro rail unavailable in {city_display})" if not has_metro else "")
                )
                rec_reason = (
                    f"शारीरिक सुगमता और सीधे गंतव्य तक पहुंचने हेतु इलेक्ट्रिक कैब/कार उपयुक्त है{metro_note}।"
                    if is_hi
                    else f"Door-to-door accessible transport with reduced emissions via EV/electric cab{metro_note}."
                )
            return rec_mode, labels.get(rec_mode, rec_mode.value), rec_reason, active_advisory

        # Distance & AQI Decision Matrix (CITY-AWARE)
        if aqi <= 200 and dist <= 2.0:
            rec_mode = TransportMode.WALKING
            rec_reason = (
                "2 किमी से कम दूरी और मध्यम एक्यूआई में पैदल चलना शून्य टेलपाइप उत्सर्जन के साथ स्वास्थ्यवर्धक है।"
                if is_hi
                else "Short commute under 2 km with moderate AQI: zero tailpipe emissions with active health benefits."
            )
        elif aqi <= 200 and dist <= 6.0:
            rec_mode = TransportMode.CYCLING
            rec_reason = (
                "शून्य टेलपाइप उत्सर्जन और मध्यम दूरी के लिए साइकिल टिकाऊ साधन है।"
                if is_hi
                else "Zero tailpipe emissions and optimal efficiency for short-to-medium trips under 6 km."
            )
        elif dist >= 8.0:
            # Long distance: Check metro availability in this city
            if has_metro:
                rec_mode = TransportMode.METRO
                rec_reason = (
                    "लंबी दूरी के लिए मेट्रो प्रति यात्री ~86% कार्बन उत्सर्जन घटाती है और सड़क स्तर के सीधे धुएं को कम करती है (स्टेशन पर N95 मास्क पहनें)।"
                    if is_hi
                    else "High-capacity electrified transit reduces per-passenger emissions by ~86% compared to solo car driving, providing lower exposure than open road transit (N95 mask advised for outdoor access walks)."
                )
            elif metro_status == TransitAvailabilityStatus.UNAVAILABLE:
                # Confirmed no metro (e.g. Udaipur)
                rec_mode = TransportMode.CARPOOL
                rec_reason = (
                    f"{city_display} में मेट्रो रेल सेवा उपलब्ध न होने के कारण, लंबी दूरी के लिए 3-व्यक्ति साझा कारपूलिंग प्रति-यात्री कार्बन उत्सर्जन में ~67% की सीधी कटौती करती है।"
                    if is_hi
                    else f"In {city_display}, where high-capacity metro rail is not operational, 3-person shared carpooling delivers the highest practical per-passenger carbon reduction (~67%) for longer commutes while reducing road traffic."
                )
            else:
                # Unknown / unverified city
                rec_mode = TransportMode.CARPOOL
                rec_reason = (
                    f"'{city_display}' के लिए स्थानीय सार्वजनिक परिवहन नेटवर्क असत्यापित है। बिना रेल अधोसंरचना पूर्वकल्पित किए, 3-व्यक्ति साझा कारपूलिंग (~67% उत्सर्जन कटौती) को एक लचीले विकल्प के रूप में अनुशंसित किया जाता है।"
                    if is_hi
                    else f"Transit network availability for '{city_display}' is unverified in our system. Recommending shared carpooling as a flexible, lower-emission road option (~67% reduction) without assuming fixed rail infrastructure."
                )
        elif dist >= 4.0:
            # Medium distance: Check electric bus availability
            has_ebus = TransitService.check_electric_bus_availability(city)
            if has_ebus:
                rec_mode = TransportMode.ELECTRIC_BUS
                rec_reason = (
                    "इलेक्ट्रिक सिटी बस प्रति यात्री उत्सर्जन को न्यूनतम रखती है और सड़क की भीड़भाड़ कम करती है।"
                    if is_hi
                    else "Electric City Bus delivers ~85% per-passenger carbon reduction and eases urban congestion."
                )
            else:
                rec_mode = TransportMode.CARPOOL
                rec_reason = (
                    "साझा यात्रा (3-व्यक्ति कारपूल) से प्रति व्यक्ति उत्सर्जन में 67% तक की सीधी कटौती होती है।"
                    if is_hi
                    else "Shared ride (3-person carpool) cuts personal emissions by 67% without route transfers."
                )
        else:
            rec_mode = TransportMode.CARPOOL
            rec_reason = (
                "साझा यात्रा (3-व्यक्ति कारपूल) से प्रति व्यक्ति उत्सर्जन में 67% तक की सीधी कटौती होती है।"
                if is_hi
                else "Shared ride (3-person carpool) cuts personal emissions by 67% without route transfers."
            )

        return rec_mode, labels.get(rec_mode, rec_mode.value), rec_reason, active_advisory

    @classmethod
    def _call_gemini_mobility(
        cls,
        request: MobilityRequest,
        outdoor: CurrentAqiResponse,
        city: str,
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

        has_metro, metro_status, metro_reason_en, metro_reason_hi = TransitService.check_metro_availability(city)
        transit_note = metro_reason_en if request.language != "hi" else metro_reason_hi

        system_instruction = (
            f"You are AirSaathi AI's Sustainable Mobility Specialist. {lang_instr}.\n"
            f"Task: Provide actionable, concise, and pollution-aware commuting advice.\n"
            f"COMMUTE PARAMETERS:\n"
            f"- City: {city}\n"
            f"- City Transit Status: {transit_note}\n"
            f"- Distance: {request.distance_km} km (One-way)\n"
            f"- Current Mode: {request.current_mode.value}\n"
            f"- Frequency: {request.frequency.value}\n"
            f"- Purpose: {request.purpose.value}\n"
            f"- Accessibility Need: {request.accessibility.value}\n"
            f"- Estimated Current Daily Emissions: {current_daily_g} g CO2e\n"
            f"AMBIENT AIR QUALITY CONTEXT:\n"
            f"- Station: {outdoor.station.name}, {city}\n"
            f"- AQI: {outdoor.aqi} ({outdoor.category.value})\n"
            f"- Prominent Pollutant: {outdoor.prominent_pollutant}\n"
            f"- Recommended Mode: {rec_mode.value} ({rec_reason})\n"
            f"- Active Mobility Caution: {active_advisory}\n\n"
            f"STRICT RULES:\n"
            f"1. Do NOT recommend or mention Metro Rail if Metro is unavailable or unverified in {city}.\n"
            f"2. Never claim any transit mode is 100% safe; clearly distinguish reduced exposure from zero exposure.\n"
            f"3. Never describe Electric Vehicles (EVs) as having zero emissions; acknowledge upstream power-grid emissions (~716 g CO2/kWh in India).\n"
            f"4. Never recommend outdoor walking or cycling without stating AQI exposure precautions.\n"
            f"5. Provide 3-4 structured bullet points on: Mode switch savings, In-transit respiratory protection, and Carpooling feasibility.\n"
            f"6. End with a short medical disclaimer."
        )

        prompt = f"Please advise on sustainable, clean-air commuting for a {request.distance_km} km commute in {city} under current {outdoor.category.value} air quality."

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
        city: str,
        rec_mode: TransportMode,
        rec_label: str,
        rec_reason: str,
        active_advisory: str,
        current_daily_g: float,
    ) -> str:
        """Deterministic expert rule generator for sustainable mobility recommendations with city awareness."""
        is_hi = request.language == "hi"
        has_metro, metro_status, _, _ = TransitService.check_metro_availability(city)

        if is_hi:
            transit_tip = (
                "- **सार्वजनिक व साझा परिवहन:** मेट्रो या 3-व्यक्ति कारपूलिंग अपनाने से यात्रा का कार्बन फुटप्रिंट 67% से 85% तक घट जाता है।"
                if has_metro
                else f"- **साझा परिवहन:** {city} में मेट्रो रेल सेवा उपलब्ध नहीं है। अतः 3-व्यक्ति कारपूलिंग या स्थानीय बस द्वारा यात्रा करने से कार्बन फुटप्रिंट में 67% की कटौती होती है।"
            )
            return (
                f"### सतत गतिशीलता परामर्श ({city} - {outdoor.station.name})\n\n"
                f"- **वर्तमान उत्सर्जन:** आपकी {request.distance_km} किमी की यात्रा में वर्तमान में लगभग **{current_daily_g} ग्राम CO2e** प्रतिदिन उत्सर्जित होता है।\n"
                f"- **अनुशंसित साधन:** **{rec_label}**\n"
                f"  - *कारण:* {rec_reason}\n"
                f"- **वायु गुणवत्ता व स्वास्थ्य सावधानी:** वर्तमान में AQI **{outdoor.aqi}** ({outdoor.category.value}) है। {active_advisory}\n"
                f"{transit_tip}\n"
                f"- **वाहन केबिन प्रोटोकॉल:** सड़क यात्रा के दौरान वाहन की खिड़कियां बंद रखें और एयर कंडीशनर को **रीसर्क्युलेशन मोड** पर रखें (यह संपर्क घटाता है परंतु शून्य नहीं करता)।"
            )
        else:
            transit_tip = (
                "- **Public Transit & Ridesharing:** Switching to electrified rail (Metro) or a 3-person carpool reduces per-passenger carbon emissions by 67% to 86%."
                if has_metro
                else f"- **Ridesharing & Local Transit:** Metro rail is not operational in {city}. Shared 3-person carpooling or local bus transit provides the highest practical carbon reduction (~67%)."
            )
            return (
                f"### Sustainable Mobility Strategy ({city} - {outdoor.station.name})\n\n"
                f"- **Current Carbon Baseline:** Your {request.distance_km} km commute generates approximately **{current_daily_g} g CO2e** per day.\n"
                f"- **Recommended Mode:** **{rec_label}**\n"
                f"  - *Rationale:* {rec_reason}\n"
                f"- **AQI Exposure Safeguard:** Currently, AQI is **{outdoor.aqi}** ({outdoor.category.value}). {active_advisory}\n"
                f"{transit_tip}\n"
                f"- **Vehicle Cabin Protocol:** Keep car windows closed in congested corridors and switch ventilation to **Air Recirculation Mode** to reduce (though not eliminate) particulate exposure."
            )
