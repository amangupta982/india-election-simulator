"""Cloud Storage service — file uploads and signed URLs.

Handles:
1. Player avatar uploads (profile pictures)
2. Shareable game report generation (post-game HTML reports)
3. Secure signed URLs for asset access
"""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Optional

from app.firebase_config import get_storage_bucket

logger = logging.getLogger(__name__)


class StorageService:
    """Manages Cloud Storage operations for user content."""

    def __init__(self):
        self._bucket = None

    @property
    def bucket(self):
        if self._bucket is None:
            self._bucket = get_storage_bucket()
        return self._bucket

    @property
    def available(self) -> bool:
        return self.bucket is not None

    async def upload_avatar(self, user_id: str, file_data: bytes, content_type: str = "image/png") -> Optional[str]:
        """Upload a player avatar to Cloud Storage.

        Path: avatars/{user_id}/profile.png
        Returns the public URL of the uploaded avatar.
        """
        if not self.available:
            return None
        try:
            blob_path = f"avatars/{user_id}/profile.png"
            blob = self.bucket.blob(blob_path)
            blob.upload_from_string(file_data, content_type=content_type)
            blob.make_public()
            logger.info(f"Avatar uploaded for user {user_id}")
            return blob.public_url
        except Exception as e:
            logger.error(f"Avatar upload failed: {e}")
            return None

    async def save_game_report(self, session_id: str, report_html: str) -> Optional[str]:
        """Save a shareable post-game report as HTML.

        Path: reports/{session_id}/report.html
        Returns a signed URL valid for 7 days.
        """
        if not self.available:
            return None
        try:
            blob_path = f"reports/{session_id}/report.html"
            blob = self.bucket.blob(blob_path)
            blob.upload_from_string(report_html, content_type="text/html")
            url = blob.generate_signed_url(expiration=timedelta(days=7))
            logger.info(f"Game report saved for session {session_id}")
            return url
        except Exception as e:
            logger.error(f"Report save failed: {e}")
            return None

    async def get_signed_url(self, blob_path: str, expiration_hours: int = 1) -> Optional[str]:
        """Generate a time-limited signed URL for secure asset access."""
        if not self.available:
            return None
        try:
            blob = self.bucket.blob(blob_path)
            url = blob.generate_signed_url(expiration=timedelta(hours=expiration_hours))
            return url
        except Exception as e:
            logger.error(f"Signed URL generation failed: {e}")
            return None


# Singleton instance
storage_service = StorageService()
