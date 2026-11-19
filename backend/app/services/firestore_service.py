"""Cloud Firestore Persistence Service for AirSaathi AI.

Manages authenticated user storage in Google Cloud Firestore under:
- /users/{userId}
- /users/{userId}/routines/{routineId}
- /users/{userId}/chat_sessions/{sessionId}
- /users/{userId}/saved_routes/{routeId}
- /users/{userId}/indoor_devices/{deviceId}
- /users/{userId}/impact_logs/{logId}

Enforces validation using Pydantic schemas, safe timestamp serialization,
and graceful offline fallback.
"""

from datetime import datetime, timezone
import logging
from typing import Any, Dict, List, Optional
from google.cloud.firestore_v1 import SERVER_TIMESTAMP

from backend.app.core.firebase import get_firestore_client, is_firebase_available
from backend.app.models.user import (
    PersistedChatSession,
    PersistedImpactLog,
    PersistedIndoorDevice,
    PersistedRoutineRecord,
    PersistedSavedRoute,
    UserProfile,
    UserProfileUpdate,
)

logger = logging.getLogger(__name__)


class FirestoreService:
    @staticmethod
    def _users_collection():
        db = get_firestore_client()
        if db is None:
            raise RuntimeError("Cloud Firestore client is not initialized or unavailable.")
        return db.collection("users")

    @classmethod
    def get_user_profile(cls, user_id: str) -> Optional[UserProfile]:
        """Fetch user profile and preferences document from /users/{userId}."""
        if not is_firebase_available():
            logger.info("Firestore unavailable; cannot fetch user profile.")
            return None

        try:
            doc_ref = cls._users_collection().document(user_id)
            snapshot = doc_ref.get()
            if not snapshot.exists:
                return None

            data = snapshot.to_dict() or {}
            # Ensure uid matches document id
            data["uid"] = user_id
            return UserProfile.model_validate(data)
        except Exception as exc:
            logger.warning(f"Error reading user profile for {user_id}: {exc}")
            return None

    @classmethod
    def upsert_user_profile(
        cls,
        user_id: str,
        update: UserProfileUpdate,
        fallback_email: Optional[str] = None,
        fallback_display_name: Optional[str] = None,
    ) -> UserProfile:
        """Create or update user profile and preferences in /users/{userId}."""
        if not is_firebase_available():
            raise RuntimeError("Cloud Firestore persistence is unavailable.")

        doc_ref = cls._users_collection().document(user_id)
        existing = cls.get_user_profile(user_id)

        now = datetime.now(timezone.utc)

        if existing is None:
            # Create fresh profile
            profile = UserProfile(
                uid=user_id,
                email=fallback_email,
                display_name=update.display_name or fallback_display_name,
                preferred_language=update.preferred_language or "en",
                location=update.location or UserProfile.model_fields["location"].default_factory(),
                family=update.family or UserProfile.model_fields["family"].default_factory(),
                routine=update.routine or UserProfile.model_fields["routine"].default_factory(),
                household=update.household or UserProfile.model_fields["household"].default_factory(),
                mobility=update.mobility or UserProfile.model_fields["mobility"].default_factory(),
                created_at=now,
                updated_at=now,
            )
        else:
            profile = existing
            if update.display_name is not None:
                profile.display_name = update.display_name
            if update.preferred_language is not None:
                profile.preferred_language = update.preferred_language
            if update.location is not None:
                profile.location = update.location
            if update.family is not None:
                profile.family = update.family
            if update.routine is not None:
                profile.routine = update.routine
            if update.household is not None:
                profile.household = update.household
            if update.mobility is not None:
                profile.mobility = update.mobility
            profile.updated_at = now

        payload = profile.model_dump(mode="json")
        doc_ref.set(payload, merge=True)
        return profile

    # Subcollection: Routines
    @classmethod
    def save_routine(cls, user_id: str, record: PersistedRoutineRecord) -> str:
        """Persist generated daily routine under /users/{userId}/routines/{routineId}."""
        if not is_firebase_available():
            raise RuntimeError("Cloud Firestore persistence is unavailable.")

        user_ref = cls._users_collection().document(user_id)
        routine_ref = user_ref.collection("routines").document(record.routine_id)
        routine_ref.set(record.model_dump(mode="json"))
        return record.routine_id

    @classmethod
    def list_routines(cls, user_id: str, limit: int = 15) -> List[Dict[str, Any]]:
        """Retrieve recent saved routines for an authenticated user."""
        if not is_firebase_available():
            return []

        try:
            docs = (
                cls._users_collection()
                .document(user_id)
                .collection("routines")
                .limit(limit)
                .stream()
            )
            return [d.to_dict() for d in docs]
        except Exception as exc:
            logger.warning(f"Error fetching routines for user {user_id}: {exc}")
            return []

    # Subcollection: Chat Sessions
    @classmethod
    def save_chat_session(cls, user_id: str, session: PersistedChatSession) -> str:
        """Persist chat history under /users/{userId}/chat_sessions/{sessionId}."""
        if not is_firebase_available():
            raise RuntimeError("Cloud Firestore persistence is unavailable.")

        session_ref = (
            cls._users_collection()
            .document(user_id)
            .collection("chat_sessions")
            .document(session.session_id)
        )
        session_ref.set(session.model_dump(mode="json"), merge=True)
        return session.session_id

    @classmethod
    def list_chat_sessions(cls, user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """List chat session history for an authenticated user."""
        if not is_firebase_available():
            return []

        try:
            docs = (
                cls._users_collection()
                .document(user_id)
                .collection("chat_sessions")
                .limit(limit)
                .stream()
            )
            return [d.to_dict() for d in docs]
        except Exception as exc:
            logger.warning(f"Error fetching chat sessions for user {user_id}: {exc}")
            return []

    # Subcollection: Saved Routes
    @classmethod
    def save_route(cls, user_id: str, route: PersistedSavedRoute) -> str:
        """Persist commute route under /users/{userId}/saved_routes/{routeId}."""
        if not is_firebase_available():
            raise RuntimeError("Cloud Firestore persistence is unavailable.")

        route_ref = (
            cls._users_collection()
            .document(user_id)
            .collection("saved_routes")
            .document(route.route_id)
        )
        route_ref.set(route.model_dump(mode="json"))
        return route.route_id

    @classmethod
    def list_routes(cls, user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """List saved commuting routes for an authenticated user."""
        if not is_firebase_available():
            return []

        try:
            docs = (
                cls._users_collection()
                .document(user_id)
                .collection("saved_routes")
                .limit(limit)
                .stream()
            )
            return [d.to_dict() for d in docs]
        except Exception as exc:
            logger.warning(f"Error fetching saved routes for user {user_id}: {exc}")
            return []

    # Subcollection: Indoor Devices
    @classmethod
    def save_indoor_device(cls, user_id: str, device: PersistedIndoorDevice) -> str:
        """Persist indoor air purifier/device under /users/{userId}/indoor_devices/{deviceId}."""
        if not is_firebase_available():
            raise RuntimeError("Cloud Firestore persistence is unavailable.")

        device_ref = (
            cls._users_collection()
            .document(user_id)
            .collection("indoor_devices")
            .document(device.device_id)
        )
        device_ref.set(device.model_dump(mode="json"))
        return device.device_id

    @classmethod
    def list_indoor_devices(cls, user_id: str) -> List[Dict[str, Any]]:
        """List registered indoor air devices for an authenticated user."""
        if not is_firebase_available():
            return []

        try:
            docs = (
                cls._users_collection()
                .document(user_id)
                .collection("indoor_devices")
                .stream()
            )
            return [d.to_dict() for d in docs]
        except Exception as exc:
            logger.warning(f"Error fetching indoor devices for user {user_id}: {exc}")
            return []

    # Subcollection: Impact Logs
    @classmethod
    def save_impact_log(cls, user_id: str, log: Any) -> str:
        """Persist environmental action log under /users/{userId}/impact_logs/{logId}."""
        if not is_firebase_available():
            raise RuntimeError("Cloud Firestore persistence is unavailable.")

        log_id = log.log_id if hasattr(log, "log_id") else log.get("log_id")
        data = log.model_dump(mode="json") if hasattr(log, "model_dump") else log

        log_ref = (
            cls._users_collection()
            .document(user_id)
            .collection("impact_logs")
            .document(log_id)
        )
        log_ref.set(data)
        return log_id

    @classmethod
    def get_impact_log(cls, user_id: str, log_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a single impact log under /users/{userId}/impact_logs/{logId}."""
        if not is_firebase_available():
            return None

        try:
            doc_ref = (
                cls._users_collection()
                .document(user_id)
                .collection("impact_logs")
                .document(log_id)
            )
            doc = doc_ref.get()
            return doc.to_dict() if doc.exists else None
        except Exception as exc:
            logger.warning(f"Error fetching impact log {log_id} for user {user_id}: {exc}")
            return None

    @classmethod
    def delete_impact_log(cls, user_id: str, log_id: str) -> bool:
        """Delete an environmental action log under /users/{userId}/impact_logs/{logId}."""
        if not is_firebase_available():
            raise RuntimeError("Cloud Firestore persistence is unavailable.")

        try:
            doc_ref = (
                cls._users_collection()
                .document(user_id)
                .collection("impact_logs")
                .document(log_id)
            )
            doc = doc_ref.get()
            if not doc.exists:
                return False
            doc_ref.delete()
            return True
        except Exception as exc:
            logger.warning(f"Error deleting impact log {log_id} for user {user_id}: {exc}")
            return False

    @classmethod
    def list_impact_logs(cls, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """List impact logs for an authenticated user."""
        if not is_firebase_available():
            return []

        try:
            docs = (
                cls._users_collection()
                .document(user_id)
                .collection("impact_logs")
                .limit(limit)
                .stream()
            )
            return [d.to_dict() for d in docs]
        except Exception as exc:
            logger.warning(f"Error fetching impact logs for user {user_id}: {exc}")
            return []
