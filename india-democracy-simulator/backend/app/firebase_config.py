"""Firebase Admin SDK + Google Cloud client initialization.

Centralizes all GCP service clients so they can be imported as singletons.
Gracefully degrades when running locally without credentials.
"""
from __future__ import annotations

import logging
from typing import Optional

logger = logging.getLogger(__name__)

# ─── Firebase Admin ──────────────────────────────────────────────
_firebase_app = None
_firestore_client = None
_storage_bucket = None


def _init_firebase() -> None:
    """Initialize Firebase Admin SDK (idempotent)."""
    global _firebase_app
    if _firebase_app is not None:
        return
    try:
        import firebase_admin
        from firebase_admin import credentials

        # On Cloud Run, default credentials are auto-injected
        # Locally, set GOOGLE_APPLICATION_CREDENTIALS env var
        _firebase_app = firebase_admin.initialize_app()
        logger.info("Firebase Admin SDK initialized successfully")
    except Exception as e:
        logger.warning(f"Firebase Admin SDK not available: {e}")
        _firebase_app = None


def get_firebase_app():
    """Get the Firebase Admin app instance."""
    _init_firebase()
    return _firebase_app


def get_firestore_client():
    """Get a Firestore client singleton."""
    global _firestore_client
    if _firestore_client is not None:
        return _firestore_client
    try:
        _init_firebase()
        from firebase_admin import firestore
        _firestore_client = firestore.client()
        logger.info("Firestore client initialized")
        return _firestore_client
    except Exception as e:
        logger.warning(f"Firestore not available: {e}")
        return None


def get_storage_bucket(bucket_name: Optional[str] = None):
    """Get a Cloud Storage bucket reference."""
    global _storage_bucket
    if _storage_bucket is not None:
        return _storage_bucket
    try:
        _init_firebase()
        from firebase_admin import storage
        from app.config import get_settings
        settings = get_settings()
        name = bucket_name or settings.gcs_bucket_name
        _storage_bucket = storage.bucket(name)
        logger.info(f"Cloud Storage bucket initialized: {name}")
        return _storage_bucket
    except Exception as e:
        logger.warning(f"Cloud Storage not available: {e}")
        return None


def verify_firebase_token(id_token: str) -> Optional[dict]:
    """Verify a Firebase ID token (from Google Sign-In on frontend).

    Returns the decoded token dict with uid, email, name, etc.
    Returns None if verification fails or Firebase is not available.
    """
    try:
        _init_firebase()
        from firebase_admin import auth
        decoded = auth.verify_id_token(id_token)
        return decoded
    except Exception as e:
        logger.warning(f"Firebase token verification failed: {e}")
        return None
