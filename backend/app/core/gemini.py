"""AirSaathi AI - Centralized Google GenAI Interactions API Integration Module.

Provides:
- Thread-safe, reusable Google GenAI client lifecycle management.
- Execution of generation requests via the Google GenAI Interactions API.
- Strict error containment and secret masking.
"""

import logging
from typing import Optional
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

_client = None


def get_gemini_client():
    """Retrieve or initialize the singleton Google GenAI client."""
    global _client
    if _client is not None:
        return _client

    if not settings.GEMINI_API_KEY or not settings.GEMINI_API_KEY.strip():
        return None

    try:
        from google import genai
        _client = genai.Client(api_key=settings.GEMINI_API_KEY)
        return _client
    except Exception as exc:
        logger.warning(f"Failed to initialize Google GenAI client: {type(exc).__name__}")
        return None


def set_mock_gemini_client(mock_client) -> None:
    """Helper for testing to inject a mock Google GenAI client."""
    global _client
    _client = mock_client


def reset_gemini_client() -> None:
    """Reset the singleton Google GenAI client state (useful between tests)."""
    global _client
    _client = None


def generate_gemini_text(prompt: str) -> Optional[str]:
    """
    Generate text using Google GenAI Interactions API.

    Calls:
        client.interactions.create(
            model=settings.GEMINI_MODEL_ID,
            input=prompt
        )

    Returns:
        interaction.output_text if valid and non-empty; otherwise None.
    """
    if not prompt or not prompt.strip():
        return None

    client = get_gemini_client()
    if client is None:
        return None

    try:
        interaction = client.interactions.create(
            model=settings.GEMINI_MODEL_ID,
            input=prompt,
        )
        if interaction and hasattr(interaction, "output_text"):
            output = interaction.output_text
            if output and isinstance(output, str) and output.strip():
                return output.strip()
        return None
    except Exception as exc:
        # Never log API keys or sensitive payload data
        logger.warning(f"Gemini generation error: {type(exc).__name__}")
        return None
