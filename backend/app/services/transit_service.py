"""City-aware transit availability service.

Identifies operational transit infrastructure (such as urban Metro Rail and Electric Buses)
across Indian cities to avoid inappropriate transport recommendations (e.g. recommending
Metro in cities like Udaipur where no metro exists).
"""

from enum import Enum
from typing import Optional, Set, Tuple


class TransitAvailabilityStatus(str, Enum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    UNVERIFIED = "unverified"


class TransitService:
    """City-aware transit availability registry and validation service."""

    # Indian cities with operational urban Metro Rail networks
    METRO_CITIES: Set[str] = {
        "delhi",
        "new delhi",
        "noida",
        "greater noida",
        "gurugram",
        "gurgaon",
        "ghaziabad",
        "faridabad",
        "mumbai",
        "navi mumbai",
        "thane",
        "bengaluru",
        "bangalore",
        "kolkata",
        "chennai",
        "hyderabad",
        "ahmedabad",
        "pune",
        "jaipur",
        "lucknow",
        "kochi",
        "cochin",
        "nagpur",
        "kanpur",
        "agra",
    }

    # Cities confirmed to have NO operational urban Metro Rail infrastructure
    NO_METRO_CITIES: Set[str] = {
        "udaipur",
        "varanasi",
        "chandigarh",
        "shimla",
        "dehradun",
        "jodhpur",
        "kota",
        "ajmer",
        "bikaner",
        "jabalpur",
        "gwalior",
        "ranchi",
        "gaya",
        "mysuru",
        "mysore",
        "amritsar",
        "ludhiana",
        "haridwar",
        "rishikesh",
        "allahabad",
        "prayagraj",
        "guwahati",
        "patna",  # Under construction, not yet operational
        "indore",  # Under construction / trial
        "bhopal",  # Under construction / trial
    }

    # Cities with known active municipal Electric Bus fleets
    ELECTRIC_BUS_CITIES: Set[str] = {
        "delhi",
        "noida",
        "mumbai",
        "bengaluru",
        "pune",
        "ahmedabad",
        "hyderabad",
        "kolkata",
        "chennai",
        "lucknow",
        "jaipur",
        "surat",
        "indore",
        "chandigarh",
    }

    @classmethod
    def normalize_city(cls, city: Optional[str]) -> str:
        if not city:
            return ""
        return city.strip().lower()

    @classmethod
    def check_metro_availability(
        cls, city: Optional[str]
    ) -> Tuple[bool, TransitAvailabilityStatus, str, str]:
        """Evaluates whether Metro Rail is operational in the specified city.

        Returns:
            Tuple of (has_metro, status, reason_en, reason_hi).
        """
        norm = cls.normalize_city(city)
        if not norm:
            return (
                False,
                TransitAvailabilityStatus.UNVERIFIED,
                "City not specified; transit network availability is unverified.",
                "शहर निर्दिष्ट नहीं है; परिवहन नेटवर्क की उपलब्धता असत्यापित है।",
            )

        # Check known operational metro cities
        for m_city in cls.METRO_CITIES:
            if m_city == norm or m_city in norm or norm in m_city:
                display_city = city.strip()
                return (
                    True,
                    TransitAvailabilityStatus.AVAILABLE,
                    f"Operational urban metro rail network is available in {display_city}.",
                    f"{display_city} में परिचालन योग्य शहरी मेट्रो रेल नेटवर्क उपलब्ध है।",
                )

        # Check confirmed no-metro cities (e.g. Udaipur)
        for no_m in cls.NO_METRO_CITIES:
            if no_m == norm or no_m in norm or norm in no_m:
                display_city = city.strip()
                return (
                    False,
                    TransitAvailabilityStatus.UNAVAILABLE,
                    f"Metro rail service is not operational in {display_city}.",
                    f"{display_city} में मेट्रो रेल सेवा उपलब्ध नहीं है।",
                )

        # Unrecognized / unknown city
        display_city = city.strip()
        return (
            False,
            TransitAvailabilityStatus.UNVERIFIED,
            f"Transit infrastructure for '{display_city}' is unverified in our registry. Fixed rail cannot be assumed.",
            f"'{display_city}' के लिए स्थानीय परिवहन नेटवर्क असत्यापित है; मेट्रो रेल सेवा पूर्वकल्पित नहीं की जा सकती।",
        )

    @classmethod
    def check_electric_bus_availability(cls, city: Optional[str]) -> bool:
        """Checks if city has known municipal electric bus deployment."""
        norm = cls.normalize_city(city)
        for eb_city in cls.ELECTRIC_BUS_CITIES:
            if eb_city == norm or eb_city in norm or norm in eb_city:
                return True
        return False
