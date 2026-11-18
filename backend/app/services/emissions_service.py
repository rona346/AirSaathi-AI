from typing import Dict, List, Optional, Tuple
from backend.app.models.mobility import (
    AccessibilityNeed,
    CarpoolEstimate,
    CommuteFrequency,
    CommutePurpose,
    ModeEmissionDetail,
    TransportMode,
)
from backend.app.services.transit_service import TransitAvailabilityStatus, TransitService


class EmissionsService:
    """Transparent, scientifically-grounded transport emission and exposure calculator.

    Emission factors are modeled using:
    - CEA (Central Electricity Authority, Ministry of Power, Govt. of India) CO2 Baseline Database
      for the Indian Power Sector, User Guide Version 19.0 (Dec 2023): National grid baseline weighted
      average: ~716 g CO2/kWh (0.716 kg CO2/kWh). Reference: https://cea.nic.in/cdm-co2-baseline-database/
    - ARAI (Automotive Research Association of India) & BEE (Bureau of Energy Efficiency) standard
      vehicle fuel efficiency benchmarks: Petrol car ~14 km/L (165 g CO2/km); Diesel car ~15.3 km/L
      (175 g CO2/km); Petrol 2-wheeler ~45 km/L (52 g CO2/km); CNG auto ~30 km/kg (72 g CO2/km).
      Reference: https://www.araiindia.com
    - DMRC (Delhi Metro Rail Corporation) Annual Sustainability Reports (2022-24) & MoHUA benchmarks:
      Urban electric metro rail specific energy consumption ~30.7 Wh/passenger-km (~22.0 g CO2e/passenger-km
      at ~716 g/kWh grid intensity). Reference: https://www.delhimetrorail.com
    - MoHUA Comprehensive Mobility Plan (CMP) urban bus occupancy standard: Average 35 passengers per bus.

    Important Principles:
    1. Electric Vehicles (EVs) have zero direct tailpipe exhaust, but generate indirect emissions through
       the electricity grid mix (~716 g CO2/kWh in India). They must NEVER be described as having zero emissions.
    2. Active travel (walking/cycling) has zero direct and indirect emissions, but carries respiratory
       particulate exposure risk during elevated AQI. Zero emissions does not imply zero health risk.
    3. Enclosed vehicles (cars, buses, trains) with air recirculation reduce roadside particulate exposure
       relative to open roads, but DO NOT provide zero exposure.
    """

    # Direct (tailpipe exhaust) emissions in g CO2e / vehicle-km
    DIRECT_EMISSION_FACTORS: Dict[TransportMode, float] = {
        TransportMode.PETROL_CAR: 165.0,
        TransportMode.DIESEL_CAR: 175.0,
        TransportMode.TWO_WHEELER: 52.0,
        TransportMode.ELECTRIC_CAR: 0.0,
        TransportMode.ELECTRIC_TWO_WHEELER: 0.0,
        TransportMode.CNG_AUTO: 72.0,
        TransportMode.PUBLIC_BUS: 1100.0,
        TransportMode.ELECTRIC_BUS: 0.0,
        TransportMode.METRO: 0.0,
        TransportMode.CARPOOL: 165.0,
        TransportMode.WALKING: 0.0,
        TransportMode.CYCLING: 0.0,
    }

    # Upstream electricity grid indirect emissions in g CO2e / vehicle-km
    # Modeled via CEA v19 grid emission factor: ~716 g CO2/kWh:
    # - 4W EV: ~0.15 kWh/km * 716 = 107.4 g CO2e / vehicle-km
    # - 2W EV: ~0.035 kWh/km * 716 = 25.1 g CO2e / vehicle-km
    # - e-Bus: ~1.20 kWh/km * 716 = 859.2 g CO2e / vehicle-km
    # - Metro: Train-level factor ~13,992 g CO2e / train-km (approx 22.0 g / passenger-km at 636 occupancy)
    GRID_INDIRECT_FACTORS: Dict[TransportMode, float] = {
        TransportMode.PETROL_CAR: 0.0,
        TransportMode.DIESEL_CAR: 0.0,
        TransportMode.TWO_WHEELER: 0.0,
        TransportMode.ELECTRIC_CAR: 107.4,
        TransportMode.ELECTRIC_TWO_WHEELER: 25.1,
        TransportMode.CNG_AUTO: 0.0,
        TransportMode.PUBLIC_BUS: 0.0,
        TransportMode.ELECTRIC_BUS: 859.2,
        TransportMode.METRO: 22.0,  # Expressed per passenger-km based on DMRC sustainability reporting
        TransportMode.CARPOOL: 0.0,
        TransportMode.WALKING: 0.0,
        TransportMode.CYCLING: 0.0,
    }

    # Standard modeled passenger occupancy benchmarks
    DEFAULT_OCCUPANCY: Dict[TransportMode, float] = {
        TransportMode.PETROL_CAR: 1.0,  # Solo baseline default
        TransportMode.DIESEL_CAR: 1.0,
        TransportMode.TWO_WHEELER: 1.0,
        TransportMode.ELECTRIC_CAR: 1.0,  # Consistent solo driver default
        TransportMode.ELECTRIC_TWO_WHEELER: 1.0,
        TransportMode.CNG_AUTO: 2.0,  # Typical shared urban auto-rickshaw occupancy
        TransportMode.PUBLIC_BUS: 35.0,  # MoHUA urban transit average
        TransportMode.ELECTRIC_BUS: 35.0,  # MoHUA urban transit average
        TransportMode.METRO: 1.0,  # Factor already calibrated per passenger-km (DMRC benchmark)
        TransportMode.CARPOOL: 3.0,  # 3-person shared commute pool
        TransportMode.WALKING: 1.0,
        TransportMode.CYCLING: 1.0,
    }

    MODE_LABELS_EN: Dict[TransportMode, str] = {
        TransportMode.PETROL_CAR: "Private Petrol Car",
        TransportMode.DIESEL_CAR: "Private Diesel Car",
        TransportMode.TWO_WHEELER: "Petrol Two-Wheeler (Bike/Scooter)",
        TransportMode.ELECTRIC_CAR: "Electric Car (EV - Grid-Powered)",
        TransportMode.ELECTRIC_TWO_WHEELER: "Electric Scooter (e-2W - Grid-Powered)",
        TransportMode.CNG_AUTO: "Shared CNG Auto-Rickshaw",
        TransportMode.PUBLIC_BUS: "Public City Bus (Diesel/CNG)",
        TransportMode.ELECTRIC_BUS: "Electric City Bus (e-Bus)",
        TransportMode.METRO: "Urban Metro Rail",
        TransportMode.CARPOOL: "Shared Carpooling (3-person pool)",
        TransportMode.WALKING: "Active Walking",
        TransportMode.CYCLING: "Active Cycling",
    }

    MODE_LABELS_HI: Dict[TransportMode, str] = {
        TransportMode.PETROL_CAR: "निजी पेट्रोल कार (Solo Car)",
        TransportMode.DIESEL_CAR: "निजी डीजल कार",
        TransportMode.TWO_WHEELER: "पेट्रोल दोपहिया (बाइक/स्कूटर)",
        TransportMode.ELECTRIC_CAR: "इलेक्ट्रिक कार (EV - ग्रिड संचालित)",
        TransportMode.ELECTRIC_TWO_WHEELER: "इलेक्ट्रिक स्कूटर (e-2W - ग्रिड संचालित)",
        TransportMode.CNG_AUTO: "सीएनजी ऑटो-रिक्शा (साझा)",
        TransportMode.PUBLIC_BUS: "पब्लिक सिटी बस",
        TransportMode.ELECTRIC_BUS: "इलेक्ट्रिक बस (e-Bus)",
        TransportMode.METRO: "मेट्रो रेल (Metro Rail)",
        TransportMode.CARPOOL: "कारपूलिंग (3-व्यक्ति साझा सफर)",
        TransportMode.WALKING: "पैदल चलना (Active Walk)",
        TransportMode.CYCLING: "साइकिल चलाना (Cycling)",
    }

    # Credible sources and reference documentation per mode
    MODE_DATA_SOURCES: Dict[TransportMode, List[str]] = {
        TransportMode.PETROL_CAR: [
            "ARAI / BEE Fuel Consumption Standards (~14.0 km/L petrol, 2310 g CO2/L): https://www.araiindia.com"
        ],
        TransportMode.DIESEL_CAR: [
            "ARAI / BEE Standards (~15.3 km/L diesel, 2680 g CO2/L): https://www.araiindia.com"
        ],
        TransportMode.TWO_WHEELER: [
            "ARAI Commuter 2-Wheeler Testing (~45 km/L, 52 g CO2/km): https://www.araiindia.com"
        ],
        TransportMode.ELECTRIC_CAR: [
            "Central Electricity Authority (CEA v19) National Grid Baseline (~716 g CO2/kWh): https://cea.nic.in/cdm-co2-baseline-database/",
            "Homologation data (~0.15 kWh/km energy consumption = 107.4 g CO2e/km)",
        ],
        TransportMode.ELECTRIC_TWO_WHEELER: [
            "CEA v19 National Grid Baseline (~716 g CO2/kWh): https://cea.nic.in/cdm-co2-baseline-database/",
            "Urban 2W EV average consumption (~0.035 kWh/km = 25.1 g CO2e/km)",
        ],
        TransportMode.CNG_AUTO: [
            "Delhi Transport Dept & ARAI 3-Wheeler Testing (~30 km/kg CNG, 2150 g CO2/kg CNG): https://transport.delhi.gov.in"
        ],
        TransportMode.PUBLIC_BUS: [
            "MoHUA Comprehensive Mobility Plan & CPCB Urban Bus Benchmarks (~1100 g CO2/km, 35 passengers): https://mohua.gov.in"
        ],
        TransportMode.ELECTRIC_BUS: [
            "CEA v19 National Grid Factor (~716 g CO2/kWh) & FAME-II STU e-bus telemetry (~1.20 kWh/km, 35 passengers): https://cea.nic.in",
        ],
        TransportMode.METRO: [
            "DMRC Annual Sustainability Report 2023-24 (~30.7 Wh/passenger-km, ~22.0 g CO2e/passenger-km): https://www.delhimetrorail.com",
            "CEA v19 Power Grid Emission Baseline: https://cea.nic.in/cdm-co2-baseline-database/",
        ],
        TransportMode.CARPOOL: [
            "ARAI Petrol Car Base (165 g/km) allocated across shared passenger pool (3 persons default = 55 g/passenger-km)"
        ],
        TransportMode.WALKING: [
            "Zero direct tailpipe emissions; active respiratory intake evaluated via CPCB AQI guidelines: https://cpcb.nic.in"
        ],
        TransportMode.CYCLING: [
            "Zero direct tailpipe emissions; minute ventilation dosage evaluated via CPCB AQI guidelines: https://cpcb.nic.in"
        ],
    }

    @classmethod
    def calculate_trip_emissions(
        cls,
        mode: TransportMode,
        distance_km: float,
        occupancy: int = 1,
    ) -> Tuple[float, float, float, float]:
        """Calculates vehicle-level direct, grid indirect, total, and per-passenger emissions in grams CO2e for a trip.

        Returns (direct_g, grid_g, total_g, per_passenger_g).
        """
        direct_factor = cls.DIRECT_EMISSION_FACTORS.get(mode, 165.0)
        grid_factor = cls.GRID_INDIRECT_FACTORS.get(mode, 0.0)

        # Vehicle-level emissions for the trip distance
        direct_g = direct_factor * distance_km
        grid_g = grid_factor * distance_km
        total_g = direct_g + grid_g

        # Determine effective passenger occupancy
        if mode in (TransportMode.PETROL_CAR, TransportMode.DIESEL_CAR, TransportMode.ELECTRIC_CAR):
            eff_occupancy = float(max(1, occupancy))
        elif mode == TransportMode.CARPOOL:
            eff_occupancy = float(max(2, occupancy if occupancy > 1 else 3))
        else:
            eff_occupancy = float(cls.DEFAULT_OCCUPANCY.get(mode, 1.0))

        per_passenger_g = total_g / eff_occupancy if eff_occupancy > 0 else total_g

        return round(direct_g, 1), round(grid_g, 1), round(total_g, 1), round(per_passenger_g, 1)

    @classmethod
    def compare_all_modes(
        cls,
        distance_km: float,
        current_mode: TransportMode,
        aqi: int,
        city: Optional[str] = None,
        language: str = "en",
        accessibility: AccessibilityNeed = AccessibilityNeed.NONE,
        occupancy: int = 1,
    ) -> List[ModeEmissionDetail]:
        """Compares all 12 transport modes against the solo private petrol car baseline with city-aware transit availability and qualified AQI exposure verdicts."""
        is_hi = language == "hi"
        labels = cls.MODE_LABELS_HI if is_hi else cls.MODE_LABELS_EN

        # Check local Metro Rail operational availability in the specified city
        has_metro, metro_status, metro_reason_en, metro_reason_hi = TransitService.check_metro_availability(city)

        # Baseline: Solo private petrol car (occupancy 1.0)
        _, _, base_total_g, _ = cls.calculate_trip_emissions(
            TransportMode.PETROL_CAR, distance_km, occupancy=1
        )

        modes_to_evaluate = [
            TransportMode.METRO,
            TransportMode.ELECTRIC_BUS,
            TransportMode.PUBLIC_BUS,
            TransportMode.CARPOOL,
            TransportMode.ELECTRIC_CAR,
            TransportMode.ELECTRIC_TWO_WHEELER,
            TransportMode.CNG_AUTO,
            TransportMode.TWO_WHEELER,
            TransportMode.PETROL_CAR,
            TransportMode.DIESEL_CAR,
            TransportMode.CYCLING,
            TransportMode.WALKING,
        ]

        results: List[ModeEmissionDetail] = []

        for mode in modes_to_evaluate:
            mode_occ = occupancy if mode == current_mode else int(cls.DEFAULT_OCCUPANCY.get(mode, 1.0))
            if mode == TransportMode.CARPOOL:
                mode_occ = max(2, occupancy if occupancy > 1 else 3)

            direct_g, grid_g, total_g, per_p_g = cls.calculate_trip_emissions(
                mode, distance_km, occupancy=mode_occ
            )

            # Check transit availability in this city
            availability_status = "available"
            if mode == TransportMode.METRO:
                if not has_metro:
                    availability_status = metro_status.value

            # Savings relative to solo petrol car baseline
            if availability_status == "available":
                savings_g = max(0.0, round(base_total_g - per_p_g, 1))
                savings_pct = round((savings_g / base_total_g * 100), 1) if base_total_g > 0 else 0.0
            else:
                # Unavailable or unverified modes do not show active savings
                savings_g = 0.0
                savings_pct = 0.0

            # AQI safety and suitability evaluation with qualified non-absolute language
            suitability, aqi_verdict, exposure, precautions = cls._evaluate_mode_aqi_safety(
                mode=mode,
                distance_km=distance_km,
                aqi=aqi,
                city=city,
                has_metro=has_metro,
                metro_status=metro_status,
                metro_reason_en=metro_reason_en,
                metro_reason_hi=metro_reason_hi,
                language=language,
                accessibility=accessibility,
            )

            data_sources = cls.MODE_DATA_SOURCES.get(mode, [])

            eff_occ = float(mode_occ) if mode in (
                TransportMode.PETROL_CAR,
                TransportMode.DIESEL_CAR,
                TransportMode.ELECTRIC_CAR,
                TransportMode.CARPOOL,
            ) else float(cls.DEFAULT_OCCUPANCY.get(mode, 1.0))

            results.append(
                ModeEmissionDetail(
                    mode=mode,
                    label=labels.get(mode, mode.value),
                    direct_emissions_g=direct_g,
                    grid_indirect_emissions_g=grid_g,
                    total_emissions_g=total_g,
                    passenger_occupancy=eff_occ,
                    per_passenger_emissions_g=per_p_g,
                    co2e_savings_vs_baseline_g=savings_g,
                    co2e_savings_pct=savings_pct,
                    suitability_score=suitability,
                    aqi_safety_verdict=aqi_verdict,
                    exposure_level=exposure,
                    precautions=precautions,
                    availability_status=availability_status,
                    data_sources=data_sources,
                )
            )

        return results

    @classmethod
    def calculate_carpooling_potential(
        cls, distance_km: float, round_trips_per_day: float = 2.0
    ) -> CarpoolEstimate:
        """Computes potential emission reductions through 2, 3, and 4-person carpooling pools."""
        solo_trip_g = round(165.0 * distance_km, 1)
        shared_2_person_g = round(solo_trip_g / 2.0, 1)
        shared_3_person_g = round(solo_trip_g / 3.0, 1)
        shared_4_person_g = round(solo_trip_g / 4.0, 1)

        daily_savings_g = (solo_trip_g - shared_3_person_g) * round_trips_per_day
        daily_savings_kg = round(daily_savings_g / 1000.0, 2)
        annual_savings_kg = round(daily_savings_kg * 250.0, 1)

        return CarpoolEstimate(
            solo_trip_emissions_g=solo_trip_g,
            shared_2_person_emissions_g=shared_2_person_g,
            shared_3_person_emissions_g=shared_3_person_g,
            shared_4_person_emissions_g=shared_4_person_g,
            daily_savings_kg=daily_savings_kg,
            annual_savings_kg=annual_savings_kg,
        )

    @classmethod
    def _evaluate_mode_aqi_safety(
        cls,
        mode: TransportMode,
        distance_km: float,
        aqi: int,
        city: Optional[str],
        has_metro: bool,
        metro_status: TransitAvailabilityStatus,
        metro_reason_en: str,
        metro_reason_hi: str,
        language: str,
        accessibility: AccessibilityNeed,
    ) -> Tuple[str, str, str, List[str]]:
        """Determines qualified health suitability, exposure level, and tailored precautions based on CPCB AQI categories and city availability.

        Guarantees:
        - Never claims any mode is 'Safe', '100% Safe', or 'Enclosed Cabin Safe'.
        - Distinguishes reduced exposure from zero exposure.
        - Follows official CPCB NAQI categories (Severe 401+, Very Poor 301-400, Poor 201-300, Moderate 101-200, Satisfactory/Good 0-100).
        """
        is_hi = language == "hi"
        city_display = city.strip() if city and city.strip() else ("शहर" if is_hi else "City")

        # 1. Metro availability handling for city
        if mode == TransportMode.METRO and not has_metro:
            if metro_status == TransitAvailabilityStatus.UNAVAILABLE:
                suitability = f"शहर में अनुपलब्ध ({city_display})" if is_hi else f"Not Available in {city_display}"
                verdict = (
                    f"{metro_reason_hi} कृपया बस या साझा कारपूलिंग जैसे सड़क विकल्पों पर विचार करें।"
                    if is_hi
                    else f"{metro_reason_en} Consider road-based public bus transit or shared carpooling."
                )
                exposure = "N/A"
                precautions = (
                    [f"{city_display} में मेट्रो रेल सेवा उपलब्ध नहीं है"]
                    if is_hi
                    else [f"Metro rail service is not operational in {city_display}"]
                )
                return suitability, verdict, exposure, precautions
            else:  # UNVERIFIED
                suitability = "उपलब्धता असत्यापित" if is_hi else "Unverified in City"
                verdict = (
                    f"{metro_reason_hi} स्थानीय सार्वजनिक नेटवर्क की पुष्टि करें।"
                    if is_hi
                    else f"{metro_reason_en} Verify local transit network availability."
                )
                exposure = "Unverified"
                precautions = (
                    ["स्थानीय परिवहन उपलब्धता की पुष्टि करें"]
                    if is_hi
                    else ["Verify local urban rail availability"]
                )
                return suitability, verdict, exposure, precautions

        # 2. CPCB Category: Severe (AQI >= 401)
        if aqi >= 401:
            if mode in (TransportMode.WALKING, TransportMode.CYCLING):
                suitability = "उच्च स्वास्थ्य जोखिम - वर्जित" if is_hi else "High Health Risk - Not Advised"
                verdict = (
                    "गंभीर प्रदूषण (AQI 401+): तीव्र शारीरिक श्रम फेफड़ों के गहराई तक PM2.5 पहुंचाता है। सक्रिय आउटडोर यात्रा पूरी तरह टालें।"
                    if is_hi
                    else "Severe Air Quality (AQI 401+): Aerobic physical exertion drives ultra-fine PM2.5 deep into alveoli. Avoid outdoor walking or cycling today."
                )
                exposure = "Severe"
                precautions = (
                    ["पैदल या साइकिल यात्रा टालें", "केवल बंद वातानुकूलित वाहन या सार्वजनिक बस चुनें"]
                    if is_hi
                    else ["Avoid outdoor active travel today", "Choose enclosed air-conditioned vehicle or bus"]
                )
            elif mode in (TransportMode.TWO_WHEELER, TransportMode.ELECTRIC_TWO_WHEELER, TransportMode.CNG_AUTO):
                suitability = "सावधानी - उच्च संपर्क" if is_hi else "Caution - High Roadside Exposure"
                verdict = (
                    "सड़क स्तर पर अत्यधिक धुआं व धूल। खुला वाहन सीधे प्रदूषक संपर्क में लाता है; बिना सीलबंद N95 मास्क यात्रा न करें।"
                    if is_hi
                    else "Extreme roadside particulate exposure; open transport offers no barrier. Certified N95 respirator mandatory."
                )
                exposure = "High"
                precautions = (
                    ["प्रमाणित N95/FFP2 मास्क अनिवार्य रूप से लगाएं", "भारी ट्रैफिक व जाम में रुकने से बचें"]
                    if is_hi
                    else ["Wear certified N95 respirator with airtight seal", "Avoid idling in heavy congestion"]
                )
            elif mode == TransportMode.METRO:
                suitability = "अनुशंसित - कम संपर्क" if is_hi else "Recommended - Lower Exposure"
                verdict = (
                    "ग्रेड-सेपरेटेड इलेक्ट्रिक कोच सड़क स्तर के सीधे धुएं को कम करते हैं (शून्य संपर्क नहीं); स्टेशन आवागमन पर N95 मास्क पहनें।"
                    if is_hi
                    else "Grade-separated electric rail reduces surface soot exposure relative to open roads (not zero exposure); wear an N95 respirator during station access."
                )
                exposure = "Moderate"
                precautions = (
                    ["स्टेशन आने-जाने और प्लेटफॉर्म पर N95 मास्क पहनें"]
                    if is_hi
                    else ["Wear N95 respirator during outdoor first/last mile station walks"]
                )
            else:  # Cars, Carpool, Buses
                suitability = "कम संपर्क विकल्प" if is_hi else "Reduced Exposure Option"
                verdict = (
                    "बंद केबिन सड़क के सीधे धुएं से संपर्क घटाता है, परंतु शून्य जोखिम की गारंटी नहीं देता। रीसर्क्युलेशन चालू रखें।"
                    if is_hi
                    else "Enclosed cabin with AC recirculation reduces particulate intake compared to open roads, but does not provide zero exposure."
                )
                exposure = "Moderate"
                precautions = (
                    ["कार एसी को रीसर्क्युलेशन मोड पर सेट करें", "खिड़कियां पूरी तरह बंद रखें"]
                    if is_hi
                    else ["Set vehicle HVAC to Recirculation Mode", "Keep all cabin windows tightly rolled up"]
                )

        # 3. CPCB Category: Very Poor (301 <= AQI <= 400)
        elif aqi >= 301:
            if mode in (TransportMode.WALKING, TransportMode.CYCLING):
                suitability = "जोखिम भरा - अनुशंसित नहीं" if is_hi else "Elevated Risk - Not Advised"
                verdict = (
                    "बहुत खराब वायु (AQI 301-400): सांस की गति तेज होने से टॉक्सिन का अवशोषण बढ़ता है। सक्रिय आवागमन टालें।"
                    if is_hi
                    else "Very Poor Air Quality (AQI 301-400): Elevated ventilation rate during exercise accelerates cumulative PM2.5 intake. Active commute not advised."
                )
                exposure = "High"
                precautions = (
                    ["सक्रिय आवागमन टालें", "बंद सार्वजनिक या साझा वाहन का चयन करें"]
                    if is_hi
                    else ["Avoid strenuous outdoor commute", "Prefer enclosed transit or rideshare"]
                )
            elif mode in (TransportMode.TWO_WHEELER, TransportMode.ELECTRIC_TWO_WHEELER, TransportMode.CNG_AUTO):
                suitability = "सावधानी" if is_hi else "Caution - Elevated Exposure"
                verdict = (
                    "सड़क स्तर पर वाहनों का धुआं व धूल। खुला सफर श्वसन तंत्र को सीधे प्रभावित करता है।"
                    if is_hi
                    else "Substantial roadside traffic soot. Unenclosed travel directly exposes upper airways."
                )
                exposure = "Moderate to High"
                precautions = (
                    ["N95 मास्क अनिवार्य", "व्यस्त घंटों में यात्रा से बचें"]
                    if is_hi
                    else ["Wear N95 respirator", "Avoid peak congestion corridors"]
                )
            elif mode == TransportMode.METRO:
                suitability = "अनुशंसित - कम संपर्क" if is_hi else "Recommended - Lower Exposure"
                verdict = (
                    "सड़क स्तर के सीधे संपर्क को कम करता है और कम कार्बन उत्सर्जन वाला साधन है।"
                    if is_hi
                    else "Lower direct roadside particulate exposure with low per-passenger carbon footprint."
                )
                exposure = "Moderate"
                precautions = (
                    ["स्टेशन के बाहर N95 मास्क पहनें"]
                    if is_hi
                    else ["Wear N95 mask during station access"]
                )
            else:
                suitability = "अनुशंसित - बंद केबिन" if is_hi else "Recommended - Enclosed Cabin"
                verdict = (
                    "बंद वाहन में रीसर्क्युलेशन मोड सड़क स्तर के सीधे धुएं के संपर्क को सीमित करता है।"
                    if is_hi
                    else "Enclosed vehicle in AC recirculation mode limits direct roadside particulate intake."
                )
                exposure = "Moderate"
                precautions = (
                    ["केबिन रीसर्क्युलेशन चालू रखें", "खिड़कियां बंद रखें"]
                    if is_hi
                    else ["Keep vehicle AC on Recirculation", "Keep windows rolled up in traffic"]
                )

        # 4. CPCB Category: Poor (201 <= AQI <= 300)
        elif aqi >= 201:
            if mode == TransportMode.WALKING:
                if distance_km <= 1.5:
                    suitability = "मध्यम - केवल छोटी दूरी" if is_hi else "Moderate - Short Trips Only"
                    verdict = (
                        "केवल 1.5 किमी से कम की आवश्यक दूरी के लिए सीमित रखें। N95 मास्क पहनें।"
                        if is_hi
                        else "Feasible only for short essential trips (< 1.5 km). N95 mask advised."
                    )
                    exposure = "Moderate"
                    precautions = (
                        ["N95 मास्क पहनें", "सुबह के इनवर्जन समय में चलने से बचें"]
                        if is_hi
                        else ["Wear N95 mask", "Avoid morning rush-hour thermal inversion"]
                    )
                else:
                    suitability = "अनुशंसित नहीं" if is_hi else "Not Advised for Long Distance"
                    verdict = (
                        "लंबी पैदल दूरी खराब वायु गुणवत्ता में फेफड़ों पर प्रदूषण का भार बढ़ाती है।"
                        if is_hi
                        else "Extended walking under poor air quality increases cumulative particulate inhalation."
                    )
                    exposure = "Moderate to High"
                    precautions = (
                        ["सार्वजनिक बस या कारपूलिंग चुनें"] if is_hi else ["Switch to transit bus or carpool"]
                    )
            elif mode == TransportMode.CYCLING:
                suitability = "सावधानी - श्रम सीमित रखें" if is_hi else "Caution - Limit Exertion"
                verdict = (
                    "साइकिल चलाते समय सांस की गति तेज होती है, जिससे प्रदूषक अधिक अंदर जाते हैं।"
                    if is_hi
                    else "Aerobic cycling increases minute ventilation, accelerating particulate intake."
                )
                exposure = "Moderate"
                precautions = (
                    ["N95 मास्क पहनें", "दोपहर में जब धूप हो तब यात्रा करें"]
                    if is_hi
                    else ["Wear breathable N95 respirator", "Prefer mid-day hours when solar heating disperses smog"]
                )
            elif mode == TransportMode.METRO:
                suitability = "अनुशंसित" if is_hi else "Recommended"
                verdict = (
                    "कम प्रति-यात्री उत्सर्जन और सड़क स्तर के धुएं से अपेक्षाकृत कम संपर्क।"
                    if is_hi
                    else "Low per-passenger emissions and lower roadside smog exposure."
                )
                exposure = "Low to Moderate"
                precautions = (
                    ["स्टेशन के बाहर मास्क पहनें"] if is_hi else ["Wear mask during outdoor access walks"]
                )
            else:
                suitability = "अनुशंसित" if is_hi else "Recommended"
                verdict = (
                    "कार्बन उत्सर्जन घटाने हेतु साझा या इलेक्ट्रिक यात्रा अपनाएं।"
                    if is_hi
                    else "Shared or electric transit significantly cuts per-passenger emissions."
                )
                exposure = "Moderate"
                precautions = (
                    ["वाहन की खिड़कियां बंद रखें"] if is_hi else ["Keep vehicle windows closed in traffic"]
                )

        # 5. CPCB Category: Moderate (101 <= AQI <= 200)
        elif aqi >= 101:
            if mode == TransportMode.WALKING and distance_km <= 2.5:
                suitability = "अनुकूल - शून्य टेलपाइप" if is_hi else "Favorable - Zero Tailpipe Emissions"
                verdict = (
                    "शून्य टेलपाइप उत्सर्जन। संवेदनशील व्यक्तियों (अस्थमा/हृदय रोगी) को अत्यधिक श्रम से बचना चाहिए।"
                    if is_hi
                    else "Zero tailpipe emissions. Sensitive individuals should moderate heavy aerobic exertion."
                )
                exposure = "Low"
                precautions = (
                    ["संवेदनशील व्यक्ति सावधानी बरतें"] if is_hi else ["Sensitive groups moderate prolonged exertion"]
                )
            elif mode == TransportMode.CYCLING and distance_km <= 8.0:
                suitability = "अनुकूल - शून्य टेलपाइप" if is_hi else "Favorable - Zero Tailpipe Emissions"
                verdict = (
                    "शून्य टेलपाइप उत्सर्जन व ऊर्जा दक्षता। व्यस्त ट्रैफिक से दूर के मार्ग चुनें।"
                    if is_hi
                    else "Zero tailpipe emissions and high efficiency. Prefer routes away from heavy diesel corridors."
                )
                exposure = "Low"
                precautions = (
                    ["हेलमेट और सुरक्षात्मक गियर पहनें"] if is_hi else ["Wear helmet and visibility gear"]
                )
            elif mode in (TransportMode.METRO, TransportMode.ELECTRIC_BUS, TransportMode.CARPOOL):
                suitability = "अनुशंसित" if is_hi else "Recommended"
                verdict = (
                    "कुशल साझा आवागमन व कम कार्बन उत्सर्जन।"
                    if is_hi
                    else "High efficiency, shared occupancy, and low urban carbon footprint."
                )
                exposure = "Low"
                precautions = []
            else:
                suitability = "सुचारु" if is_hi else "Viable Transit Option"
                verdict = (
                    "मध्यम वायु गुणवत्ता में व्यवहार्य यात्रा विकल्प।"
                    if is_hi
                    else "Viable commute option under moderate air quality."
                )
                exposure = "Low"
                precautions = []

        # 6. CPCB Category: Good to Satisfactory (AQI <= 100)
        else:
            if mode == TransportMode.WALKING and distance_km <= 3.0:
                suitability = "अनुकूल - सक्रिय आवागमन" if is_hi else "Favorable - Active Travel"
                verdict = (
                    "शून्य टेलपाइप उत्सर्जन और स्वास्थ्य के लिए अनुकूल वायु गुणवत्ता।"
                    if is_hi
                    else "Zero direct emissions with low pollution exposure risk under favorable air quality."
                )
                exposure = "Minimal"
                precautions = (
                    ["हाइड्रेटेड रहें"] if is_hi else ["Stay hydrated"]
                )
            elif mode == TransportMode.CYCLING and distance_km <= 10.0:
                suitability = "अनुकूल - सक्रिय आवागमन" if is_hi else "Favorable - Active Travel"
                verdict = (
                    "शून्य टेलपाइप उत्सर्जन और शून्य ग्रिड निर्भरता।"
                    if is_hi
                    else "Zero tailpipe emissions and zero grid reliance for short/medium commutes."
                )
                exposure = "Minimal"
                precautions = (
                    ["हेलमेट पहनें"] if is_hi else ["Wear helmet and safety gear"]
                )
            elif mode in (TransportMode.METRO, TransportMode.ELECTRIC_BUS, TransportMode.CARPOOL):
                suitability = "अनुशंसित" if is_hi else "Recommended"
                verdict = (
                    "पर्यावरण-अनुकूल व उच्च दक्षता वाला सार्वजनिक परिवहन।"
                    if is_hi
                    else "Low-emission and energy-efficient shared transit."
                )
                exposure = "Minimal"
                precautions = []
            else:
                suitability = "सुचारु" if is_hi else "Viable Transit Option"
                verdict = (
                    "स्वीकार्य यात्रा विकल्प।" if is_hi else "Viable travel option."
                )
                exposure = "Minimal"
                precautions = []

        # Accessibility adjustments
        if accessibility in (
            AccessibilityNeed.WHEELCHAIR,
            AccessibilityNeed.LOW_WALKING,
            AccessibilityNeed.SENIOR_FRIENDLY,
        ):
            if mode in (TransportMode.WALKING, TransportMode.CYCLING):
                suitability = "शारीरिक सुगमता हेतु अनुपयुक्त" if is_hi else "Not Accessible"
                precautions.append(
                    "शारीरिक सुगमता प्रतिबंधों के कारण सक्रिय यात्रा उपयुक्त नहीं है।"
                    if is_hi
                    else "Active walking/cycling does not meet accessibility requirements."
                )

        return suitability, verdict, exposure, precautions
