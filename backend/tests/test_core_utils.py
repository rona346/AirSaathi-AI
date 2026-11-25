"""Unit tests for shared core utilities."""

from datetime import timezone
from fastapi import Query
from backend.app.core.utils import get_utc_now, resolve_query_param


def test_resolve_query_param_direct_values():
    assert resolve_query_param("delhi", "default") == "delhi"
    assert resolve_query_param(123, 0) == 123
    assert resolve_query_param(True, False) is True
    assert resolve_query_param(None, "fallback") == "fallback"


def test_resolve_query_param_fastapi_query_object():
    q_param = Query("default_val")
    assert resolve_query_param(q_param, "other") == "default_val"

    q_param_none = Query(None)
    assert resolve_query_param(q_param_none, "fallback") is None


def test_get_utc_now_timezone_aware():
    now = get_utc_now()
    assert now.tzinfo is not None
    assert now.tzinfo == timezone.utc
