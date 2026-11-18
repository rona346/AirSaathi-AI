"""Unit tests for Firebase Authentication and Authorization dependencies.

Verifies:
1. Successful ID token verification and claim extraction.
2. Missing Authorization header (HTTP 401).
3. Invalid / expired token rejection (HTTP 401).
4. Unauthorized cross-user access prevention (HTTP 403).
5. Optional user resolution in guest mode.
6. Service status reporting (/api/v1/user/status).
7. Service unavailable behavior when Firebase is not initialized.
"""

from unittest.mock import MagicMock, patch
import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from backend.app.core.auth import get_current_user, get_optional_user, verify_user_ownership
from backend.app.core.firebase import reset_firebase, set_mock_firebase
from backend.app.models.user import AuthenticatedUser
from backend.app.api.v1.endpoints.user import (
    get_auth_service_status,
    get_current_user_profile,
    get_user_profile_by_id,
)
from backend.app.models.user import UserProfile


@pytest.fixture(autouse=True)
def reset_fb_state():
    reset_firebase()
    yield
    reset_firebase()


def test_missing_token_raises_401():
    """Verify that calling get_current_user with no credentials raises 401."""
    with pytest.raises(HTTPException) as exc:
        get_current_user(None)
    assert exc.value.status_code == 401
    assert "missing or empty Bearer token" in exc.value.detail


def test_empty_token_raises_401():
    """Verify that calling get_current_user with an empty token raises 401."""
    cred = HTTPAuthorizationCredentials(scheme="Bearer", credentials="   ")
    with pytest.raises(HTTPException) as exc:
        get_current_user(cred)
    assert exc.value.status_code == 401


def test_firebase_unavailable_raises_503():
    """Verify that when Firebase is unconfigured, attempting to verify a token returns 503."""
    cred = HTTPAuthorizationCredentials(scheme="Bearer", credentials="any-token")
    with patch("backend.app.core.auth.is_firebase_available", return_value=False):
        with pytest.raises(HTTPException) as exc:
            get_current_user(cred)
        assert exc.value.status_code == 503
        assert "temporarily unavailable" in exc.value.detail


def test_successful_token_verification():
    """Verify that a valid token parses into an AuthenticatedUser."""
    cred = HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid.mock.jwt")
    mock_claims = {
        "uid": "usr_alpha_123",
        "email": "user@example.com",
        "name": "Ronak Gupta",
        "email_verified": True,
    }

    with patch("backend.app.core.auth.is_firebase_available", return_value=True):
        with patch("backend.app.core.auth.verify_id_token", return_value=mock_claims):
            user = get_current_user(cred)
            assert isinstance(user, AuthenticatedUser)
            assert user.uid == "usr_alpha_123"
            assert user.email == "user@example.com"
            assert user.display_name == "Ronak Gupta"
            assert user.email_verified is True


def test_invalid_token_raises_401():
    """Verify that an invalid or expired token raises 401."""
    cred = HTTPAuthorizationCredentials(scheme="Bearer", credentials="expired.or.malformed.jwt")

    with patch("backend.app.core.auth.is_firebase_available", return_value=True):
        with patch("backend.app.core.auth.verify_id_token", side_effect=ValueError("Token has expired")):
            with pytest.raises(HTTPException) as exc:
                get_current_user(cred)
            assert exc.value.status_code == 401
            assert "Invalid or expired" in exc.value.detail


def test_optional_user_returns_none_when_unauthenticated():
    """Verify get_optional_user returns None when no header is supplied."""
    user = get_optional_user(None)
    assert user is None


def test_optional_user_returns_user_when_valid():
    """Verify get_optional_user returns AuthenticatedUser when token is valid."""
    cred = HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid.jwt")
    mock_claims = {"uid": "usr_guest_1", "email": "guest@test.com"}

    with patch("backend.app.core.auth.is_firebase_available", return_value=True):
        with patch("backend.app.core.auth.verify_id_token", return_value=mock_claims):
            user = get_optional_user(cred)
            assert user is not None
            assert user.uid == "usr_guest_1"


def test_cross_user_access_strictly_forbidden_403():
    """Verify that User A cannot access User B's profile or subcollections."""
    user_a = AuthenticatedUser(uid="user_a_123", email="a@test.com")
    user_b_id = "user_b_456"

    # Direct authorization check
    with pytest.raises(HTTPException) as exc:
        verify_user_ownership(user_b_id, user_a)
    assert exc.value.status_code == 403
    assert "Access forbidden" in exc.value.detail

    # Endpoint enforcement
    with pytest.raises(HTTPException) as exc_endpoint:
        get_user_profile_by_id(target_user_id=user_b_id, current_user=user_a)
    assert exc_endpoint.value.status_code == 403


def test_own_user_access_permitted():
    """Verify that user accessing their own ID is authorized."""
    user_a = AuthenticatedUser(uid="user_a_123", email="a@test.com")
    # Should not raise exception
    verify_user_ownership("user_a_123", user_a)


def test_auth_service_status_reporting():
    """Verify status endpoint transparently exposes available mode."""
    # When unavailable
    with patch("backend.app.api.v1.endpoints.user.is_firebase_available", return_value=False):
        status_unavail = get_auth_service_status()
        assert status_unavail.success is True
        assert status_unavail.data["firebase_available"] is False
        assert status_unavail.data["mode"] == "guest_demonstration"
        assert status_unavail.is_demo_data is True

    # When available
    with patch("backend.app.api.v1.endpoints.user.is_firebase_available", return_value=True):
        status_avail = get_auth_service_status()
        assert status_avail.success is True
        assert status_avail.data["firebase_available"] is True
        assert status_avail.data["mode"] == "authenticated_firestore"
        assert status_avail.is_demo_data is False
