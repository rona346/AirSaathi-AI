"""Unit tests for the centralized Google GenAI Interactions API module."""

import pytest
from unittest.mock import MagicMock, patch
import httpx
from backend.app.core.gemini import (
    DEFAULT_GEMINI_TIMEOUT_SECONDS,
    generate_gemini_text,
    get_gemini_client,
    reset_gemini_client,
    sanitize_json_output,
    set_mock_gemini_client,
)
from backend.app.core.config import settings
from backend.app.core.utils import get_utc_now, resolve_query_param
from backend.app.core.utils import get_utc_now, resolve_query_param
from backend.app.core.utils import get_utc_now, resolve_query_param


@pytest.fixture(autouse=True)
def clean_gemini_client():
    reset_gemini_client()
    yield
    reset_gemini_client()


def test_generate_gemini_text_success():
    mock_client = MagicMock()
    mock_interaction = MagicMock()
    mock_interaction.output_text = "Verified air quality advisory response."
    mock_client.interactions.create.return_value = mock_interaction
    set_mock_gemini_client(mock_client)

    result = generate_gemini_text("Tell me about PM2.5 in Delhi.")

    assert result == "Verified air quality advisory response."
    mock_client.interactions.create.assert_called_once_with(
        model=settings.GEMINI_MODEL_ID,
        input="Tell me about PM2.5 in Delhi.",
        timeout=DEFAULT_GEMINI_TIMEOUT_SECONDS,
    )


def test_generate_gemini_text_custom_timeout():
    mock_client = MagicMock()
    mock_interaction = MagicMock()
    mock_interaction.output_text = "Custom timeout response."
    mock_client.interactions.create.return_value = mock_interaction
    set_mock_gemini_client(mock_client)

    result = generate_gemini_text("Test custom timeout prompt", timeout=5.0)

    assert result == "Custom timeout response."
    mock_client.interactions.create.assert_called_once_with(
        model=settings.GEMINI_MODEL_ID,
        input="Test custom timeout prompt",
        timeout=5.0,
    )


def test_generate_gemini_text_timeout_exception():
    mock_client = MagicMock()
    mock_client.interactions.create.side_effect = httpx.ReadTimeout("The read operation timed out")
    set_mock_gemini_client(mock_client)

    result = generate_gemini_text("Test prompt that times out")
    assert result is None


def test_indoor_fallback_on_gemini_timeout():
    from backend.app.models.indoor import HouseholdInput, IndoorAssessmentRequest
    from backend.app.services.indoor_service import IndoorAirService

    with patch("backend.app.services.indoor_service.generate_gemini_text", return_value=None):
        req = IndoorAssessmentRequest(
            station_id="delhi-anand-vihar",
            household=HouseholdInput(),
        )
        assessment = IndoorAirService.evaluate_indoor_air(req)
        assert assessment is not None
        assert assessment.ai_provider != "google-gemini"
        assert assessment.ai_generated is False
        assert assessment.qualitative_risk in ("Low", "Moderate", "High", "Severe")


def test_mobility_fallback_on_gemini_timeout():
    from backend.app.models.mobility import MobilityRequest, TransportMode
    from backend.app.services.mobility_service import MobilityService

    with patch("backend.app.services.mobility_service.generate_gemini_text", return_value=None):
        req = MobilityRequest(
            station_id="delhi-anand-vihar",
            distance_km=10.0,
            current_mode=TransportMode.PETROL_CAR,
        )
        plan = MobilityService.generate_mobility_plan(req)
        assert plan is not None
        assert plan.ai_provider == "expert-rules-fallback"
        assert plan.ai_generated is False
        assert plan.recommended_mode is not None


def test_generate_gemini_text_empty_response():
    mock_client = MagicMock()
    mock_interaction = MagicMock()
    mock_interaction.output_text = ""
    mock_client.interactions.create.return_value = mock_interaction
    set_mock_gemini_client(mock_client)

    result = generate_gemini_text("Test prompt")
    assert result is None


def test_generate_gemini_text_none_output_text():
    mock_client = MagicMock()
    mock_interaction = MagicMock()
    mock_interaction.output_text = None
    mock_client.interactions.create.return_value = mock_interaction
    set_mock_gemini_client(mock_client)

    result = generate_gemini_text("Test prompt")
    assert result is None


def test_generate_gemini_text_empty_prompt():
    mock_client = MagicMock()
    set_mock_gemini_client(mock_client)

    assert generate_gemini_text("") is None
    assert generate_gemini_text("   ") is None
    mock_client.interactions.create.assert_not_called()


def test_generate_gemini_text_api_exception():
    mock_client = MagicMock()
    mock_client.interactions.create.side_effect = RuntimeError("API service quota exceeded")
    set_mock_gemini_client(mock_client)

    # Must return None safely without raising an unhandled exception
    result = generate_gemini_text("Test prompt")
    assert result is None


def test_generate_gemini_text_no_client():
    with patch.object(settings, "GEMINI_API_KEY", ""):
        reset_gemini_client()
        result = generate_gemini_text("Test prompt")
        assert result is None


def test_client_singleton_reuse():
    mock_client = MagicMock()
    set_mock_gemini_client(mock_client)

    c1 = get_gemini_client()
    c2 = get_gemini_client()
    assert c1 is c2
    assert c1 is mock_client


def test_sanitize_json_output():
    """Verify JSON fence stripping across various markdown wrappers."""
    assert sanitize_json_output('{"key": "value"}') == '{"key": "value"}'
    assert sanitize_json_output('```json\n{"key": "value"}\n```') == '{"key": "value"}'
    assert sanitize_json_output('```\n{"key": "value"}\n```') == '{"key": "value"}'
    assert sanitize_json_output('   ```json   \n   {"key": "value"}   \n   ```   ') == '{"key": "value"}'

    # Markdown with surrounding whitespace
    raw_spaced = '   ```json   \n   {"a": 1}   \n   ```   '
    assert sanitize_json_output(raw_spaced) == '{"a": 1}'
