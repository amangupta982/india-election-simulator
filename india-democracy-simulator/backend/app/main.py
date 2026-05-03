"""FastAPI main application."""
import logging
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware

from app.cloud_logging import setup_cloud_logging
from app.config import get_settings
from app.database import engine, Base
from app.routers.auth import router as auth_router
from app.routers.game import router as game_router
from app.routers.constituencies import router as const_router
from app.routers.leaderboard import leaderboard_router, feedback_router
from app.websocket.manager import manager

# Initialize structured logging
setup_cloud_logging()
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup (dev only — use Alembic in prod)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info(f"🏛️ {settings.app_name} started successfully")
    yield
    await engine.dispose()
    logger.info("Application shutting down")


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="AI-powered Indian Lok Sabha election simulator with Google Cloud integration",
    lifespan=lifespan,
)

import os
allowed_origin = os.getenv("ALLOWED_ORIGIN")
origins = ["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000", "http://127.0.0.1:3001"]
if allowed_origin:
    origins.append(allowed_origin)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if allowed_origin else ["*"],
    allow_credentials=False if not allowed_origin else True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Request ID + Logging Middleware ──────────────────────────────

@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    """Add request ID and log all API requests with latency."""
    request_id = str(uuid.uuid4())[:8]
    request.state.request_id = request_id
    start_time = time.time()

    response = await call_next(request)

    duration_ms = (time.time() - start_time) * 1000
    logger.info(
        f"[{request_id}] {request.method} {request.url.path} "
        f"→ {response.status_code} ({duration_ms:.0f}ms)"
    )
    response.headers["X-Request-ID"] = request_id
    return response


# Mount routers
app.include_router(auth_router, prefix=settings.api_v1_prefix)
app.include_router(game_router, prefix=settings.api_v1_prefix)
app.include_router(const_router, prefix=settings.api_v1_prefix)
app.include_router(leaderboard_router, prefix=settings.api_v1_prefix)
app.include_router(feedback_router, prefix=settings.api_v1_prefix)


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "app": settings.app_name,
        "google_cloud": {
            "firebase": settings.firebase_enabled,
            "firestore": settings.firestore_enabled,
            "vertex_ai": True,
            "cloud_storage": True,
            "cloud_logging": True,
        },
    }


@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await manager.connect(session_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo back for now; game events push via manager.broadcast()
            await websocket.send_text(f"ack:{data}")
    except WebSocketDisconnect:
        manager.disconnect(session_id, websocket)
