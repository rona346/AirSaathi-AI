"""Authentication and User Authorization Dependencies for AirSaathi AI.

Provides FastAPI dependencies for:
- Required authenticated user (get_current_user) -> 401 on missing/invalid token
- Optional authenticated user (get_optional_user) -> None if unauthenticated
- User-level authorization and ownership verification (verify_user_ownership) -> 403 on cross-user access
"""

import logging
from typing import Optional
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from backend.app.core.firebase import is_firebase_available, verify_id_token
from backend.app.models.user import AuthenticatedUser

logger = logging.getLogger(__name__)

# Security schemes: auto_error=False allows flexible optional checks
security_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security_scheme),
) -> AuthenticatedUser:
    """
    FastAPI dependency requiring a valid Firebase ID token in the Authorization header.
    Returns AuthenticatedUser with uid, email, and claims.
    Raises 401 if token is missing, invalid, or expired.
    Raises 503 if Firebase is not configured on the backend.
    """
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required: missing or empty Bearer token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials.strip()
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required: missing or empty Bearer token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not is_firebase_available():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Cloud authentication service is temporarily unavailable or not configured.",
        )

    try:
        decoded_claims = verify_id_token(token)
    except Exception as exc:
        logger.warning(f"Failed to verify Firebase ID token: {exc}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired authentication token: {str(exc)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

    uid = decoded_claims.get("uid") or decoded_claims.get("sub")
    if not uid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Malformed token: missing subject/uid claim.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return AuthenticatedUser(
        uid=uid,
        email=decoded_claims.get("email"),
        display_name=decoded_claims.get("name"),
        email_verified=bool(decoded_claims.get("email_verified", False)),
        claims=decoded_claims,
    )


def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security_scheme),
) -> Optional[AuthenticatedUser]:
    """
    FastAPI dependency that returns an AuthenticatedUser if valid credentials exist,
    or None if no credentials were provided (guest mode).
    Raises 401 if a token was supplied but is invalid or expired.
    """
    if not credentials or not credentials.credentials:
        return None

    return get_current_user(credentials)


def verify_user_ownership(target_user_id: str, current_user: AuthenticatedUser) -> None:
    """
    Enforce that an authenticated user can only access and modify their own records.
    Raises HTTP 403 Forbidden if a user attempts cross-account access.
    """
    if current_user.uid != target_user_id:
        logger.warning(
            f"Cross-user access blocked: user {current_user.uid} tried accessing resources of {target_user_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: you do not have permission to access another user's resources.",
        )
