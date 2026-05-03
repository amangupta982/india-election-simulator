"""FastAPI main application."""
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import engine, Base
from app.routers.auth import router as auth_router
from app.routers.game import router as game_router
from app.routers.constituencies import router as const_router
from app.routers.leaderboard import leaderboard_router, feedback_router
from app.websocket.manager import manager

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup (dev only — use Alembic in prod)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="AI-powered Indian Lok Sabha election simulator",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000", "http://127.0.0.1:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(auth_router, prefix=settings.api_v1_prefix)
app.include_router(game_router, prefix=settings.api_v1_prefix)
app.include_router(const_router, prefix=settings.api_v1_prefix)
app.include_router(leaderboard_router, prefix=settings.api_v1_prefix)
app.include_router(feedback_router, prefix=settings.api_v1_prefix)


@app.get("/health")
async def health():
    return {"status": "ok", "app": settings.app_name}


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
