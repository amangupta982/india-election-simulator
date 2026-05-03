"""Game router — start, decision, state, end, AI advisor."""
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import User, GameSession, GameStateSnapshot
from app.schemas import GameStartRequest, GameStartResponse, DecisionRequest, DecisionResponse, GameStateResponse
from app.services.game_engine import GameEngine
from app.services.firestore_service import firestore_service
from app.services.vertex_ai_service import vertex_ai_service
from app.routers.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/game", tags=["game"])
engine = GameEngine()


@router.post("/start", response_model=GameStartResponse)
async def start_game(req: GameStartRequest, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await engine.start_game(db, user.id, req.player_party, req.role.value, req.difficulty.value)

    # Sync to Firestore for real-time features
    await firestore_service.save_game_session_meta(result["session_id"], {
        "player_party": req.player_party,
        "role": req.role.value,
        "difficulty": req.difficulty.value,
        "user_id": user.id,
    })
    await firestore_service.save_game_state(result["session_id"], result["initial_state"])
    await firestore_service.log_analytics_event("game_started", {
        "session_id": result["session_id"],
        "player_party": req.player_party,
        "role": req.role.value,
    })

    logger.info(f"Game started: session={result['session_id']} party={req.player_party}")
    return result


@router.post("/{session_id}/decision", response_model=DecisionResponse)
async def make_decision(session_id: str, req: DecisionRequest, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    session = await db.get(GameSession, session_id)
    if not session or session.user_id != user.id:
        raise HTTPException(status_code=404, detail="Session not found")
    try:
        result = await engine.process_decision(db, session_id, req.event_id, req.choice_index)

        # Sync to Firestore
        await firestore_service.save_game_state(session_id, result["new_state"])
        await firestore_service.log_analytics_event("decision_made", {
            "session_id": session_id,
            "event_id": req.event_id,
            "choice_index": req.choice_index,
        })

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


@router.get("/{session_id}/ai-advice")
async def get_ai_advice(session_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Get AI-powered campaign strategy advice from Vertex AI Gemini.

    Analyzes the current game state and provides personalized recommendations
    for the player's next strategic moves.
    """
    session = await db.get(GameSession, session_id)
    if not session or session.user_id != user.id:
        raise HTTPException(status_code=404, detail="Session not found")

    # Get latest snapshot
    result = await db.execute(
        select(GameStateSnapshot).where(GameStateSnapshot.session_id == session_id)
        .order_by(GameStateSnapshot.created_at.desc()).limit(1)
    )
    snap = result.scalar_one_or_none()
    if not snap:
        raise HTTPException(status_code=404, detail="No game state found")

    game_state = {
        "player_party": session.player_party,
        "week_number": snap.week_number,
        "seat_projection_you": snap.seat_projection_you,
        "seat_projection_opp": snap.seat_projection_opp,
        "budget_remaining": snap.budget_remaining,
        "approval_rating": snap.approval_rating,
        "win_probability": snap.win_probability,
    }

    advice = await vertex_ai_service.generate_campaign_advice(game_state)

    if not advice:
        # Fallback advice when Vertex AI is unavailable
        if snap.seat_projection_you < 272:
            deficit = 272 - snap.seat_projection_you
            advice = (
                f"You need {deficit} more seats to reach the majority mark of 272. "
                f"Focus on swing states where margins are thin. "
                f"With ₹{snap.budget_remaining:.0f} crore remaining, prioritize ground game over expensive rallies."
            )
        else:
            advice = (
                f"Strong position at {snap.seat_projection_you} seats! "
                f"Protect your lead by defending swing seats rather than expanding. "
                f"Watch for opponent counter-moves in your weak states."
            )

    await firestore_service.log_analytics_event("ai_advice_requested", {
        "session_id": session_id,
    })

    return {
        "session_id": session_id,
        "advice": advice,
        "powered_by": "vertex_ai" if vertex_ai_service.available else "rule_engine",
        "game_state_summary": {
            "seats": snap.seat_projection_you,
            "target": 272,
            "budget": snap.budget_remaining,
            "win_probability": snap.win_probability,
        },
    }
