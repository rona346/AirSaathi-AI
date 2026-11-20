"""Unit tests for the centralized Google GenAI Interactions API module."""

import pytest
from unittest.mock import MagicMock, patch
from backend.app.core.gemini import (
    generate_gemini_text,
    get_gemini_client,
    reset_gemini_client,
    set_mock_gemini_client,
)
from backend.app.core.config import settings


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
    )


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
