"""Official Central Pollution Control Board (CPCB) National Air Quality Index (NAQI) calculator.

Reference:
- 'National Air Quality Index', Central Pollution Control Board (CPCB),
  Ministry of Environment, Forests & Climate Change, Govt. of India.
- Breakpoints and piecewise linear interpolation formula:
    Ip = [ (I_hi - I_lo) / (B_hi - B_lo) * (Cp - B_lo) ] + I_lo
"""

from typing import Dict, List, Optional, Tuple
from backend.app.models.aqi import AqiCategory

# Standard CPCB NAQI Categories and breakpoints
AQI_CATEGORIES = [
    (0, 50, AqiCategory.GOOD),
    (51, 100, AqiCategory.SATISFACTORY),
    (101, 200, AqiCategory.MODERATE),
    (201, 300, AqiCategory.POOR),
    (301, 400, AqiCategory.VERY_POOR),
    (401, 500, AqiCategory.SEVERE),
]

# Official CPCB Breakpoints Table: (B_lo, B_hi, I_lo, I_hi)
CPCB_BREAKPOINTS: Dict[str, List[Tuple[float, float, int, int]]] = {
    "PM2.5": [
        (0.0, 30.0, 0, 50),
        (30.0, 60.0, 51, 100),
        (60.0, 90.0, 101, 200),
        (90.0, 120.0, 201, 300),
        (120.0, 250.0, 301, 400),
        (250.0, 380.0, 401, 500),
    ],
    "PM10": [
        (0.0, 50.0, 0, 50),
        (50.0, 100.0, 51, 100),
        (100.0, 250.0, 101, 200),
        (250.0, 350.0, 201, 300),
        (350.0, 430.0, 301, 400),
        (430.0, 510.0, 401, 500),
    ],
    "NO2": [
        (0.0, 40.0, 0, 50),
        (40.0, 80.0, 51, 100),
        (80.0, 180.0, 101, 200),
        (180.0, 280.0, 201, 300),
        (280.0, 400.0, 301, 400),
        (400.0, 500.0, 401, 500),
    ],
    "SO2": [
        (0.0, 40.0, 0, 50),
        (40.0, 80.0, 51, 100),
        (80.0, 380.0, 101, 200),
        (380.0, 800.0, 201, 300),
        (800.0, 1600.0, 301, 400),
        (1600.0, 2000.0, 401, 500),
    ],
    "CO": [
        (0.0, 1.0, 0, 50),
        (1.0, 2.0, 51, 100),
        (2.0, 10.0, 101, 200),
        (10.0, 17.0, 201, 300),
        (17.0, 34.0, 301, 400),
        (34.0, 50.0, 401, 500),
    ],
    "O3": [
        (0.0, 50.0, 0, 50),
        (50.0, 100.0, 51, 100),
        (100.0, 168.0, 101, 200),
        (168.0, 208.0, 201, 300),
        (208.0, 748.0, 301, 400),
        (748.0, 1000.0, 401, 500),
    ],
    "NH3": [
        (0.0, 200.0, 0, 50),
        (200.0, 400.0, 51, 100),
        (400.0, 800.0, 101, 200),
        (800.0, 1200.0, 201, 300),
        (1200.0, 1800.0, 301, 400),
        (1800.0, 2400.0, 401, 500),
    ],
    "Pb": [
        (0.0, 0.5, 0, 50),
        (0.5, 1.0, 51, 100),
        (1.0, 2.0, 101, 200),
        (2.0, 3.0, 201, 300),
        (3.0, 3.5, 301, 400),
        (3.5, 5.0, 401, 500),
    ],
}


def get_aqi_category_from_value(aqi: int) -> AqiCategory:
    """Return CPCB NAQI category for a given numerical AQI."""
    if aqi < 0:
        return AqiCategory.GOOD
    for low, high, cat in AQI_CATEGORIES:
        if low <= aqi <= high:
            return cat
    return AqiCategory.SEVERE_PLUS


def calculate_subindex(pollutant: str, concentration: float) -> int:
    """Calculate the CPCB NAQI sub-index for a given pollutant and concentration."""
    if concentration <= 0:
        return 0

    breakpoints = CPCB_BREAKPOINTS.get(pollutant.upper())
    if not breakpoints:
        raise ValueError(f"Unknown pollutant: {pollutant}. Supported: {list(CPCB_BREAKPOINTS.keys())}")

    # Check each band
    for b_lo, b_hi, i_lo, i_hi in breakpoints:
        if b_lo <= concentration <= b_hi:
            ratio = (i_hi - i_lo) / (b_hi - b_lo)
            sub_index = i_lo + ratio * (concentration - b_lo)
            return int(round(sub_index))

    # If concentration exceeds highest breakpoint
    highest_band = breakpoints[-1]
    if concentration > highest_band[1]:
        # Values above highest band fall in Severe+ (500+)
        ratio = (highest_band[3] - highest_band[2]) / (highest_band[1] - highest_band[0])
        sub_index = highest_band[2] + ratio * (concentration - highest_band[0])
        return min(999, int(round(sub_index)))

    return 0


def calculate_concentration_for_subindex(pollutant: str, target_subindex: int) -> float:
    """Inverse CPCB formula: find typical concentration given a target sub-index."""
    if target_subindex <= 0:
        return 0.0

    breakpoints = CPCB_BREAKPOINTS.get(pollutant.upper())
    if not breakpoints:
        raise ValueError(f"Unknown pollutant: {pollutant}")

    for b_lo, b_hi, i_lo, i_hi in breakpoints:
        if i_lo <= target_subindex <= i_hi:
            ratio = (b_hi - b_lo) / (i_hi - i_lo)
            conc = b_lo + ratio * (target_subindex - i_lo)
            return round(conc, 2)

    # If beyond 500
    highest = breakpoints[-1]
    ratio = (highest[1] - highest[0]) / (highest[3] - highest[2])
    conc = highest[0] + ratio * (target_subindex - highest[2])
    return round(conc, 2)


def calculate_overall_aqi(pollutant_concentrations: Dict[str, float]) -> Tuple[int, str, Dict[str, int]]:
    """
    Calculate the official CPCB overall AQI from a dictionary of pollutant concentrations.
    Returns:
        (overall_aqi, prominent_pollutant, sub_indices_dict)
    Rule:
        Overall AQI is the maximum of the individual sub-indices.
    """
    sub_indices: Dict[str, int] = {}
    max_subindex = 0
    prominent = "PM2.5"

    for pol, conc in pollutant_concentrations.items():
        pol_key = pol.upper()
        if pol_key in CPCB_BREAKPOINTS:
            sub = calculate_subindex(pol_key, conc)
            sub_indices[pol] = sub
            if sub > max_subindex:
                max_subindex = sub
                prominent = pol

    return max_subindex, prominent, sub_indices
