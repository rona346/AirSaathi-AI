import json
from datetime import datetime
from unittest.mock import MagicMock, patch
import httpx
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.models.aqi import AqiCategory, CurrentAqiResponse, HealthAdvisory, PollutantDetail, StationInfo
from backend.app.models.chat import (
    ChatContextInfo,
    ChatMessage,
    ChatRequest,
    ChatResponse,
    ChatRole,
)
from backend.app.services.chat_service import ChatService


@pytest.fixture
def mock_cpcb_reading():
    return CurrentAqiResponse(
        station=StationInfo(
            id="delhi-anand-vihar",
            name="Anand Vihar",
            city="Delhi",
            state="Delhi",
            latitude=28.6469,
            longitude=77.3160,
            is_hotspot=True,
        ),
        aqi=379,
        category=AqiCategory.VERY_POOR,
        prominent_pollutant="PM2.5",
        pollutants={
            "PM2.5": PollutantDetail(
                name="PM2.5",
                value=222.0,
                unit="µg/m³",
                sub_index=379,
                category=AqiCategory.VERY_POOR,
                standard_limit=60.0,
                who_limit=15.0,
            ),
        },
        health_advisory=HealthAdvisory(
            general_advice="High health risk",
            children_and_seniors="Avoid outdoor activity",
            patients_with_respiratory_issues="Remain indoors",
            outdoor_activity="Avoid",
            mask_recommendation="N95 Mandatory",
            purifier_recommendation="Run continuously",
            ventilation_window="Brief mid-day only",
        ),
        weather={"temperature": 18.0, "humidity": 68.0, "condition": "Smoggy"},
        data_source="Central Pollution Control Board (CPCB) - CAAQMS Live",
        last_updated=datetime(2026, 11, 18, 15, 0, 0),
        is_demo_data=False,
    )


def test_chat_message_success_en(mock_cpcb_reading):
    with patch("backend.app.services.chat_service.get_active_aqi_provider") as mock_get_provider:
        mock_provider = MagicMock()
        mock_provider.get_current_aqi.return_value = mock_cpcb_reading
        mock_get_provider.return_value = mock_provider

        req = ChatRequest(
            message="What is PM2.5 and how does it harm lungs?",
            station_id="delhi-anand-vihar",
            language="en",
        )

        res = ChatService.process_chat_message(req)

        assert isinstance(res, ChatResponse)
        assert res.language == "en"
        assert "PM2.5" in res.message
        assert res.context_used.station_name == "Anand Vihar"
        assert res.context_used.aqi == 379
        assert "Medical Disclaimer" in res.disclaimer
        assert len(res.suggested_followups) >= 2


def test_chat_message_success_hi(mock_cpcb_reading):
    with patch("backend.app.services.chat_service.get_active_aqi_provider") as mock_get_provider:
        mock_provider = MagicMock()
        mock_provider.get_current_aqi.return_value = mock_cpcb_reading
        mock_get_provider.return_value = mock_provider

        req = ChatRequest(
            message="आज बच्चों को स्मॉग से कैसे बचाएं?",
            station_id="delhi-anand-vihar",
            language="hi",
        )

        res = ChatService.process_chat_message(req)

        assert isinstance(res, ChatResponse)
        assert res.language == "hi"
        assert "बच्चे" in res.message or "स्कूल" in res.message or "N95" in res.message
        assert "चिकित्सीय अस्वीकरण" in res.disclaimer
        assert len(res.suggested_followups) >= 2


def test_cpcb_context_injection(mock_cpcb_reading):
    with patch("backend.app.services.chat_service.get_active_aqi_provider") as mock_get_provider:
        mock_provider = MagicMock()
        mock_provider.get_current_aqi.return_value = mock_cpcb_reading
        mock_get_provider.return_value = mock_provider

        req = ChatRequest(message="What is the current air status?", language="en")
        res = ChatService.process_chat_message(req)

        assert "Anand Vihar" in res.message
        assert "379" in res.message
        assert "Very Poor" in res.message
        assert res.context_used.prominent_pollutant == "PM2.5"


def test_demo_live_provenance(mock_cpcb_reading):
    with patch("backend.app.services.chat_service.get_active_aqi_provider") as mock_get_provider:
        mock_provider = MagicMock()

        # Case 1: Live CPCB
        mock_cpcb_reading.is_demo_data = False
        mock_cpcb_reading.data_source = "CPCB Live Test Telemetry"
        mock_provider.get_current_aqi.return_value = mock_cpcb_reading
        mock_get_provider.return_value = mock_provider

        res_live = ChatService.process_chat_message(ChatRequest(message="Status"))
        assert res_live.context_used.is_demo_data is False
        assert "Live CPCB" in res_live.message

        # Case 2: Demo Mode
        mock_cpcb_reading.is_demo_data = True
        mock_cpcb_reading.data_source = "CPCB Demo Historical Baseline"
        mock_provider.get_current_aqi.return_value = mock_cpcb_reading

        res_demo = ChatService.process_chat_message(ChatRequest(message="Status"))
        assert res_demo.context_used.is_demo_data is True
        assert "Demo Mode" in res_demo.message


def test_conversation_history_handling(mock_cpcb_reading):
    with patch("backend.app.services.chat_service.get_active_aqi_provider") as mock_get_provider:
        mock_provider = MagicMock()
        mock_provider.get_current_aqi.return_value = mock_cpcb_reading
        mock_get_provider.return_value = mock_provider

        history = [
            ChatMessage(role=ChatRole.USER, content="Hello"),
            ChatMessage(role=ChatRole.ASSISTANT, content="Hi! How can I help with air pollution?"),
            ChatMessage(role=ChatRole.USER, content="Should I run outside today?"),
        ]

        req = ChatRequest(
            message="What about walking instead?",
            history=history,
            language="en",
        )

        res = ChatService.process_chat_message(req)
        assert res is not None
        assert res.context_used.aqi == 379


def test_gemini_api_call_and_fallback(mock_cpcb_reading):
    from backend.app.core.config import settings

    with patch("backend.app.services.chat_service.get_active_aqi_provider") as mock_get_provider:
        mock_provider = MagicMock()
        mock_provider.get_current_aqi.return_value = mock_cpcb_reading
        mock_get_provider.return_value = mock_provider

        # Success case with Gemini API mock
        mock_client = MagicMock()
        mock_post = MagicMock()
        mock_post.status_code = 200
        mock_post.json.return_value = {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {"thought": "Evaluating user query about morning exercise..."},
                            {"text": "Exercising outdoors in current Very Poor AQI (379) is hazardous to lungs."},
                        ]
                    }
                }
            ]
        }
        mock_client.post.return_value = mock_post
        mock_client.__enter__.return_value = mock_client
        mock_client.__exit__.return_value = None

        with patch("httpx.Client", return_value=mock_client):
            with patch.object(settings, "GEMINI_API_KEY", "test-key"):
                res_gemini = ChatService.process_chat_message(ChatRequest(message="Exercise advice?"))
                assert res_gemini.ai_provider == "google-gemini"
                assert res_gemini.ai_generated is True
                assert "379" in res_gemini.message

        # Error case: HTTP 429
        mock_post_429 = MagicMock()
        mock_post_429.status_code = 429
        mock_post_429.text = "Quota exceeded"
        mock_client.post.return_value = mock_post_429

        with patch("httpx.Client", return_value=mock_client):
            with patch.object(settings, "GEMINI_API_KEY", "test-key"):
                res_fallback = ChatService.process_chat_message(ChatRequest(message="Exercise advice?"))
                assert res_fallback.ai_provider == "expert-rules-fallback"
                assert res_fallback.ai_generated is False


def test_chat_api_endpoint_validation():
    from backend.app.api.v1.endpoints.chat import send_chat_message

    with patch("backend.app.services.chat_service.ChatService.process_chat_message") as mock_process:
        mock_process.return_value = ChatResponse(
            message="Test reply",
            language="en",
            ai_provider="expert-rules-fallback",
            ai_generated=False,
            context_used=ChatContextInfo(
                station_id="delhi-anand-vihar",
                station_name="Anand Vihar",
                city="Delhi",
                aqi=379,
                category="Very Poor",
                prominent_pollutant="PM2.5",
                is_demo_data=False,
                data_source="CPCB Live",
                observed_at=datetime.utcnow(),
            ),
            suggested_followups=["Next question"],
            disclaimer="Disclaimer",
            timestamp=datetime.utcnow(),
        )

        # Valid Request
        req_valid = ChatRequest(message="How to protect against smog?")
        api_res = send_chat_message(request=req_valid)
        assert api_res.success is True
        assert api_res.data.message == "Test reply"

        # Invalid Empty Request should raise HTTPException 400
        with pytest.raises(Exception):
            send_chat_message(request=ChatRequest(message="   "))

        # Oversized message (>1000 chars) should raise HTTPException 400
        with pytest.raises(Exception):
            send_chat_message(request=ChatRequest(message="a" * 1050))
