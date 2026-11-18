from typing import Dict, List, Tuple
from backend.app.models.mobility import (
    AccessibilityNeed,
    CarpoolEstimate,
    CommuteFrequency,
    CommutePurpose,
    ModeEmissionDetail,
    TransportMode,
)


class EmissionsService:
    """Transparent, scientifically-grounded transport emission calculator.

    Emission factors are modeled using CEA (Central Electricity Authority, India v19 CO2 baseline:
    ~716 g CO2/kWh), ARAI vehicle fuel economy averages, and CPCB urban transit benchmarks.

    All outputs are explicitly labeled as modeled engineering calculations, not physical in-situ measurements.
    """

    # Direct (tailpipe) emissions in g CO2e / vehicle-km
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

    # Upstream electricity grid indirect emissions in g CO2e / vehicle-km (or passenger-km for rail)
    # India Grid Emission Factor ~716 g CO2/kWh:
    # - 4W EV: ~0.15 kWh/km * 716 = 107.4 g CO2e / km
    # - 2W EV: ~0.035 kWh/km * 716 = 25.1 g CO2e / km
    # - e-Bus: ~1.20 kWh/km * 716 = 859.2 g CO2e / km
    # - Metro: ~22.0 g CO2e / passenger-km
    GRID_INDIRECT_FACTORS: Dict[TransportMode, float] = {
        TransportMode.PETROL_CAR: 0.0,
        TransportMode.DIESEL_CAR: 0.0,
        TransportMode.TWO_WHEELER: 0.0,
        TransportMode.ELECTRIC_CAR: 107.4,
        TransportMode.ELECTRIC_TWO_WHEELER: 25.1,
        TransportMode.CNG_AUTO: 0.0,
        TransportMode.PUBLIC_BUS: 0.0,
        TransportMode.ELECTRIC_BUS: 859.2,
        TransportMode.METRO: 22.0,
        TransportMode.CARPOOL: 0.0,
        TransportMode.WALKING: 0.0,
        TransportMode.CYCLING: 0.0,
    }

    # Standard modeled passenger occupancy
    DEFAULT_OCCUPANCY: Dict[TransportMode, float] = {
        TransportMode.PETROL_CAR: 1.2,
        TransportMode.DIESEL_CAR: 1.2,
        TransportMode.TWO_WHEELER: 1.0,
        TransportMode.ELECTRIC_CAR: 1.5,
        TransportMode.ELECTRIC_TWO_WHEELER: 1.0,
        TransportMode.CNG_AUTO: 2.0,
        TransportMode.PUBLIC_BUS: 35.0,
        TransportMode.ELECTRIC_BUS: 35.0,
        TransportMode.METRO: 1.0,  # factor already expressed per passenger-km
        TransportMode.CARPOOL: 3.0,
        TransportMode.WALKING: 1.0,
        TransportMode.CYCLING: 1.0,
    }

    MODE_LABELS_EN: Dict[TransportMode, str] = {
        TransportMode.PETROL_CAR: "Private Petrol Car",
        TransportMode.DIESEL_CAR: "Private Diesel Car",
        TransportMode.TWO_WHEELER: "Petrol Two-Wheeler (Bike/Scooter)",
        TransportMode.ELECTRIC_CAR: "Electric Car (EV)",
        TransportMode.ELECTRIC_TWO_WHEELER: "Electric Scooter (e-2W)",
        TransportMode.CNG_AUTO: "Shared CNG Auto-Rickshaw",
        TransportMode.PUBLIC_BUS: "Public City Bus (CNG/Diesel)",
        TransportMode.ELECTRIC_BUS: "Electric City Bus (e-Bus)",
        TransportMode.METRO: "Urban Metro Rail",
        TransportMode.CARPOOL: "Shared Carpooling (3-person)",
        TransportMode.WALKING: "Active Walking",
        TransportMode.CYCLING: "Active Cycling",
    }

    MODE_LABELS_HI: Dict[TransportMode, str] = {
        TransportMode.PETROL_CAR: "निजी पेट्रोल कार (Solo Car)",
        TransportMode.DIESEL_CAR: "निजी डीजल कार",
        TransportMode.TWO_WHEELER: "पेट्रोल दोपहिया (बाइक/स्कूटर)",
        TransportMode.ELECTRIC_CAR: "इलेक्ट्रिक कार (EV)",
        TransportMode.ELECTRIC_TWO_WHEELER: "इलेक्ट्रिक स्कूटर (e-2W)",
        TransportMode.CNG_AUTO: "सीएनजी ऑटो-रिक्शा",
        TransportMode.PUBLIC_BUS: "पब्लिक सिटी बस",
        TransportMode.ELECTRIC_BUS: "इलेक्ट्रिक बस (e-Bus)",
        TransportMode.METRO: "मेट्रो रेल (Metro Rail)",
        TransportMode.CARPOOL: "कारपूलिंग (3-व्यक्ति साझा सफर)",
        TransportMode.WALKING: "पैदल चलना (Active Walk)",
        TransportMode.CYCLING: "साइकिल चलाना (Cycling)",
    }

    @classmethod
    def calculate_trip_emissions(
        cls,
        mode: TransportMode,
        distance_km: float,
        occupancy: int = 1,
    ) -> Tuple[float, float, float, float]:
        """Calculates direct, grid indirect, total, and per-passenger emissions in grams CO2e for a trip.

        Returns (direct_g, grid_g, total_g, per_passenger_g).
        """
        direct_factor = cls.DIRECT_EMISSION_FACTORS.get(mode, 165.0)
        grid_factor = cls.GRID_INDIRECT_FACTORS.get(mode, 0.0)

        # Vehicle-level emissions for the distance
        direct_g = direct_factor * distance_km
        grid_g = grid_factor * distance_km
        total_g = direct_g + grid_g

        # Determine effective passenger occupancy
        if mode == TransportMode.PETROL_CAR or mode == TransportMode.DIESEL_CAR:
            eff_occupancy = max(1, occupancy)
        elif mode == TransportMode.CARPOOL:
            eff_occupancy = max(2, occupancy if occupancy > 1 else 3)
        else:
            eff_occupancy = cls.DEFAULT_OCCUPANCY.get(mode, 1.0)

        per_passenger_g = total_g / eff_occupancy if eff_occupancy > 0 else total_g

        return round(direct_g, 1), round(grid_g, 1), round(total_g, 1), round(per_passenger_g, 1)

    @classmethod
    def compare_all_modes(
        cls,
        distance_km: float,
        current_mode: TransportMode,
        aqi: int,
        language: str = "en",
        accessibility: AccessibilityNeed = AccessibilityNeed.NONE,
        occupancy: int = 1,
    ) -> List[ModeEmissionDetail]:
        """Compares all 12 transport modes against the private petrol car baseline with AQI-aware health safety verdicts."""
        is_hi = language == "hi"
        labels = cls.MODE_LABELS_HI if is_hi else cls.MODE_LABELS_EN

        # Baseline: Solo private petrol car
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
            direct_g, grid_g, total_g, per_p_g = cls.calculate_trip_emissions(
                mode, distance_km, occupancy=occupancy if mode == current_mode else 1
            )

            # Savings relative to solo petrol car baseline
            savings_g = max(0.0, round(base_total_g - per_p_g, 1))
            savings_pct = round((savings_g / base_total_g * 100), 1) if base_total_g > 0 else 0.0

            # AQI safety and suitability evaluation
            suitability, aqi_verdict, exposure, precautions = cls._evaluate_mode_aqi_safety(
                mode, distance_km, aqi, language, accessibility
            )

            results.append(
                ModeEmissionDetail(
                    mode=mode,
                    label=labels.get(mode, mode.value),
                    direct_emissions_g=direct_g,
                    grid_indirect_emissions_g=grid_g,
                    total_emissions_g=total_g,
                    per_passenger_emissions_g=per_p_g,
                    co2e_savings_vs_baseline_g=savings_g,
                    co2e_savings_pct=savings_pct,
                    suitability_score=suitability,
                    aqi_safety_verdict=aqi_verdict,
                    exposure_level=exposure,
                    precautions=precautions,
                )
            )

        return results

    @classmethod
    def calculate_carpooling_potential(
        cls, distance_km: float, round_trips_per_day: float = 2.0
    ) -> CarpoolEstimate:
        """Computes potential emission reductions through 2, 3, and 4-person carpooling pools."""
        # 165 g CO2e / km for private petrol car
        solo_trip_g = round(165.0 * distance_km, 1)
        shared_2_person_g = round(solo_trip_g / 2.0, 1)
        shared_3_person_g = round(solo_trip_g / 3.0, 1)
        shared_4_person_g = round(solo_trip_g / 4.0, 1)

        # Daily savings for 3-person pool (avoiding 2 solo cars)
        # Net savings per person per day = (solo_trip_g - shared_3_person_g) * round_trips_per_day
        daily_savings_g = (solo_trip_g - shared_3_person_g) * round_trips_per_day
        daily_savings_kg = round(daily_savings_g / 1000.0, 2)
        annual_savings_kg = round(daily_savings_kg * 250.0, 1)  # 250 work days

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
        language: str,
        accessibility: AccessibilityNeed,
    ) -> Tuple[str, str, str, List[str]]:
        """Determines health suitability, exposure score, and tailored precautions based on AQI and accessibility."""
        is_hi = language == "hi"

        # Severe Smog Condition (AQI >= 301)
        if aqi >= 301:
            if mode in (TransportMode.WALKING, TransportMode.CYCLING):
                suitability = "आज वर्जित (Restricted)" if is_hi else "Not Advised Today"
                verdict = (
                    "अत्यधिक स्मॉग जोखिम: गहरी सांस लेने से PM2.5 फेफड़ों में गहराई तक समा जाता है।"
                    if is_hi
                    else "Critical Smog Hazard: Rapid ventilation deposits ultra-fine PM2.5 directly into alveolar air-sacs."
                )
                exposure = "Severe"
                precautions = (
                    ["पैदल या साइकिल यात्रा टालें", "केवल बंद वातानुकूलित वाहन या मेट्रो चुनें"]
                    if is_hi
                    else ["Avoid active outdoor transit today", "Prioritize enclosed air-conditioned metro or bus"]
                )
            elif mode in (TransportMode.TWO_WHEELER, TransportMode.ELECTRIC_TWO_WHEELER, TransportMode.CNG_AUTO):
                suitability = "सावधानी (Caution)" if is_hi else "Caution - High Exposure"
                verdict = (
                    "सड़क स्तर पर अत्यधिक धुआं व धूल जोखिम। बिना मास्क यात्रा न करें।"
                    if is_hi
                    else "High roadside particulate exposure; exhaust soot trapped near ground level."
                )
                exposure = "High"
                precautions = (
                    ["प्रमाणित N95/FFP2 मास्क अनिवार्य रूप से पहनें", "व्यस्त चौराहों पर रुमाल की जगह सील मास्क लगाएं"]
                    if is_hi
                    else ["Wear certified N95 respirator with airtight seal", "Avoid idling in heavy diesel queues"]
                )
            elif mode in (TransportMode.METRO,):
                suitability = "सर्वोत्तम (Optimal)" if is_hi else "Optimal Today"
                verdict = (
                    "भूमिगत व वातानुकूलित कोच सड़क स्तर के जहरीले स्मॉग से सुरक्षा प्रदान करते हैं।"
                    if is_hi
                    else "Enclosed, grade-separated electric transit bypasses dangerous surface smog inversions."
                )
                exposure = "Low"
                precautions = (
                    ["स्टेशन तक पहुंचने और निकलने के दौरान N95 मास्क पहनें"]
                    if is_hi
                    else ["Wear N95 respirator during first/last mile station walk"]
                )
            else:
                suitability = "अनुशंसित (Recommended)" if is_hi else "Recommended"
                verdict = (
                    "बंद केबिन में एयर रीसर्क्युलेशन चालू रखें।"
                    if is_hi
                    else "Enclosed vehicle protects against wind-driven particulate when windows stay sealed."
                )
                exposure = "Moderate"
                precautions = (
                    ["कार एसी को रीसर्क्युलेशन मोड पर सेट करें", "खिड़कियां पूरी तरह बंद रखें"]
                    if is_hi
                    else ["Set vehicle HVAC to Recirculation Mode", "Keep all cabin windows tightly rolled up"]
                )

        # Poor to Very Poor Smog (201 <= AQI <= 300)
        elif aqi >= 201:
            if mode == TransportMode.WALKING:
                if distance_km <= 1.5:
                    suitability = "मध्यम (Moderate)" if is_hi else "Moderate - Short Only"
                    verdict = (
                        "केवल 1.5 किमी से कम की आवश्यक दूरी के लिए सीमित रखें। N95 मास्क पहनें।"
                        if is_hi
                        else "Feasible only for short essential trips (< 1.5 km). N95 mask required."
                    )
                    exposure = "Moderate"
                    precautions = (
                        ["N95 मास्क अनिवार्य", "सुबह 7 से 10 बजे के इनवर्जन समय में चलने से बचें"]
                        if is_hi
                        else ["N95 mask mandatory", "Avoid walking during morning rush-hour thermal inversion"]
                    )
                else:
                    suitability = "वर्जित (Restricted)" if is_hi else "Not Advised"
                    verdict = (
                        "लंबी पैदल दूरी फेफड़ों पर प्रदूषण का भार बढ़ाती है।"
                        if is_hi
                        else "Walking long distances under high AQI leads to elevated cumulative PM2.5 intake."
                    )
                    exposure = "High"
                    precautions = (
                        ["पब्लिक बस या मेट्रो का उपयोग करें"] if is_hi else ["Switch to metro or transit bus"]
                    )
            elif mode == TransportMode.CYCLING:
                suitability = "सावधानी (Caution)" if is_hi else "Caution - Limit Exertion"
                verdict = (
                    "साइकिल चलाते समय सांस की गति तेज होती है, जिससे प्रदूषक अधिक अंदर जाते हैं।"
                    if is_hi
                    else "Aerobic cycling increases minute ventilation rate, accelerating toxin inhalation."
                )
                exposure = "High"
                precautions = (
                    ["बिना N95 मास्क साइकिल न चलाएं", "दोपहर में जब धूप हो तब यात्रा करें"]
                    if is_hi
                    else ["Wear breathable N95 respirator", "Prefer mid-day hours when solar heating disperses smog"]
                )
            elif mode == TransportMode.METRO:
                suitability = "सर्वोत्तम (Optimal)" if is_hi else "Optimal"
                verdict = (
                    "पर्यावरण व स्वास्थ्य दोनों के लिए सबसे सुरक्षित विकल्प।"
                    if is_hi
                    else "Lowest per-passenger emissions and shielded from outdoor particulate exposure."
                )
                exposure = "Low"
                precautions = (
                    ["स्टेशन के बाहर N95 मास्क पहनें"] if is_hi else ["Wear N95 mask during outdoor access walks"]
                )
            else:
                suitability = "अनुशंसित (Recommended)" if is_hi else "Recommended"
                verdict = (
                    "कार्बन उत्सर्जन घटाने हेतु साझा यात्रा अपनाएं।"
                    if is_hi
                    else "Shared or electric transit significantly cuts per-passenger urban pollution."
                )
                exposure = "Moderate"
                precautions = (
                    ["वाहन की खिड़कियां बंद रखें"] if is_hi else ["Keep vehicle windows closed in traffic"]
                )

        # Moderate, Satisfactory, Good (AQI <= 200)
        else:
            if mode == TransportMode.WALKING and distance_km <= 2.5:
                suitability = "सर्वोत्तम (Optimal)" if is_hi else "Optimal - Zero Emissions"
                verdict = (
                    "शून्य उत्सर्जन और स्वास्थ्य के लिए उत्तम।"
                    if is_hi
                    else "Zero direct emissions and beneficial active physical activity."
                )
                exposure = "Low"
                precautions = (
                    ["धूप व हाइड्रेशन का ध्यान रखें"] if is_hi else ["Stay hydrated"]
                )
            elif mode == TransportMode.CYCLING and distance_km <= 8.0:
                suitability = "सर्वोत्तम (Optimal)" if is_hi else "Optimal - Zero Emissions"
                verdict = (
                    "स्वच्छ और शून्य-उत्सर्जन आवागमन।"
                    if is_hi
                    else "Zero tailpipe emissions and zero grid reliance for short/medium commutes."
                )
                exposure = "Low"
                precautions = (
                    ["हेलमेट और परावर्तक जैकेट पहनें"] if is_hi else ["Wear helmet and high-visibility gear"]
                )
            elif mode in (TransportMode.METRO, TransportMode.ELECTRIC_BUS, TransportMode.CARPOOL):
                suitability = "सर्वोत्तम (Optimal)" if is_hi else "Optimal"
                verdict = (
                    "न्यूनतम कार्बन पदचिह्न और कुशल सार्वजनिक परिवहन।"
                    if is_hi
                    else "High efficiency, shared occupancy, and low urban carbon footprint."
                )
                exposure = "Low"
                precautions = []
            else:
                suitability = "अनुशंसित (Recommended)" if is_hi else "Recommended"
                verdict = (
                    "सुचारु यात्रा विकल्प।" if is_hi else "Viable travel option."
                )
                exposure = "Low"
                precautions = []

        # Accessibility adjustments
        if accessibility in (AccessibilityNeed.WHEELCHAIR, AccessibilityNeed.LOW_WALKING, AccessibilityNeed.SENIOR_FRIENDLY):
            if mode in (TransportMode.WALKING, TransportMode.CYCLING):
                suitability = "अनुपयुक्त (Not Suitable)" if is_hi else "Not Accessible"
                precautions.append(
                    "शारीरिक सुगमता प्रतिबंधों के कारण सक्रिय यात्रा उपयुक्त नहीं है।"
                    if is_hi
                    else "Active walking/cycling does not meet accessibility requirements."
                )

        return suitability, verdict, exposure, precautions
