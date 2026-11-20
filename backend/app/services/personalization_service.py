"""Personalization and Household Exposure-Reduction Recommendation Engine for AirSaathi AI.

Generates deterministic, scientifically grounded exposure-reduction recommendations
based strictly on:
1. Available ambient air quality telemetry (CurrentAqiResponse).
2. Saved household demographics and environmental preferences (FamilyPreferencesData).
3. Configured clean-air infrastructure assets (HEPA purifier, kitchen exhaust, indoor monitor).

Core domain and safety principles:
- Transparent data provenance: distinguishes live CPCB data from demo/fallback baselines.
- Zero data fabrication: missing telemetry returns an explicit unavailable state.
- No medical claims: provides atmospheric exposure reduction advice, never diagnosis or treatment.
- Non-interference: alert thresholds never alter official AQI readings or CPCB categories.
"""

from datetime import datetime
import logging
from typing import Any, Dict, List, Optional

from backend.app.models.aqi import CurrentAqiResponse
from backend.app.models.user import (
    AlertThresholdPreference,
    FamilyPreferencesData,
    PersonalizedActionItem,
    PersonalizedAdvisoryResponse,
)
from backend.app.services.live_aqi_provider import get_active_aqi_provider

logger = logging.getLogger(__name__)

DISCLAIMER_TEXT = (
    "AirSaathi provides atmospheric exposure-mitigation guidance based on ambient air quality. "
    "This is not medical diagnosis, clinical treatment, or a health guarantee."
)


class PersonalizationService:
    """Deterministic household environmental personalization engine."""

    @classmethod
    def generate_advisory(
        cls,
        family: FamilyPreferencesData,
        aqi_data: Optional[CurrentAqiResponse] = None,
        station_id: Optional[str] = None,
    ) -> PersonalizedAdvisoryResponse:
        """
        Generate personalized household exposure-reduction recommendations.

        If aqi_data is not provided, attempts to retrieve it using station_id.
        If reliable AQI data cannot be retrieved, returns an explicit unavailable state.
        """
        # 1. Resolve ambient air quality data if not provided
        if aqi_data is None and station_id:
            try:
                provider = get_active_aqi_provider()
                aqi_data = provider.get_current_aqi(station_id)
            except Exception as exc:
                logger.warning(f"Failed to retrieve AQI for station {station_id}: {exc}")
                aqi_data = None

        # 2. Handle missing or invalid AQI telemetry
        if aqi_data is None or aqi_data.aqi is None or aqi_data.aqi < 0:
            return PersonalizedAdvisoryResponse(
                status="unavailable",
                station_id=station_id,
                station_name=None,
                city=None,
                aqi=None,
                category=None,
                prominent_pollutant=None,
                data_source="Unavailable",
                is_demo_data=False,
                observed_at=None,
                threshold_applied=family.preferences.alert_threshold,
                household_size=family.household_size,
                actions=[
                    PersonalizedActionItem(
                        category="general",
                        priority="advisory",
                        title="Air Quality Telemetry Unavailable",
                        description="Reliable ambient air quality telemetry could not be retrieved for this location. Personalized smog guidance cannot be evaluated.",
                        target_group="all",
                        rationale="Personalized recommendations require verified ambient atmospheric readings.",
                    )
                ],
                active_safeguards=cls._build_active_safeguards(family),
                equipment_status=cls._extract_equipment_status(family),
                disclaimer=DISCLAIMER_TEXT,
            )

        # 3. Extract verified ambient context
        aqi = aqi_data.aqi
        category_str = (
            aqi_data.category.value
            if hasattr(aqi_data.category, "value")
            else str(aqi_data.category)
        )
        threshold = family.preferences.alert_threshold

        # 4. Determine elevated alert state based on household sensitivity threshold
        # SENSITIVE: trigger elevated caution when AQI > 100 (Moderate)
        # STANDARD: trigger elevated caution when AQI > 200 (Poor)
        # HIGH_TOLERANCE: trigger elevated caution when AQI > 300 (Very Poor)
        is_elevated_alert = False
        if threshold == AlertThresholdPreference.SENSITIVE and aqi > 100:
            is_elevated_alert = True
        elif threshold == AlertThresholdPreference.STANDARD and aqi > 200:
            is_elevated_alert = True
        elif threshold == AlertThresholdPreference.HIGH_TOLERANCE and aqi > 300:
            is_elevated_alert = True

        actions: List[PersonalizedActionItem] = []

        # 5. Demographic-Specific Exposure-Reduction Actions
        # A. Infants (0 - 2 yrs)
        if family.demographics.has_infants:
            if aqi > 100 or is_elevated_alert:
                actions.append(
                    PersonalizedActionItem(
                        category="demographic",
                        priority="urgent" if aqi > 200 else "caution",
                        title="Infant Respiratory Shield",
                        description="Keep infants in filtered indoor air. Avoid stroller transit outdoors near roadways as tailpipe particulate concentration at 0.5m-1m above ground is up to 3x higher.",
                        target_group="infants",
                        rationale="Infants have immature nasal filtration and breathe more air per unit body weight than adults.",
                    )
                )
            else:
                actions.append(
                    PersonalizedActionItem(
                        category="demographic",
                        priority="good",
                        title="Infant Outdoor Air Quality Normal",
                        description="Current ambient air quality is within acceptable limits. Standard gentle outdoor exposure and room ventilation are appropriate.",
                        target_group="infants",
                        rationale="Ambient particulate levels currently do not exceed infant sensitivity thresholds.",
                    )
                )

        # B. Children (3 - 11 yrs) - from demographics or legacy vulnerability
        has_children = family.demographics.has_children or family.vulnerability.has_children
        if has_children:
            if aqi > 200 or is_elevated_alert:
                if family.preferences.school_commute_active:
                    actions.append(
                        PersonalizedActionItem(
                            category="demographic",
                            priority="urgent" if aqi > 300 else "caution",
                            title="Pediatric Commute & School Exposure Mitigation",
                            description="Limit outdoor exposure duration during school commutes when pollution is elevated. Request schools move outdoor morning assemblies and physical activities indoors. If outdoor exposure is unavoidable, consider age-appropriate, comfortable particulate filtration masks with adult supervision.",
                            target_group="children",
                            rationale="Children breathe more air per unit body weight than adults and their developing airways are more susceptible to particulate-induced inflammation.",
                        )
                    )
                else:
                    actions.append(
                        PersonalizedActionItem(
                            category="demographic",
                            priority="caution",
                            title="Limit Vigorous Outdoor Play",
                            description="Substitute strenuous outdoor sports with indoor activities. High minute-ventilation during running increases deep-lung PM2.5 deposition.",
                            target_group="children",
                            rationale="Children's airways are narrower and more susceptible to particulate-induced inflammation.",
                        )
                    )

        # C. Seniors (60+ yrs) - from demographics or legacy vulnerability
        has_seniors = family.demographics.has_seniors or family.vulnerability.has_seniors
        if has_seniors:
            if aqi > 200 or is_elevated_alert:
                if family.preferences.morning_outdoor_window:
                    actions.append(
                        PersonalizedActionItem(
                            category="demographic",
                            priority="urgent" if aqi > 300 else "caution",
                            title="Senior Outdoor Activity Exposure Caution",
                            description="During periods of elevated morning pollution, consider reducing the duration of outdoor walks or shifting to indoor stretching and exercise. Check localized real-time AQI before planning outdoor activities.",
                            target_group="seniors",
                            rationale="Elevated particulate matter can exacerbate cardiovascular and respiratory strain in older adults with reduced mucociliary clearance.",
                        )
                    )
                else:
                    actions.append(
                        PersonalizedActionItem(
                            category="demographic",
                            priority="caution",
                            title="Senior Cardiovascular Safeguard",
                            description="Remain in aerated indoor spaces with low particulate load. Keep routine prescriptions accessible.",
                            target_group="seniors",
                            rationale="Elderly airways have reduced mucociliary clearance efficiency.",
                        )
                    )

        # D. Respiratory Sensitivity (Asthma / Bronchitis / Allergy)
        if family.vulnerability.has_respiratory_condition:
            if aqi > 100 or is_elevated_alert:
                actions.append(
                    PersonalizedActionItem(
                        category="demographic",
                        priority="urgent" if aqi > 250 else "caution",
                        title="Respiratory Exposure Mitigation",
                        description="Follow your physician-prescribed management plan and keep prescribed routine respiratory medications readily accessible. Minimize prolonged or strenuous outdoor physical exertion during elevated smog episodes.",
                        target_group="respiratory_sensitive",
                        rationale="Inhaled fine particulate matter (PM2.5) can irritate airway passages and exacerbate existing respiratory sensitivity.",
                    )
                )

        # E. Pregnancy
        if family.vulnerability.is_pregnant:
            if aqi > 150 or is_elevated_alert:
                actions.append(
                    PersonalizedActionItem(
                        category="demographic",
                        priority="caution",
                        title="Prenatal Exposure Mitigation",
                        description="Avoid walking along congested traffic corridors with diesel exhaust. Spend high-smog periods in HEPA-filtered indoor environments.",
                        target_group="pregnant",
                        rationale="Systemic inflammation from inhaled fine particulates can elevate maternal cardiovascular load.",
                    )
                )

        # F. Adults
        if family.demographics.has_adults and aqi > 300:
            actions.append(
                PersonalizedActionItem(
                    category="demographic",
                    priority="caution",
                    title="Avoid Intense Outdoor Workouts",
                    description="Avoid outdoor running or intense cardiovascular workouts during Severe smog. Move exercise indoors.",
                    target_group="adults",
                    rationale="High-intensity cardiovascular exertion switches breathing to oral inhalation, bypassing nasal particulate filtration.",
                )
            )

        # 6. Clean-Air Infrastructure & Home Asset Actions
        # A. HEPA Purifier
        if family.preferences.has_hepa_purifier:
            if aqi > 150:
                actions.append(
                    PersonalizedActionItem(
                        category="indoor_asset",
                        priority="urgent" if aqi > 300 else "advisory",
                        title="Prioritize HEPA Air Filtration Indoors",
                        description="Prioritize operating your HEPA air purifier in frequently occupied rooms (especially bedrooms during rest), keeping exterior doors and windows closed during elevated outdoor pollution episodes.",
                        target_group="all",
                        rationale="Mechanical True HEPA filtration captures airborne particulate matter (PM2.5) down to 0.3 microns.",
                    )
                )
            else:
                actions.append(
                    PersonalizedActionItem(
                        category="indoor_asset",
                        priority="good",
                        title="Operate Air Filtration as Needed",
                        description="Outdoor air quality is within acceptable or moderate limits. Operate your air purifier as needed in occupied rooms while maintaining sensible indoor ventilation.",
                        target_group="all",
                        rationale="Lower ambient particulate infiltration reduces the immediate demand on indoor air cleaning.",
                    )
                )
        elif aqi > 200:
            actions.append(
                PersonalizedActionItem(
                    category="indoor_asset",
                    priority="advisory",
                    title="Consider Mechanical Air Filtration",
                    description="Outdoor air is Poor or worse and your household has no HEPA purifier recorded. Consider mechanical filtration for primary occupied rooms.",
                    target_group="all",
                    rationale="Without active filtration, indoor particulate levels typically equilibrate to 50-70% of outdoor ambient smog.",
                )
            )

        # B. Kitchen Exhaust / Chimney
        if family.preferences.has_kitchen_exhaust:
            if aqi > 250:
                actions.append(
                    PersonalizedActionItem(
                        category="indoor_asset",
                        priority="advisory",
                        title="Operate Kitchen Exhaust with Interior Isolation",
                        description="Engage kitchen exhaust or chimney during cooking (especially for frying or tadka). Keep interior kitchen doors closed to prevent cooking aerosols from migrating into living/sleeping quarters, while avoiding opening windows facing heavy outdoor smog.",
                        target_group="all",
                        rationale="Cooking emissions generate indoor PM2.5 and volatile compounds; isolating the kitchen minimizes aerosol distribution when outdoor air is heavily polluted.",
                    )
                )
            else:
                actions.append(
                    PersonalizedActionItem(
                        category="indoor_asset",
                        priority="advisory",
                        title="Engage Kitchen Exhaust During Cooking",
                        description="Turn on ducted kitchen exhaust or chimney during cooking, particularly when frying or tempering spices.",
                        target_group="all",
                        rationale="Cooking oils and gas burners generate indoor spikes of fine particulates and combustion byproducts.",
                    )
                )
        else:
            if aqi > 250:
                actions.append(
                    PersonalizedActionItem(
                        category="indoor_asset",
                        priority="caution",
                        title="Isolate Kitchen During Cooking",
                        description="Your household does not have ducted exhaust recorded. Because outdoor pollution is elevated, avoid opening exterior windows that admit outdoor smog; instead, keep interior doors closed to prevent fumes from spreading to living and sleeping spaces.",
                        target_group="all",
                        rationale="Unvented cooking generates significant indoor particulates, but admitting heavily polluted outdoor air compounds total household exposure.",
                    )
                )
            else:
                actions.append(
                    PersonalizedActionItem(
                        category="indoor_asset",
                        priority="caution",
                        title="Ensure Moderate Kitchen Cross-Ventilation",
                        description="Your household has no ducted kitchen exhaust recorded. When outdoor air is acceptable, ensure adequate cross-ventilation during cooking to vent smoke and grease aerosols outdoors.",
                        target_group="all",
                        rationale="Unvented indoor cooking without ventilation can elevate localized particulate levels.",
                    )
                )

        # C. Indoor Air Monitor
        if family.preferences.has_indoor_monitor:
            actions.append(
                PersonalizedActionItem(
                    category="indoor_asset",
                    priority="good",
                    title="Verify Indoor/Outdoor Protection Ratio",
                    description=f"Compare your indoor monitor's real-time PM2.5 reading against the outdoor station ({aqi_data.station.name}: AQI {aqi}) to verify home sealing effectiveness.",
                    target_group="all",
                    rationale="An effective indoor protective envelope maintains indoor PM2.5 at less than 30% of ambient outdoor levels.",
                )
            )

        # 7. Commute & Mobility Actions
        transit_mode = family.preferences.preferred_transit_mode.lower()
        if transit_mode in ("public_transit", "metro", "electric_bus", "bus"):
            mode_display = "Public Transit" if transit_mode == "public_transit" else family.preferences.preferred_transit_mode.title()
            actions.append(
                PersonalizedActionItem(
                    category="commute",
                    priority="good",
                    title=f"Enclosed Transit Preferred ({mode_display})",
                    description=f"Using enclosed {mode_display.lower()} options reduces direct roadside exhaust inhalation compared to open two-wheelers or three-wheelers.",
                    target_group="all",
                    rationale="Enclosed transit vehicles with cabin air filtration offer lower direct particulate exposure than open-air roadway micro-environments.",
                )
            )
        elif transit_mode in ("walking", "cycling") and aqi > 200:
            actions.append(
                PersonalizedActionItem(
                    category="commute",
                    priority="urgent" if aqi > 300 else "caution",
                    title="Active Commute Smog Warning",
                    description=f"Your preferred mode is {family.preferences.preferred_transit_mode}. At current AQI ({aqi}), strenuous active travel significantly increases lung-deposited particulate mass. Consider enclosed transit or wearing a sealed N95 mask.",
                    target_group="all",
                    rationale="Ventilation rates during active cycling or walking increase 2-3x, overcoming upper respiratory defense barriers.",
                )
            )

        if family.preferences.office_commute_active:
            actions.append(
                PersonalizedActionItem(
                    category="commute",
                    priority="advisory",
                    title="Office Commute Cabin Sealing",
                    description="Keep vehicle windows rolled up and switch AC to 'Recirculation' mode during peak commute traffic.",
                    target_group="all",
                    rationale="Cabin air recirculation prevents incoming roadway NO2 and diesel soot from infiltrating vehicle interiors.",
                )
            )

        # 8. Assemble response
        return PersonalizedAdvisoryResponse(
            status="active",
            station_id=aqi_data.station.id,
            station_name=aqi_data.station.name,
            city=aqi_data.station.city,
            aqi=aqi,
            category=category_str,
            prominent_pollutant=aqi_data.prominent_pollutant,
            data_source=aqi_data.data_source,
            is_demo_data=aqi_data.is_demo_data,
            observed_at=aqi_data.last_updated,
            threshold_applied=threshold,
            household_size=family.household_size,
            actions=actions,
            active_safeguards=cls._build_active_safeguards(family),
            equipment_status=cls._extract_equipment_status(family),
            disclaimer=DISCLAIMER_TEXT,
        )

    @staticmethod
    def _build_active_safeguards(family: FamilyPreferencesData) -> List[str]:
        safeguards: List[str] = []
        if family.demographics.has_infants:
            safeguards.append("Infant Respiratory Shield")
        if family.demographics.has_children or family.vulnerability.has_children:
            safeguards.append("Pediatric Airway Safeguard")
        if family.demographics.has_seniors or family.vulnerability.has_seniors:
            safeguards.append("Senior Cardiovascular Safeguard")
        if family.vulnerability.has_respiratory_condition:
            safeguards.append("Asthma & Allergy Preparedness")
        if family.vulnerability.is_pregnant:
            safeguards.append("Prenatal Care Shield")
        if family.preferences.has_hepa_purifier:
            safeguards.append("HEPA Indoor Filtration")
        if family.preferences.has_kitchen_exhaust:
            safeguards.append("Kitchen Exhaust Active")
        if family.preferences.has_indoor_monitor:
            safeguards.append("Indoor Telemetry Verification")
        if family.preferences.preferred_transit_mode in ("public_transit", "metro", "electric_bus", "bus"):
            safeguards.append("Enclosed Transit Priority")
        return safeguards

    @staticmethod
    def _extract_equipment_status(family: FamilyPreferencesData) -> Dict[str, Any]:
        return {
            "has_hepa_purifier": family.preferences.has_hepa_purifier,
            "has_kitchen_exhaust": family.preferences.has_kitchen_exhaust,
            "has_indoor_monitor": family.preferences.has_indoor_monitor,
            "preferred_transit_mode": family.preferences.preferred_transit_mode,
            "alert_threshold": family.preferences.alert_threshold.value
            if hasattr(family.preferences.alert_threshold, "value")
            else str(family.preferences.alert_threshold),
        }
