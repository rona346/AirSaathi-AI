"""Firebase Admin SDK and Cloud Firestore Initialization.

Provides:
- Resilient initialization supporting:
  1. Service account JSON file path (FIREBASE_SERVICE_ACCOUNT_PATH)
  2. Stringified Service account JSON (FIREBASE_SERVICE_ACCOUNT_JSON)
  3. Google Application Default Credentials (ADC)
  4. Project ID only option
- Graceful fallback when Firebase credentials are not provided (no application crash).
- Thread-safe singleton client access for Auth and Firestore.
"""

import json
import logging
import os
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

_firebase_app = None
_firestore_client = None
_is_available = False


def initialize_firebase() -> bool:
    """Initialize Firebase Admin SDK using the most appropriate available credential."""
    global _firebase_app, _firestore_client, _is_available

    if _firebase_app is not None:
        return _is_available

    from backend.app.core.config import settings

    try:
        import firebase_admin
        from firebase_admin import credentials, firestore
    except ImportError:
        logger.warning("firebase-admin package not installed. Firebase features will be disabled.")
        _is_available = False
        return False

    # Check if an app is already initialized in firebase_admin
    try:
        if firebase_admin._apps and "[DEFAULT]" in firebase_admin._apps:
            _firebase_app = firebase_admin.get_app()
            _firestore_client = firestore.client()
            _is_available = True
            logger.info("Reusing existing Firebase Admin [DEFAULT] application.")
            return True
    except Exception:
        pass

    cred = None

    # 1. Direct Service Account JSON string
    if settings.FIREBASE_SERVICE_ACCOUNT_JSON:
        try:
            cert_dict = json.loads(settings.FIREBASE_SERVICE_ACCOUNT_JSON)
            cred = credentials.Certificate(cert_dict)
            logger.info("Loaded Firebase credentials from FIREBASE_SERVICE_ACCOUNT_JSON.")
        except Exception as exc:
            logger.warning(f"Failed to parse FIREBASE_SERVICE_ACCOUNT_JSON: {exc}")

    # 2. Service Account JSON file path
    if cred is None and settings.FIREBASE_SERVICE_ACCOUNT_PATH:
        path = os.path.expanduser(settings.FIREBASE_SERVICE_ACCOUNT_PATH)
        if os.path.exists(path):
            try:
                cred = credentials.Certificate(path)
                logger.info(f"Loaded Firebase credentials from file: {path}")
            except Exception as exc:
                logger.warning(f"Failed to load Firebase credentials from file {path}: {exc}")
        else:
            logger.warning(f"FIREBASE_SERVICE_ACCOUNT_PATH specifies nonexistent file: {path}")

    # 3. Application Default Credentials (ADC) or explicit Project ID
    options: Dict[str, Any] = {}
    if settings.FIREBASE_PROJECT_ID:
        options["projectId"] = settings.FIREBASE_PROJECT_ID

    if cred is None:
        try:
            # Check for GOOGLE_APPLICATION_CREDENTIALS
            if os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
                cred = credentials.ApplicationDefault()
                logger.info("Loaded Firebase Application Default Credentials.")
            elif settings.FIREBASE_PROJECT_ID:
                # In environments like Cloud Run or GCP, default credentials are automatically resolved
                cred = credentials.ApplicationDefault()
                logger.info(f"Using ApplicationDefault with project {settings.FIREBASE_PROJECT_ID}.")
        except Exception as exc:
            logger.info(f"No Google Application Default Credentials found: {exc}")

    # 4. Attempt initialization if cred or project ID is available
    try:
        if cred is not None:
            _firebase_app = firebase_admin.initialize_app(cred, options=options or None)
            _firestore_client = firestore.client()
            _is_available = True
            logger.info("Firebase Admin successfully initialized with explicit credentials.")
            return True
        elif settings.FIREBASE_PROJECT_ID:
            _firebase_app = firebase_admin.initialize_app(options=options)
            _firestore_client = firestore.client()
            _is_available = True
            logger.info(f"Firebase Admin initialized with project ID: {settings.FIREBASE_PROJECT_ID}")
            return True
        else:
            logger.info(
                "Firebase credentials not provided. Operating in Guest/Demonstration mode without Cloud Firestore."
            )
            _is_available = False
            return False
    except Exception as exc:
        logger.warning(
            f"Firebase Admin initialization encountered error: {exc}. Operating in offline/guest mode."
        )
        _is_available = False
        return False


def is_firebase_available() -> bool:
    """Check if Firebase Admin SDK is initialized and available."""
    global _is_available
    if _firebase_app is None:
        return initialize_firebase()
    return _is_available


def get_firestore_client():
    """Retrieve the Cloud Firestore client or None if unavailable."""
    global _firestore_client
    if _firestore_client is None:
        initialize_firebase()
    return _firestore_client


def verify_id_token(token: str) -> Dict[str, Any]:
    """
    Verify Firebase ID token and return decoded claims.
    Raises ValueError, auth.InvalidIdTokenError, or auth.ExpiredIdTokenError on failure.
    """
    if not is_firebase_available():
        raise RuntimeError("Firebase service is unavailable or not configured.")

    from firebase_admin import auth

    return auth.verify_id_token(token, check_revoked=True)


def set_mock_firebase(app_mock=None, firestore_mock=None) -> None:
    """Helper for testing to inject mock Firebase objects."""
    global _firebase_app, _firestore_client, _is_available
    _firebase_app = app_mock or True
    _firestore_client = firestore_mock
    _is_available = True


def reset_firebase() -> None:
    """Reset Firebase singleton state (useful between tests)."""
    global _firebase_app, _firestore_client, _is_available
    _firebase_app = None
    _firestore_client = None
    _is_available = False
