"""Firestore service — real-time game state and analytics.

Firestore is used alongside SQLite to provide:
1. Real-time game state sync (frontend listens for live updates)
2. Analytics event logging (player decision patterns)
3. Live leaderboard (real-time updates across all clients)

SQLite remains the primary relational DB for complex queries.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Optional

from app.firebase_config import get_firestore_client

logger = logging.getLogger(__name__)


class FirestoreService:
    """Manages Firestore operations for real-time features."""

    def __init__(self):
        self._db = None

    @property
    def db(self):
        if self._db is None:
            self._db = get_firestore_client()
        return self._db

    @property
    def available(self) -> bool:
        return self.db is not None

    async def save_game_state(self, session_id: str, state: dict) -> bool:
        """Write game state snapshot to Firestore for real-time sync.

        Path: game_sessions/{session_id}/snapshots/{week_number}
        Frontend can listen to this collection for live updates.
        """
        if not self.available:
            return False
        try:
            week = state.get("week_number", 0)
            doc_ref = (
                self.db.collection("game_sessions")
                .document(session_id)
                .collection("snapshots")
                .document(f"week_{week}")
            )
            doc_ref.set({
                "session_id": session_id,
                "week_number": week,
                "seat_projection_you": state.get("seat_projection_you", 0),
                "seat_projection_opp": state.get("seat_projection_opp", 0),
                "budget_remaining": state.get("budget_remaining", 0),
                "approval_rating": state.get("approval_rating", 0),
                "win_probability": state.get("win_probability", 0),
                "status": state.get("status", "in_progress"),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            })
            logger.info(f"Firestore: saved game state for session {session_id} week {week}")
            return True
        except Exception as e:
            logger.error(f"Firestore write failed: {e}")
            return False

    async def save_game_session_meta(self, session_id: str, meta: dict) -> bool:
        """Write game session metadata (party, role, difficulty).

        Path: game_sessions/{session_id}
        """
        if not self.available:
            return False
        try:
            doc_ref = self.db.collection("game_sessions").document(session_id)
            doc_ref.set({
                "player_party": meta.get("player_party", ""),
                "role": meta.get("role", ""),
                "difficulty": meta.get("difficulty", "normal"),
                "status": "in_progress",
                "created_at": datetime.now(timezone.utc).isoformat(),
            })
            return True
        except Exception as e:
            logger.error(f"Firestore meta write failed: {e}")
            return False

    async def update_leaderboard(self, entry: dict) -> bool:
        """Add/update leaderboard entry in Firestore.

        Path: leaderboard/{entry_id}
        Enables real-time leaderboard updates across all connected clients.
        """
        if not self.available:
            return False
        try:
            self.db.collection("leaderboard").add({
                "display_name": entry.get("display_name", "Anonymous"),
                "score": entry.get("score", 0),
                "player_party": entry.get("player_party", ""),
                "role": entry.get("role", ""),
                "seat_margin": entry.get("seat_margin", 0),
                "created_at": datetime.now(timezone.utc).isoformat(),
            })
            return True
        except Exception as e:
            logger.error(f"Firestore leaderboard update failed: {e}")
            return False

    async def log_analytics_event(self, event_type: str, data: dict) -> bool:
        """Log analytics events for player behavior analysis.

        Path: analytics/{auto_id}
        Used for understanding player decision patterns and improving the game.
        """
        if not self.available:
            return False
        try:
            self.db.collection("analytics").add({
                "event_type": event_type,
                "data": data,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
            return True
        except Exception as e:
            logger.error(f"Firestore analytics write failed: {e}")
            return False


# Singleton instance
firestore_service = FirestoreService()
