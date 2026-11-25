"""Security, CORS, and Boundary Edge Case Verification Test Suite.

Verifies:
1. Security response headers (X-Content-Type-Options, X-Frame-Options, X-XSS-Protection, HSTS, Referrer-Policy).
2. CORS policy enforcement for allowed and disallowed origins (including the production Vercel frontend).
3. CORS configuration validator handling (comma-delimited string, JSON array string, list).
4. Sanitization of authentication failure details to prevent raw exception leakage.
5. Input validation bounds on coordinates, mobility parameters, and empty messages.
"""

from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.core.config import Settings
from backend.app.core.auth import get_current_user
from fastapi.security import HTTPAuthorizationCredentials
from fastapi import HTTPException


@pytest.fixture
def client():
    """Test client for HTTP request/response inspection."""
    return TestClient(app)


def test_security_response_headers(client):
    """Verify defense-in-depth security headers are present on all responses."""
    endpoints = ["/", "/api/v1/health"]
    for path in endpoints:
        response = client.get(path)
        assert response.status_code == 200
        headers = response.headers
        assert headers.get("X-Content-Type-Options") == "nosniff"
        assert headers.get("X-Frame-Options") == "DENY"
        assert headers.get("X-XSS-Protection") == "1; mode=block"
        assert "max-age=31536000" in headers.get("Strict-Transport-Security", "")
        assert headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"


def test_cors_production_vercel_origin_allowed(client):
    """Verify that the production Vercel frontend origin is accepted by CORS."""
    origin = "https://air-saathi-ai.vercel.app"
    headers = {
        "Origin": origin,
        "Access-Control-Request-Method": "GET",
    }
    response = client.options("/api/v1/health", headers=headers)
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == origin
    assert response.headers.get("access-control-allow-credentials") == "true"


def test_cors_localhost_origins_allowed(client):
    """Verify that local development origins remain accepted by CORS."""
    for origin in ["http://localhost:5173", "http://localhost:3000"]:
        response = client.options(
            "/api/v1/health",
            headers={"Origin": origin, "Access-Control-Request-Method": "GET"},
        )
        assert response.status_code == 200
        assert response.headers.get("access-control-allow-origin") == origin


def test_cors_disallowed_origin_rejected(client):
    """Verify that unauthorized external origins do not receive CORS authorization."""
    unauthorized_origin = "https://malicious-phishing-site.example.com"
    response = client.get(
        "/api/v1/health",
        headers={"Origin": unauthorized_origin},
    )
    assert response.status_code == 200
    # Disallowed origin must not have access-control-allow-origin matching the unauthorized origin
    assert response.headers.get("access-control-allow-origin") != unauthorized_origin


def test_cors_settings_field_validator_comma_separated():
    """Verify that BACKEND_CORS_ORIGINS parses comma-separated environment strings."""
    parsed = Settings.assemble_cors_origins(
        "https://air-saathi-ai.vercel.app, http://localhost:5173, http://127.0.0.1:3000"
    )
    assert isinstance(parsed, list)
    assert len(parsed) == 3
    assert "https://air-saathi-ai.vercel.app" in parsed
    assert "http://localhost:5173" in parsed


def test_cors_settings_field_validator_json_array():
    """Verify that BACKEND_CORS_ORIGINS parses JSON array strings from env."""
    parsed = Settings.assemble_cors_origins('["https://air-saathi-ai.vercel.app"]')
    assert isinstance(parsed, list)
    assert parsed == ["https://air-saathi-ai.vercel.app"]


def test_auth_error_sanitization_does_not_leak_internals():
    """Verify that token verification failures return a safe message without leaking internal exceptions."""
    cred = HTTPAuthorizationCredentials(scheme="Bearer", credentials="bad.signature.token")

    with patch("backend.app.core.auth.is_firebase_available", return_value=True):
        with patch("backend.app.core.auth.verify_id_token", side_effect=ValueError("Cryptographic RSA signature mismatch: key 0x4F1B")):
            with pytest.raises(HTTPException) as exc_info:
                get_current_user(cred)
            assert exc_info.value.status_code == 401
            # Detail must be strictly sanitized
            assert exc_info.value.detail == "Invalid or expired authentication token."
            # Raw cryptographic exception details must never be present
            assert "Cryptographic" not in exc_info.value.detail
            assert "0x4F1B" not in exc_info.value.detail


def test_weather_endpoint_invalid_coordinates_rejected(client):
    """Verify that coordinates outside geographic bounds [-90, 90] and [-180, 180] return HTTP 400."""
    res_lat = client.get("/api/v1/weather/current?latitude=95.0&longitude=77.0")
    assert res_lat.status_code == 400
    assert "Invalid coordinates" in res_lat.json()["detail"]

    res_lon = client.get("/api/v1/weather/current?latitude=28.0&longitude=195.0")
    assert res_lon.status_code == 400
    assert "Invalid coordinates" in res_lon.json()["detail"]


def test_mobility_endpoint_negative_distance_validation(client):
    """Verify that negative distance in mobility query returns HTTP 422 Unprocessable Entity."""
    res = client.get("/api/v1/mobility/plan?distance_km=-5.0")
    assert res.status_code == 422


def test_chat_endpoint_empty_message_rejected(client):
    """Verify that empty or whitespace-only messages in chat return HTTP 422."""
    res = client.post(
        "/api/v1/chat/message",
        json={"message": "", "station_id": "delhi-anand-vihar", "language": "en"},
    )
    assert res.status_code == 422
