"""Leaderboard and feedback routers."""
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models import LeaderboardEntry, User, ModelFeedback
from app.schemas import LeaderboardResponse, LeaderboardEntryResponse, FeedbackRequest, FeedbackResponse
from app.routers.auth import get_current_user

leaderboard_router = APIRouter(prefix="/leaderboard", tags=["leaderboard"])
feedback_router = APIRouter(prefix="/feedback", tags=["feedback"])


@leaderboard_router.get("", response_model=LeaderboardResponse)
async def get_leaderboard(
    party: str = Query(None), role: str = Query(None),
    limit: int = Query(100, le=100), db: AsyncSession = Depends(get_db),
):
    q = select(LeaderboardEntry, User.display_name).join(User).order_by(LeaderboardEntry.score.desc())
    if party:
        q = q.where(LeaderboardEntry.player_party == party)
    if role:
        q = q.where(LeaderboardEntry.role == role)
    q = q.limit(limit)
    result = await db.execute(q)
    rows = result.all()
    entries = []
    for i, (entry, name) in enumerate(rows, 1):
        entries.append(LeaderboardEntryResponse(
            rank=i, display_name=name, score=entry.score,
            player_party=entry.player_party, role=entry.role,
            seat_margin=entry.seat_margin, created_at=entry.created_at,
        ))
    return LeaderboardResponse(entries=entries, total=len(entries))


@feedback_router.post("/event", response_model=FeedbackResponse)
async def submit_feedback(
    req: FeedbackRequest, user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    fb = ModelFeedback(
        session_id=req.session_id, event_id=req.event_id,
        rating=req.rating, feedback_text=req.feedback_text,
    )
    db.add(fb)
    await db.flush()
    return FeedbackResponse(id=fb.id)
