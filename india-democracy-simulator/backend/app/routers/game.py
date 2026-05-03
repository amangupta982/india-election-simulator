"""Game router — start, decision, state, end."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import User, GameSession, GameStateSnapshot
from app.schemas import GameStartRequest, GameStartResponse, DecisionRequest, DecisionResponse, GameStateResponse
from app.services.game_engine import GameEngine
from app.routers.auth import get_current_user

router = APIRouter(prefix="/game", tags=["game"])
engine = GameEngine()


@router.post("/start", response_model=GameStartResponse)
async def start_game(req: GameStartRequest, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await engine.start_game(db, user.id, req.player_party, req.role.value, req.difficulty.value)
    return result


@router.post("/{session_id}/decision", response_model=DecisionResponse)
async def make_decision(session_id: str, req: DecisionRequest, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    session = await db.get(GameSession, session_id)
    if not session or session.user_id != user.id:
        raise HTTPException(status_code=404, detail="Session not found")
    try:
        result = await engine.process_decision(db, session_id, req.event_id, req.choice_index)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{session_id}/state", response_model=GameStateResponse)
async def get_state(session_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    session = await db.get(GameSession, session_id)
    if not session or session.user_id != user.id:
        raise HTTPException(status_code=404, detail="Session not found")
    result = await db.execute(
        select(GameStateSnapshot).where(GameStateSnapshot.session_id == session_id)
        .order_by(GameStateSnapshot.created_at.desc()).limit(1)
    )
    snap = result.scalar_one_or_none()
    if not snap:
        raise HTTPException(status_code=404, detail="No state found")
    return {
        "session_id": session_id, "week_number": snap.week_number,
        "status": session.status, "player_party": session.player_party,
        "role": session.role, "difficulty": session.difficulty,
        "budget_remaining": snap.budget_remaining, "approval_rating": snap.approval_rating,
        "seat_projection_you": snap.seat_projection_you, "seat_projection_opp": snap.seat_projection_opp,
        "win_probability": snap.win_probability, "decisions_made": 0, "total_weeks": 8,
    }


@router.get("/{session_id}/post-mortem")
async def get_post_mortem(session_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    try:
        return await engine.get_post_mortem(db, session_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
