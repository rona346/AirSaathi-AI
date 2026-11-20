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
    FamilyMemberProfile,
    FamilyPreferencesData,
    FamilyPreferencesUpdate,
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
    def _merge_family_preferences(
        cls,
        target: FamilyPreferencesData,
        source: Any,
    ) -> None:
        """Safe nested merge of family preferences with bidirectional sync and empty-list support.
        
        Distinguishes omitted fields from explicitly provided values using exclude_unset=True.
        Supports explicit clearing operations (empty lists).
        Maintains bidirectional synchronization between demographics and vulnerability flags.
        """
        if hasattr(source, "model_dump"):
            src_dict = source.model_dump(exclude_unset=True)
        elif isinstance(source, dict):
            src_dict = source
        else:
            return

        # 1. Scalar household size
        if "household_size" in src_dict and src_dict["household_size"] is not None:
            target.household_size = src_dict["household_size"]

        # 2. Lists: Explicit empty lists are valid clearing operations
        if "members" in src_dict and src_dict["members"] is not None:
            target.members = [
                FamilyMemberProfile.model_validate(m) if not isinstance(m, FamilyMemberProfile) else m
                for m in src_dict["members"]
            ]
        if "configured_precautions" in src_dict and src_dict["configured_precautions"] is not None:
            target.configured_precautions = list(src_dict["configured_precautions"])

        # 3. Clean air preferences
        if "preferences" in src_dict and src_dict["preferences"] is not None:
            pref_val = src_dict["preferences"]
            pref_dict = pref_val.model_dump(exclude_unset=True) if hasattr(pref_val, "model_dump") else pref_val
            if isinstance(pref_dict, dict):
                for k, v in pref_dict.items():
                    if hasattr(target.preferences, k) and v is not None:
                        setattr(target.preferences, k, v)

        # 4. Demographics and Vulnerability with Bidirectional Synchronization
        dem_supplied = "demographics" in src_dict and src_dict["demographics"] is not None
        vuln_supplied = "vulnerability" in src_dict and src_dict["vulnerability"] is not None

        dem_dict = {}
        if dem_supplied:
            dem_val = src_dict["demographics"]
            dem_dict = dem_val.model_dump(exclude_unset=True) if hasattr(dem_val, "model_dump") else dem_val
            if isinstance(dem_dict, dict):
                for k, v in dem_dict.items():
                    if hasattr(target.demographics, k) and v is not None:
                        setattr(target.demographics, k, v)

        vuln_dict = {}
        if vuln_supplied:
            vuln_val = src_dict["vulnerability"]
            vuln_dict = vuln_val.model_dump(exclude_unset=True) if hasattr(vuln_val, "model_dump") else vuln_val
            if isinstance(vuln_dict, dict):
                for k, v in vuln_dict.items():
                    if hasattr(target.vulnerability, k) and v is not None:
                        setattr(target.vulnerability, k, v)

        # Bidirectional synchronization for shared demographics / vulnerabilities:
        # A. Children:
        if dem_supplied and "has_children" in dem_dict:
            target.vulnerability.has_children = bool(dem_dict["has_children"])
            target.demographics.has_children = bool(dem_dict["has_children"])
        elif vuln_supplied and "has_children" in vuln_dict:
            target.demographics.has_children = bool(vuln_dict["has_children"])
            target.vulnerability.has_children = bool(vuln_dict["has_children"])

        # B. Seniors:
        if dem_supplied and "has_seniors" in dem_dict:
            target.vulnerability.has_seniors = bool(dem_dict["has_seniors"])
            target.demographics.has_seniors = bool(dem_dict["has_seniors"])
        elif vuln_supplied and "has_seniors" in vuln_dict:
            target.demographics.has_seniors = bool(vuln_dict["has_seniors"])
            target.vulnerability.has_seniors = bool(vuln_dict["has_seniors"])

    @classmethod
    def upsert_user_profile(
        cls,
        user_id: str,
        update: UserProfileUpdate,
        fallback_email: Optional[str] = None,
        fallback_display_name: Optional[str] = None,
    ) -> UserProfile:
        """Create or update user profile and preferences in /users/{userId} with safe partial merging."""
        if not is_firebase_available():
            raise RuntimeError("Cloud Firestore persistence is unavailable.")

        doc_ref = cls._users_collection().document(user_id)
        existing = cls.get_user_profile(user_id)

        now = datetime.now(timezone.utc)

        if existing is None:
            # Create fresh profile
            init_family = UserProfile.model_fields["family"].default_factory()
            if update.family is not None:
                cls._merge_family_preferences(init_family, update.family)

            profile = UserProfile(
                uid=user_id,
                email=fallback_email,
                display_name=update.display_name or fallback_display_name,
                preferred_language=update.preferred_language or "en",
                location=update.location or UserProfile.model_fields["location"].default_factory(),
                family=init_family,
                routine=update.routine or UserProfile.model_fields["routine"].default_factory(),
                household=update.household or UserProfile.model_fields["household"].default_factory(),
                mobility=update.mobility or UserProfile.model_fields["mobility"].default_factory(),
                created_at=now,
                updated_at=now,
            )
        else:
            profile = existing
            update_dict = update.model_dump(exclude_unset=True)

            if "display_name" in update_dict and update.display_name is not None:
                profile.display_name = update.display_name
            if "preferred_language" in update_dict and update.preferred_language is not None:
                profile.preferred_language = update.preferred_language

            # Nested location update
            if "location" in update_dict and update.location is not None:
                loc_dict = update.location.model_dump(exclude_unset=True)
                for k, v in loc_dict.items():
                    if hasattr(profile.location, k) and v is not None:
                        setattr(profile.location, k, v)

            # Safe nested family merge
            if "family" in update_dict and update.family is not None:
                cls._merge_family_preferences(profile.family, update.family)

            # Nested routine update
            if "routine" in update_dict and update.routine is not None:
                rt_dict = update.routine.model_dump(exclude_unset=True)
                for k, v in rt_dict.items():
                    if k == "preferences" and isinstance(v, dict):
                        for pk, pv in v.items():
                            if hasattr(profile.routine.preferences, pk) and pv is not None:
                                setattr(profile.routine.preferences, pk, pv)
                    elif hasattr(profile.routine, k) and v is not None:
                        setattr(profile.routine, k, v)

            # Nested household update
            if "household" in update_dict and update.household is not None:
                hh_dict = update.household.model_dump(exclude_unset=True)
                if profile.household is None:
                    profile.household = UserProfile.model_fields["household"].default_factory()
                for k, v in hh_dict.items():
                    if hasattr(profile.household, k) and v is not None:
                        setattr(profile.household, k, v)

            # Nested mobility update
            if "mobility" in update_dict and update.mobility is not None:
                mob_dict = update.mobility.model_dump(exclude_unset=True)
                if profile.mobility is None:
                    profile.mobility = UserProfile.model_fields["mobility"].default_factory()
                for k, v in mob_dict.items():
                    if hasattr(profile.mobility, k) and v is not None:
                        setattr(profile.mobility, k, v)

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
