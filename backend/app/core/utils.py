"""Shared Core Utilities for AirSaathi AI.

Provides common helpers for:
- Safe resolution of FastAPI Query parameter defaults in direct test calls.
- Timezone-aware UTC timestamp generation.
"""

from datetime import datetime, timezone
from typing import Any


def resolve_query_param(val: Any, default: Any = None) -> Any:
    """
    Safely resolves parameter values when endpoints are called directly as Python functions
    in test suites without FastAPI's dependency injection container.
    """
    if hasattr(val, "default"):
        return val.default
    return val if val is not None else default


def get_utc_now() -> datetime:
    """Return current timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)
