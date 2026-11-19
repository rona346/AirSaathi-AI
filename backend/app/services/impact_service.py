"""Environmental Impact Calculation Engine & Service for AirSaathi AI (Module 6).

Responsible for:
1. Translating personal commute and lifestyle activities into verified CO2e impact metrics.
2. Reusing EmissionsService benchmarks without factor duplication.
3. Strictly separating vehicle-km from passenger-km emission factors (never dividing passenger-km factors by occupancy).
4. Enforcing consistent passenger-to-passenger baseline comparisons.
5. Preserving scientific integrity: purifiers and ventilation mitigate particulate exposure, never claiming false vehicular CO2 reductions.
6. Strictly isolating authenticated Cloud Firestore logs from guest in-memory demonstration states.
"""

from datetime import date, datetime, timedelta, timezone
import logging
from typing import Any, Dict, List, Optional, Tuple
import uuid

from backend.app.core.firebase import get_firestore_client, is_firebase_available
from backend.app.models.impact import (
    CalculationMethodologyDetail,
    DailyTrendItem,
    ImpactActivityType,
    ImpactLogCreate,
    ImpactLogRecord,
    ImpactSummaryResponse,
    ModeBreakdownItem,
    SustainabilitySuggestion,
    TimeframeFilter,
)
from backend.app.models.mobility import TransportMode
from backend.app.services.emissions_service import EmissionsService
from backend.app.services.firestore_service import FirestoreService

logger = logging.getLogger(__name__)


class ImpactService:
    """Scientific environmental impact calculation and aggregation service."""

    # Pre-defined demonstration records for unauthenticated guest mode
    # Reflects a realistic week of urban commuting in India
    _DEMO_RECORDS: List[Dict[str, Any]] = [
        {
            "log_id": "demo_imp_01",
            "activity_type": ImpactActivityType.PUBLIC_TRANSIT.value,
            "mode": TransportMode.METRO.value,
            "distance_km": 16.0,
            "passengers": 1,
            "vehicle_emissions_kg_co2e": 0.35,
            "per_passenger_emissions_kg_co2e": 0.35,
            "baseline_emissions_kg_co2e": 2.64,
            "emission_saved_kg_co2e": 2.29,
            "exposure_avoided_score": 25.0,
            "notes": "Office commute via Blue Line Metro",
            "days_ago": 0,
            "data_provenance": "simulated_demo",
            "methodology_notes": "Metro benchmark: 22.0 g CO2e/passenger-km (DMRC 2024), evaluated per passenger.",
        },
        {
            "log_id": "demo_imp_02",
            "activity_type": ImpactActivityType.CARPOOL.value,
            "mode": TransportMode.CARPOOL.value,
            "distance_km": 18.0,
            "passengers": 3,
            "vehicle_emissions_kg_co2e": 2.97,
            "per_passenger_emissions_kg_co2e": 0.99,
            "baseline_emissions_kg_co2e": 2.97,
            "emission_saved_kg_co2e": 1.98,
            "exposure_avoided_score": 15.0,
            "notes": "Carpooling with 2 colleagues",
            "days_ago": 1,
            "data_provenance": "simulated_demo",
            "methodology_notes": "Petrol car 165 g/km divided by 3 occupants = 55.0 g/pax-km.",
        },
        {
            "log_id": "demo_imp_03",
            "activity_type": ImpactActivityType.EV_TRANSIT.value,
            "mode": TransportMode.ELECTRIC_BUS.value,
            "distance_km": 12.0,
            "passengers": 35,
            "vehicle_emissions_kg_co2e": 10.31,
            "per_passenger_emissions_kg_co2e": 0.29,
            "baseline_emissions_kg_co2e": 1.98,
            "emission_saved_kg_co2e": 1.69,
            "exposure_avoided_score": 20.0,
            "notes": "Electric city feeder bus to tech park",
            "days_ago": 2,
            "data_provenance": "simulated_demo",
            "methodology_notes": "e-Bus: 859.2 g CO2e/vehicle-km at CEA grid intensity (716 g/kWh), allocated across 35 passengers.",
        },
        {
            "log_id": "demo_imp_04",
            "activity_type": ImpactActivityType.ACTIVE_TRAVEL.value,
            "mode": TransportMode.WALKING.value,
            "distance_km": 2.5,
            "passengers": 1,
            "vehicle_emissions_kg_co2e": 0.0,
            "per_passenger_emissions_kg_co2e": 0.0,
            "baseline_emissions_kg_co2e": 0.41,
            "emission_saved_kg_co2e": 0.41,
            "exposure_avoided_score": 10.0,
            "notes": "Evening walk to neighborhood market",
            "days_ago": 3,
            "data_provenance": "simulated_demo",
            "methodology_notes": "Zero tailpipe emissions. Active travel inhalation assessed via AQI threshold.",
        },
        {
            "log_id": "demo_imp_05",
            "activity_type": ImpactActivityType.PURIFIER_OPTIMIZED.value,
            "mode": None,
            "distance_km": 0.0,
            "passengers": 1,
            "vehicle_emissions_kg_co2e": 0.0,
            "per_passenger_emissions_kg_co2e": 0.0,
            "baseline_emissions_kg_co2e": 0.0,
            "emission_saved_kg_co2e": 0.0,
            "exposure_avoided_score": 30.0,
            "notes": "HEPA air purifier runtime optimized for peak smog hours (18:00 - 22:00)",
            "days_ago": 4,
            "data_provenance": "simulated_demo",
            "methodology_notes": "Purifier actions mitigate particulate exposure (PM2.5/PM10); they do not claim vehicular CO2 reductions.",
        },
        {
            "log_id": "demo_imp_06",
            "activity_type": ImpactActivityType.PUBLIC_TRANSIT.value,
            "mode": TransportMode.METRO.value,
            "distance_km": 16.0,
            "passengers": 1,
            "vehicle_emissions_kg_co2e": 0.35,
            "per_passenger_emissions_kg_co2e": 0.35,
            "baseline_emissions_kg_co2e": 2.64,
            "emission_saved_kg_co2e": 2.29,
            "exposure_avoided_score": 25.0,
            "notes": "Morning commute via Metro Rail",
            "days_ago": 5,
            "data_provenance": "simulated_demo",
            "methodology_notes": "Metro benchmark: 22.0 g CO2e/passenger-km (DMRC 2024).",
        },
    ]

    @classmethod
    def calculate_action_emissions(
        cls,
        activity_type: ImpactActivityType,
        mode: Optional[TransportMode],
        distance_km: Optional[float],
        passengers: int = 1,
        baseline_mode: TransportMode = TransportMode.PETROL_CAR,
        exposure_avoided_score: Optional[float] = 0.0,
    ) -> Tuple[float, float, float, float, str]:
        """Calculates emissions, baseline comparator, and avoided CO2e for a single activity.

        Returns:
            Tuple of:
            (vehicle_emissions_kg, per_passenger_emissions_kg, baseline_emissions_kg, emission_saved_kg, methodology_notes)

        STRICT DATA INTEGRITY PRINCIPLES:
        1. Separates vehicle-km from passenger-km factors:
           - Metro factor (22.0 g/km) is ALREADY a passenger-km factor from DMRC sustainability reports.
             It is NEVER divided by occupancy again.
           - Bus factors are vehicle-km factors (1100 g/km for diesel/CNG, 859.2 g/km for e-bus)
             allocated across standard MoHUA CMP bus occupancy (35 passengers).
           - Carpool factor (165 g/km petrol car) is divided by vehicle occupancy (min 2, default 3).
           - Private vehicles are divided by actual vehicle occupancy.
           - Walking and cycling produce 0.0 g CO2e.
        2. Baseline comparisons use consistent distance and single-commuter assumptions:
           - Baseline = distance_km * 165.0 g/km (solo private petrol car, 1 passenger).
        3. Indoor safeguards (purifier/ventilation) mitigate lung exposure, NOT tailpipe CO2:
           - Emits 0.0 kg and saves 0.0 kg CO2e, preventing fabricated green claims.
        """
        # Guard: Indoor safeguards do not reduce vehicular CO2 emissions
        if activity_type in (ImpactActivityType.PURIFIER_OPTIMIZED, ImpactActivityType.VENTILATION_TIMED):
            return (
                0.0,
                0.0,
                0.0,
                0.0,
                "Indoor actions protect lung health by reducing particulate intake (PM2.5/PM10); they do not claim vehicular CO2 greenhouse gas reductions.",
            )

        # Transit activities require valid mode and distance
        effective_dist = float(max(0.1, distance_km or 0.0))
        effective_mode = mode or TransportMode.PETROL_CAR
        eff_passengers = max(1, passengers)

        # Baseline: Single commuter traveling the identical distance in a private solo petrol car
        baseline_factor_g = EmissionsService.DIRECT_EMISSION_FACTORS.get(baseline_mode, 165.0)
        baseline_emissions_g = effective_dist * baseline_factor_g
        baseline_emissions_kg = round(baseline_emissions_g / 1000.0, 3)

        # Mode-specific emissions calculation
        if effective_mode == TransportMode.METRO:
            # Passenger-km factor: 22.0 g CO2e/passenger-km (DMRC 2024 sustainability report)
            # Factor is ALREADY passenger-allocated. Never divide by occupancy.
            pax_factor_g = EmissionsService.GRID_INDIRECT_FACTORS.get(TransportMode.METRO, 22.0)
            per_passenger_g = effective_dist * pax_factor_g
            vehicle_emissions_g = per_passenger_g  # Individual transit allocation
            notes = f"Metro benchmark: {pax_factor_g} g CO2e/passenger-km (DMRC 2024); factor is passenger-allocated."

        elif effective_mode in (TransportMode.PUBLIC_BUS, TransportMode.ELECTRIC_BUS):
            # Vehicle-km factor allocated across MoHUA standard bus occupancy (35 passengers)
            v_direct = EmissionsService.DIRECT_EMISSION_FACTORS.get(effective_mode, 0.0)
            v_grid = EmissionsService.GRID_INDIRECT_FACTORS.get(effective_mode, 0.0)
            v_total = v_direct + v_grid
            bus_occupancy = EmissionsService.DEFAULT_OCCUPANCY.get(effective_mode, 35.0)
            vehicle_emissions_g = effective_dist * v_total
            per_passenger_g = vehicle_emissions_g / bus_occupancy
            notes = f"Bus vehicle factor: {v_total:.1f} g CO2e/vehicle-km allocated across MoHUA standard occupancy ({bus_occupancy:.0f} pax)."

        elif effective_mode == TransportMode.CARPOOL:
            # Vehicle factor: 165.0 g/km (petrol car) allocated across carpool occupants (min 2, default 3)
            carpool_occ = max(2, eff_passengers if eff_passengers > 1 else 3)
            v_total = EmissionsService.DIRECT_EMISSION_FACTORS.get(TransportMode.CARPOOL, 165.0)
            vehicle_emissions_g = effective_dist * v_total
            per_passenger_g = vehicle_emissions_g / float(carpool_occ)
            notes = f"Carpooling: 165.0 g CO2/km shared across {carpool_occ} passengers ({165.0 / carpool_occ:.1f} g/pax-km)."

        elif effective_mode == TransportMode.CNG_AUTO:
            # Vehicle factor: 72.0 g/km allocated across shared 2-passenger auto occupancy
            v_total = EmissionsService.DIRECT_EMISSION_FACTORS.get(TransportMode.CNG_AUTO, 72.0)
            auto_occ = 2.0
            vehicle_emissions_g = effective_dist * v_total
            per_passenger_g = vehicle_emissions_g / auto_occ
            notes = f"Shared CNG Auto: 72.0 g/km allocated across typical 2-passenger urban occupancy (36.0 g/pax-km)."

        elif effective_mode in (TransportMode.WALKING, TransportMode.CYCLING):
            vehicle_emissions_g = 0.0
            per_passenger_g = 0.0
            notes = "Zero direct and indirect vehicular emissions. Active travel respiratory intake evaluated via AQI."

        else:
            # Private motorized vehicle (Petrol Car, Diesel Car, EV Car, 2-Wheeler)
            v_direct = EmissionsService.DIRECT_EMISSION_FACTORS.get(effective_mode, 165.0)
            v_grid = EmissionsService.GRID_INDIRECT_FACTORS.get(effective_mode, 0.0)
            v_total = v_direct + v_grid
            vehicle_emissions_g = effective_dist * v_total
            per_passenger_g = vehicle_emissions_g / float(eff_passengers)
            notes = f"Vehicle total: {v_total:.1f} g CO2e/km allocated across {eff_passengers} passenger(s)."

        vehicle_kg = round(vehicle_emissions_g / 1000.0, 3)
        per_pax_kg = round(per_passenger_g / 1000.0, 3)
        savings_kg = max(0.0, round(baseline_emissions_kg - per_pax_kg, 3))

        return vehicle_kg, per_pax_kg, baseline_emissions_kg, savings_kg, notes

    @classmethod
    def create_log_record(
        cls,
        payload: ImpactLogCreate,
        user_id: Optional[str] = None,
    ) -> ImpactLogRecord:
        """Processes and formats an impact log record without persistence side-effects."""
        now = datetime.now(timezone.utc)
        act_date = payload.activity_date or now.date()
        date_str = act_date.strftime("%Y-%m-%d")

        v_kg, p_kg, base_kg, sav_kg, notes = cls.calculate_action_emissions(
            activity_type=payload.activity_type,
            mode=payload.mode,
            distance_km=payload.distance_km,
            passengers=payload.passengers,
            baseline_mode=payload.baseline_mode,
            exposure_avoided_score=payload.exposure_avoided_score,
        )

        log_id = f"imp_{act_date.strftime('%Y%m%d')}_{uuid.uuid4().hex[:8]}"

        provenance = "modeled_estimate" if user_id else "simulated_demo"

        return ImpactLogRecord(
            log_id=log_id,
            user_id=user_id,
            activity_type=payload.activity_type,
            mode=payload.mode,
            distance_km=round(payload.distance_km or 0.0, 1),
            passengers=payload.passengers,
            vehicle_emissions_kg_co2e=v_kg,
            per_passenger_emissions_kg_co2e=p_kg,
            baseline_emissions_kg_co2e=base_kg,
            emission_saved_kg_co2e=sav_kg,
            exposure_avoided_score=round(payload.exposure_avoided_score or 0.0, 1),
            activity_date=date_str,
            notes=payload.notes,
            recorded_at=now,
            data_provenance=provenance,
            methodology_notes=notes,
        )

    @classmethod
    def get_demo_records(cls) -> List[ImpactLogRecord]:
        """Generates fresh demonstration records mapped to current dates for guest exploration."""
        today = datetime.now(timezone.utc).date()
        records: List[ImpactLogRecord] = []

        for item in cls._DEMO_RECORDS:
            item_date = today - timedelta(days=item["days_ago"])
            rec = ImpactLogRecord(
                log_id=item["log_id"],
                user_id=None,
                activity_type=ImpactActivityType(item["activity_type"]),
                mode=TransportMode(item["mode"]) if item.get("mode") else None,
                distance_km=item["distance_km"],
                passengers=item["passengers"],
                vehicle_emissions_kg_co2e=item["vehicle_emissions_kg_co2e"],
                per_passenger_emissions_kg_co2e=item["per_passenger_emissions_kg_co2e"],
                baseline_emissions_kg_co2e=item["baseline_emissions_kg_co2e"],
                emission_saved_kg_co2e=item["emission_saved_kg_co2e"],
                exposure_avoided_score=item["exposure_avoided_score"],
                activity_date=item_date.strftime("%Y-%m-%d"),
                notes=item["notes"],
                recorded_at=datetime.now(timezone.utc),
                data_provenance="simulated_demo",
                methodology_notes=item["methodology_notes"],
            )
            records.append(rec)

        return records

    @classmethod
    def filter_records_by_timeframe(
        cls,
        records: List[ImpactLogRecord],
        timeframe: TimeframeFilter,
        reference_date: Optional[date] = None,
    ) -> List[ImpactLogRecord]:
        """Filters a list of records according to the requested aggregation window."""
        ref = reference_date or datetime.now(timezone.utc).date()

        if timeframe == TimeframeFilter.DAY:
            cutoff = ref
        elif timeframe == TimeframeFilter.WEEK:
            cutoff = ref - timedelta(days=6)  # Past 7 days including today
        elif timeframe == TimeframeFilter.MONTH:
            cutoff = ref - timedelta(days=29)  # Past 30 days including today
        else:
            return records  # ALL_TIME

        cutoff_str = cutoff.strftime("%Y-%m-%d")
        return [r for r in records if r.activity_date >= cutoff_str]

    @classmethod
    def aggregate_summary(
        cls,
        records: List[ImpactLogRecord],
        timeframe: TimeframeFilter,
        is_demo_data: bool = False,
        reference_date: Optional[date] = None,
    ) -> ImpactSummaryResponse:
        """Aggregates a set of records into daily trends, modal split, and educational indicators."""
        ref = reference_date or datetime.now(timezone.utc).date()
        filtered = cls.filter_records_by_timeframe(records, timeframe, reference_date=ref)

        total_activities = len(filtered)
        total_dist = round(sum(r.distance_km for r in filtered), 1)
        total_emissions = round(sum(r.per_passenger_emissions_kg_co2e for r in filtered), 2)
        total_savings = round(sum(r.emission_saved_kg_co2e for r in filtered), 2)

        # Educational Tree-Month equivalent (optional, non-credit indicator)
        # Based on US EPA GHG Equivalencies: ~21 kg/mature tree/year = ~1.75 kg/tree/month
        tree_months = round(total_savings / 1.75, 2) if total_savings > 0 else 0.0

        # Build daily trends series
        daily_trends = cls._build_daily_trends(filtered, timeframe, reference_date=ref)

        # Build modal split breakdown
        mode_breakdown = cls._build_mode_breakdown(filtered, total_dist)

        # Generate contextual suggestions
        suggestions = cls._generate_suggestions(filtered, total_savings)

        return ImpactSummaryResponse(
            timeframe=timeframe,
            total_activities_logged=total_activities,
            total_distance_km=total_dist,
            total_emissions_kg_co2e=total_emissions,
            total_savings_kg_co2e=total_savings,
            tree_months_equivalent=tree_months,
            daily_trends=daily_trends,
            mode_breakdown=mode_breakdown,
            suggestions=suggestions,
            methodology=CalculationMethodologyDetail(),
            is_demo_data=is_demo_data,
        )

    @classmethod
    def _build_daily_trends(
        cls,
        records: List[ImpactLogRecord],
        timeframe: TimeframeFilter,
        reference_date: date,
    ) -> List[DailyTrendItem]:
        """Constructs an unbroken daily timeseries for chart rendering."""
        if timeframe == TimeframeFilter.DAY:
            days_count = 1
        elif timeframe == TimeframeFilter.WEEK:
            days_count = 7
        elif timeframe == TimeframeFilter.MONTH:
            days_count = 30
        else:
            days_count = 14  # Default sample window for all_time

        # Create empty date map
        date_map: Dict[str, Dict[str, float]] = {}
        for i in range(days_count - 1, -1, -1):
            d = reference_date - timedelta(days=i)
            d_str = d.strftime("%Y-%m-%d")
            label = d.strftime("%a") if days_count <= 7 else d.strftime("%b %d")
            date_map[d_str] = {
                "day_label": label,
                "emissions_kg": 0.0,
                "savings_kg": 0.0,
                "clean_distance_km": 0.0,
                "activity_count": 0.0,
            }

        # Populate from records
        low_emission_modes = (
            TransportMode.METRO,
            TransportMode.ELECTRIC_BUS,
            TransportMode.PUBLIC_BUS,
            TransportMode.CARPOOL,
            TransportMode.ELECTRIC_CAR,
            TransportMode.ELECTRIC_TWO_WHEELER,
            TransportMode.WALKING,
            TransportMode.CYCLING,
        )

        for r in records:
            if r.activity_date in date_map:
                entry = date_map[r.activity_date]
                entry["emissions_kg"] += r.per_passenger_emissions_kg_co2e
                entry["savings_kg"] += r.emission_saved_kg_co2e
                if r.mode in low_emission_modes:
                    entry["clean_distance_km"] += r.distance_km
                entry["activity_count"] += 1.0

        items: List[DailyTrendItem] = []
        for d_str, val in date_map.items():
            items.append(
                DailyTrendItem(
                    date_str=d_str,
                    day_label=str(val["day_label"]),
                    emissions_kg=round(val["emissions_kg"], 2),
                    savings_kg=round(val["savings_kg"], 2),
                    clean_distance_km=round(val["clean_distance_km"], 1),
                    activity_count=int(val["activity_count"]),
                )
            )

        return items

    @classmethod
    def _build_mode_breakdown(
        cls,
        records: List[ImpactLogRecord],
        total_distance: float,
    ) -> List[ModeBreakdownItem]:
        """Constructs modal split breakdown analytics."""
        mode_stats: Dict[str, Dict[str, Any]] = {}

        for r in records:
            if not r.mode:
                continue
            m_val = r.mode.value if isinstance(r.mode, TransportMode) else str(r.mode)
            if m_val not in mode_stats:
                mode_enum = TransportMode(m_val) if m_val in TransportMode._value2member_map_ else TransportMode.PETROL_CAR
                mode_stats[m_val] = {
                    "mode_enum": mode_enum,
                    "trip_count": 0,
                    "distance_km": 0.0,
                    "emissions_kg": 0.0,
                    "savings_kg": 0.0,
                }
            s = mode_stats[m_val]
            s["trip_count"] += 1
            s["distance_km"] += r.distance_km
            s["emissions_kg"] += r.per_passenger_emissions_kg_co2e
            s["savings_kg"] += r.emission_saved_kg_co2e

        breakdown: List[ModeBreakdownItem] = []
        for m_val, s in mode_stats.items():
            mode_enum = s["mode_enum"]
            dist = round(s["distance_km"], 1)
            pct = round((dist / total_distance * 100.0), 1) if total_distance > 0 else 0.0
            breakdown.append(
                ModeBreakdownItem(
                    mode=m_val,
                    label_en=EmissionsService.MODE_LABELS_EN.get(mode_enum, m_val.title()),
                    label_hi=EmissionsService.MODE_LABELS_HI.get(mode_enum, m_val.title()),
                    trip_count=s["trip_count"],
                    distance_km=dist,
                    emissions_kg=round(s["emissions_kg"], 2),
                    savings_kg=round(s["savings_kg"], 2),
                    distance_share_pct=pct,
                )
            )

        # Sort by distance descending
        breakdown.sort(key=lambda x: x.distance_km, reverse=True)
        return breakdown

    @classmethod
    def _generate_suggestions(
        cls,
        records: List[ImpactLogRecord],
        total_savings_kg: float,
    ) -> List[SustainabilitySuggestion]:
        """Generates actionable, evidence-based recommendations tailored to travel history."""
        suggestions: List[SustainabilitySuggestion] = [
            SustainabilitySuggestion(
                id="sug_metro_shift",
                title_en="Shift 2 Weekly Office Commutes to Metro",
                title_hi="सप्ताह में 2 दिन कार्यालय हेतु मेट्रो का उपयोग करें",
                description_en="Metro rail emits only 22.0 g CO2e per passenger-km compared to 165 g/km in a solo petrol car, reducing your weekly commute emissions by up to 86%.",
                description_hi="मेट्रो रेल प्रति यात्री केवल 22.0 ग्राम CO2 उत्सर्जित करती है, जिससे आपकी साप्ताहिक यात्रा का प्रदूषण 86% तक घट सकता है।",
                potential_monthly_savings_kg=18.5,
                difficulty="easy",
                category="transit",
            ),
            SustainabilitySuggestion(
                id="sug_carpool_pool",
                title_en="Share Commutes with 2 Colleagues (Carpool)",
                title_hi="2 सहकर्मियों के साथ कारपूलिंग साझा करें",
                description_en="Carpooling with 3 passengers splits vehicle emissions equally, immediately avoiding 67% of individual transport emissions without requiring a new vehicle.",
                description_hi="3 व्यक्तियों की कारपूलिंग व्यक्तिगत उत्सर्जन में 67% की सीधी कमी लाती है बिना नया वाहन खरीदे।",
                potential_monthly_savings_kg=15.8,
                difficulty="moderate",
                category="carpool",
            ),
            SustainabilitySuggestion(
                id="sug_indoor_timing",
                title_en="Synchronize HEPA Purifier with Peak Outdoor Smog",
                title_hi="शाम के स्मॉग समय HEPA प्यूरीफायर चालू रखें",
                description_en="Concentrating purifier runtime during high inversion windows (18:00 - 22:00) maximizes particulate lung protection while optimizing electricity consumption.",
                description_hi="शाम के समय (18:00 - 22:00) प्यूरीफायर चलाने से बिजली की बचत के साथ फेफड़ों की सुरक्षा अधिकतम होती है।",
                potential_monthly_savings_kg=0.0,  # Zero claimed CO2 savings for indoor actions
                difficulty="easy",
                category="indoor",
            ),
        ]
        return suggestions

    @classmethod
    def parse_stored_record(cls, raw: Dict[str, Any]) -> Optional[ImpactLogRecord]:
        """Parses a stored dictionary from Firestore into a typed ImpactLogRecord."""
        try:
            doc = dict(raw)
            # Ensure activity_date exists
            if not doc.get("activity_date"):
                rec_at = doc.get("recorded_at")
                if isinstance(rec_at, datetime):
                    doc["activity_date"] = rec_at.strftime("%Y-%m-%d")
                else:
                    doc["activity_date"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")

            # Backward-compat with PersistedImpactLog
            if "emission_saved_kg_co2e" not in doc and "emission_saved_kg_co2" in doc:
                doc["emission_saved_kg_co2e"] = doc["emission_saved_kg_co2"]

            # Map legacy or string activity_type
            act_val = doc.get("activity_type")
            if act_val == "clean_commute":
                doc["activity_type"] = ImpactActivityType.COMMUTE.value
            elif act_val not in ImpactActivityType._value2member_map_:
                doc["activity_type"] = ImpactActivityType.COMMUTE.value

            return ImpactLogRecord(**doc)
        except Exception as exc:
            logger.warning(f"Error parsing stored impact log record: {exc}")
            return None

    @classmethod
    def get_user_records(cls, user_id: str, limit: int = 100) -> List[ImpactLogRecord]:
        """Retrieves and parses authenticated user impact records from Firestore."""
        raw_docs = FirestoreService.list_impact_logs(user_id=user_id, limit=limit)
        parsed: List[ImpactLogRecord] = []
        for doc in raw_docs:
            rec = cls.parse_stored_record(doc)
            if rec:
                parsed.append(rec)

        # Sort newest activity_date first, then newest recorded_at
        parsed.sort(key=lambda r: (r.activity_date, r.recorded_at), reverse=True)
        return parsed

    @classmethod
    def get_methodology(cls) -> CalculationMethodologyDetail:
        """Returns the scientific calculation methodology and emission benchmark citations."""
        return CalculationMethodologyDetail()
