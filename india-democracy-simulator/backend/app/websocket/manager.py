"""WebSocket connection manager for real-time game events."""
from __future__ import annotations
import json
from typing import Dict, Set
from fastapi import WebSocket


class ConnectionManager:
    """Manages WebSocket connections keyed by session_id."""

    def __init__(self):
        self.active: Dict[str, Set[WebSocket]] = {}

    async def connect(self, session_id: str, ws: WebSocket):
        await ws.accept()
        if session_id not in self.active:
            self.active[session_id] = set()
        self.active[session_id].add(ws)

    def disconnect(self, session_id: str, ws: WebSocket):
        if session_id in self.active:
            self.active[session_id].discard(ws)
            if not self.active[session_id]:
                del self.active[session_id]

    async def broadcast(self, session_id: str, data: dict):
        if session_id in self.active:
            msg = json.dumps(data)
            dead = set()
            for ws in self.active[session_id]:
                try:
                    await ws.send_text(msg)
                except Exception:
                    dead.add(ws)
            for ws in dead:
                self.active[session_id].discard(ws)


manager = ConnectionManager()
