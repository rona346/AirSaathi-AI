"""
CAQM Graded Response Action Plan (GRAP) Evaluation Service.

Statutory Context:
- Graded Response Action Plan (GRAP) for the National Capital Region (NCR) and Adjoining Areas
  is formulated and notified by the Commission for Air Quality Management in NCR & Adjoining Areas (CAQM).
- Aligned with the official revised CAQM GRAP schedule (dated September 2026).
- Key September 2026 structural updates:
  * Advance of regulated DG-set operation, fuel conversion (PNG/bi-fuel/approved retrofits),
    and entry restrictions on BS-IV and below diesel buses from Stage II down to Stage I.
  * Formal extension of BS-III Petrol and BS-IV Diesel 4-wheeler LMV bans in Stage III to Sonipat
    alongside Gurugram, Faridabad, Ghaziabad, and Gautam Buddha Nagar (Noida / Greater Noida).
- Statutory jurisdiction is strictly limited to the National Capital Region (Delhi, Noida,
  Greater Noida, Ghaziabad, Gurugram, Faridabad, Sonipat, and adjoining notified NCR districts).
- Statutory invocation and revocation are ordered by the Sub-Committee on GRAP based on
  ambient AQI telemetry and IMD / IITM meteorological forecasts.
- This service computes an Indicative AQI-Based GRAP Category derived from monitored or
  projected air quality data. It explicitly flags that statutory enforcement requires official
  executive orders from the CAQM.
"""

from typing import Optional, Set
from backend.app.models.aqi import GrapStage, GrapStatus

# Recognized districts / cities in the National Capital Region (NCR)
NCR_CITIES: Set[str] = {
    "delhi",
    "new delhi",
    "noida",
    "greater noida",
    "ghaziabad",
    "gurugram",
    "gurgaon",
    "faridabad",
    "sonipat",
    "sonepat",
    "panipat",
    "meerut",
    "jhajjar",
    "rohtak",
    "hapur",
    "bulandshahr",
    "baghpat",
    "alwar",
    "bharatpur",
    "rewari",
    "palwal",
}

NCR_STATES: Set[str] = {
    "delhi",
    "nct of delhi",
    "national capital territory of delhi",
}

GRAP_DISCLAIMER_NCR = (
    "Indicative stage modeled from ambient CPCB AQI telemetry under the revised CAQM GRAP schedule "
    "(September 2026). Statutory invocation or revocation is ordered by the CAQM Sub-Committee based "
    "on IMD/IITM meteorological forecasts."
)

GRAP_DISCLAIMER_NON_NCR = (
    "GRAP is an emergency response framework under the Commission for Air Quality Management "
    "in NCR & Adjoining Areas Act, 2021. Stations outside Delhi-NCR adhere to standard CPCB "
    "National Air Quality Index (NAQI) health advisories."
)


def is_ncr_location(city: Optional[str] = None, state: Optional[str] = None) -> bool:
    """
    Check whether a given city or state belongs to the National Capital Region (NCR).
    GRAP is statutory only within Delhi-NCR and adjoining notified districts.
    """
    if city and city.strip().lower() in NCR_CITIES:
        return True
    if state and state.strip().lower() in NCR_STATES:
        return True
    return False


def get_grap_stage_for_aqi(aqi: int) -> GrapStage:
    """
    Resolve the CAQM GRAP stage based on ambient or forecast AQI:
    - AQI <= 200: None (Normal / No Curbs)
    - AQI 201-300: Stage I ('Poor')
    - AQI 301-400: Stage II ('Very Poor')
    - AQI 401-450: Stage III ('Severe')
    - AQI > 450: Stage IV ('Severe+')
    """
    if aqi <= 200:
        return GrapStage.NONE
    if aqi <= 300:
        return GrapStage.STAGE_1
    if aqi <= 400:
        return GrapStage.STAGE_2
    if aqi <= 450:
        return GrapStage.STAGE_3
    return GrapStage.STAGE_4


def evaluate_grap(
    aqi: int,
    city: Optional[str] = None,
    state: Optional[str] = None,
) -> GrapStatus:
    """
    Evaluate GRAP status for a station based on its ambient AQI and geographic jurisdiction.

    Returns a structured GrapStatus specifying:
    - applicability (True only for Delhi-NCR)
    - indicative stage
    - official bracket description
    - citizen and municipal curbs summary
    - legal/statutory disclaimer
    """
    if not is_ncr_location(city=city, state=state):
        return GrapStatus(
            applicable=False,
            stage=GrapStage.NONE,
            stage_name="Not Applicable (Outside Delhi-NCR)",
            aqi_threshold="N/A",
            status_type="indicative_aqi_based",
            is_official_order=False,
            curbs_summary=[
                "CAQM Graded Response Action Plan (GRAP) is statutory only within the National Capital Region (Delhi-NCR).",
                "Standard CPCB National Air Quality Index (NAQI) health advisories and municipal protocols apply.",
            ],
            notice=GRAP_DISCLAIMER_NON_NCR,
        )

    stage = get_grap_stage_for_aqi(aqi)

    if stage == GrapStage.NONE:
        return GrapStatus(
            applicable=True,
            stage=stage,
            stage_name="Normal (AQI ≤ 200) — No GRAP Curbs Active",
            aqi_threshold="0–200",
            status_type="indicative_aqi_based",
            is_official_order=False,
            curbs_summary=[
                "Standard environmental guidelines and routine dust mitigation.",
                "No emergency vehicular, industrial, or construction curbs active.",
            ],
            notice=GRAP_DISCLAIMER_NCR,
        )

    if stage == GrapStage.STAGE_1:
        return GrapStatus(
            applicable=True,
            stage=stage,
            stage_name="Stage I — Poor (AQI 201–300)",
            aqi_threshold="201–300",
            status_type="indicative_aqi_based",
            is_official_order=False,
            curbs_summary=[
                "Strict enforcement of CAQM Direction on regulated DG set operation, fuel conversion (PNG/bi-fuel/approved retrofits), and emergency-only limits (advanced from Stage II in Sep 2026 revision).",
                "Entry restrictions on BS-IV and below diesel buses entering Delhi from adjoining states (advanced from Stage II in Sep 2026 revision).",
                "Strict dust suppression enforcement at construction & demolition sites (>500 sq m) with anti-smog guns.",
                "Strict prohibition and intensified vigilance against open burning of biomass and municipal solid waste.",
            ],
            notice=GRAP_DISCLAIMER_NCR,
        )

    if stage == GrapStage.STAGE_2:
        return GrapStatus(
            applicable=True,
            stage=stage,
            stage_name="Stage II — Very Poor (AQI 301–400)",
            aqi_threshold="301–400",
            status_type="indicative_aqi_based",
            is_official_order=False,
            curbs_summary=[
                "Daily mechanical sweeping and intensive water sprinkling with chemical dust suppressants on identified high-density corridors.",
                "Augmentation of CNG/electric bus services and increased Delhi Metro trip frequency to maximize public transit mode share.",
                "Enhanced parking fee structures to discourage non-essential private vehicle usage.",
                "Targeted dust suppression and intensive vehicular emissions monitoring across identified pollution hotspots.",
            ],
            notice=GRAP_DISCLAIMER_NCR,
        )

    if stage == GrapStage.STAGE_3:
        return GrapStatus(
            applicable=True,
            stage=stage,
            stage_name="Stage III — Severe (AQI 401–450)",
            aqi_threshold="401–450",
            status_type="indicative_aqi_based",
            is_official_order=False,
            curbs_summary=[
                "Strict ban on non-essential construction and demolition activities across NCR (exempting critical healthcare, defense, metro, railway).",
                "Plying restrictions on BS-III Petrol and BS-IV Diesel 4-wheeler passenger vehicles (LMVs) across Delhi, Gurugram, Faridabad, Ghaziabad, Gautam Buddha Nagar, and Sonipat.",
                "Strict restriction on interstate buses entering Delhi (only EV/CNG/BS-VI diesel buses permitted from NCR states).",
                "Discontinuation of physical classes for children up to Class V; shift to online mode.",
            ],
            notice=GRAP_DISCLAIMER_NCR,
        )

    # stage == GrapStage.STAGE_4
    return GrapStatus(
        applicable=True,
        stage=stage,
        stage_name="Stage IV — Severe+ (AQI > 450)",
        aqi_threshold="> 450",
        status_type="indicative_aqi_based",
        is_official_order=False,
        curbs_summary=[
            "Strict ban on entry of non-essential trucks into Delhi (exempting LNG/CNG/electric and trucks carrying essential commodities).",
            "Ban on Delhi-registered diesel medium and heavy goods vehicles (BS-IV and below) other than essentials.",
            "Physical classes suspended for grades VI to IX and XI (online mode recommended).",
            "50% capacity advisory for public and private offices with mandatory work-from-home (WFH) for remaining staff.",
        ],
        notice=GRAP_DISCLAIMER_NCR,
    )
