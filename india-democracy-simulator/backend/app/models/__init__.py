"""SQLAlchemy ORM models for India Democracy Simulator.

Uses portable types (JSON, String) instead of PostgreSQL-specific
(JSONB, ARRAY, UUID) so the app runs on SQLite out of the box.
"""
from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    JSON,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


# ─── Enums ────────────────────────────────────────────────────────────────────

class SeatClass(str, PyEnum):
    SUPER_SWING = "super_swing"
    SWING = "swing"
    SAFE = "safe"


class Region(str, PyEnum):
    NORTH = "North"
    SOUTH = "South"
    EAST = "East"
    WEST = "West"
    CENTRAL = "Central"
    NORTHEAST = "Northeast"
    UTS = "UTs"


class PlayerRole(str, PyEnum):
    PARTY_LEADER = "party_leader"
    CAMPAIGN_MANAGER = "campaign_manager"
    SWING_VOTER = "swing_voter"
    ELECTION_COMMISSION = "election_commission"


class GameStatus(str, PyEnum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class EventType(str, PyEnum):
    CRISIS = "crisis"
    RALLY = "rally"
    ALLIANCE = "alliance"
    SCAM = "scam"
    MEDIA = "media"
    BOOTH = "booth"
    CASTE_COALITION = "caste_coalition"
    REGIONAL_DEFENSE = "regional_defense"
    OPPOSITION_RESEARCH = "opposition_research"


class OpponentMoveType(str, PyEnum):
    COUNTER_RALLY = "counter_rally"
    ATTACK_AD = "attack_ad"
    POACH_ALLIANCE = "poach_alliance"
    OPPO_RESEARCH = "oppo_research"
    PM_EVENT = "pm_event"
    BOOTH_AGENT_DEPLOY = "booth_agent_deploy"


class Difficulty(str, PyEnum):
    EASY = "easy"
    NORMAL = "normal"
    HARD = "hard"
    EXPERT = "expert"


# ─── Helper ───────────────────────────────────────────────────────────────────

def new_uuid() -> str:
    """Generate a UUID string for use as primary key."""
    return str(uuid.uuid4())


# ─── Models ───────────────────────────────────────────────────────────────────

class Constituency(Base):
    """563 Lok Sabha constituencies seeded from CSV."""
    __tablename__ = "constituencies"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    state_ut: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    const_no: Mapped[int] = mapped_column(Integer, nullable=False)
    seats: Mapped[int] = mapped_column(Integer, default=1)

    # Actual 2024 results
    actual_winner_2024: Mapped[str] = mapped_column(String(200), nullable=False)
    winning_party_2024: Mapped[str] = mapped_column(String(200), nullable=False)
    runner_up_2024: Mapped[str] = mapped_column(String(200), nullable=False)
    runner_up_party_2024: Mapped[str] = mapped_column(String(200), nullable=False)
    actual_margin_2024: Mapped[int] = mapped_column(Integer, nullable=False)

    # Derived classification (stored as plain strings, not DB enums)
    seat_class: Mapped[str] = mapped_column(String(20), nullable=False)
    default_lean: Mapped[dict] = mapped_column(JSON, nullable=False)
    region: Mapped[str] = mapped_column(String(20), nullable=False)

    def __repr__(self) -> str:
        return f"<Constituency {self.name} ({self.state_ut})>"


class User(Base):
    """Registered players."""
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    total_games: Mapped[int] = mapped_column(Integer, default=0)
    wins: Mapped[int] = mapped_column(Integer, default=0)
    favorite_role: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    preferred_party: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    # Relationships
    game_sessions: Mapped[list["GameSession"]] = relationship(back_populates="user")
    leaderboard_entries: Mapped[list["LeaderboardEntry"]] = relationship(
        back_populates="user"
    )

    def __repr__(self) -> str:
        return f"<User {self.display_name}>"


class GameSession(Base):
    """A single playthrough of the simulation."""
    __tablename__ = "game_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False
    )
    player_party: Mapped[str] = mapped_column(String(200), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="in_progress")
    difficulty: Mapped[str] = mapped_column(String(20), default="normal")
    started_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    final_seats_you: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    final_seats_opp: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    won_majority: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="game_sessions")
    snapshots: Mapped[list["GameStateSnapshot"]] = relationship(
        back_populates="session", cascade="all, delete-orphan"
    )
    decisions: Mapped[list["PlayerDecision"]] = relationship(
        back_populates="session", cascade="all, delete-orphan"
    )
    events: Mapped[list["GameEvent"]] = relationship(
        back_populates="session", cascade="all, delete-orphan"
    )
    opponent_moves: Mapped[list["OpponentMove"]] = relationship(
        back_populates="session", cascade="all, delete-orphan"
    )


class GameStateSnapshot(Base):
    """Weekly snapshot of the full game state."""
    __tablename__ = "game_state_snapshots"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    session_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("game_sessions.id"), nullable=False
    )
    week_number: Mapped[int] = mapped_column(Integer, nullable=False)
    budget_remaining: Mapped[float] = mapped_column(Float, nullable=False)
    approval_rating: Mapped[float] = mapped_column(Float, nullable=False)
    seat_projection_you: Mapped[int] = mapped_column(Integer, nullable=False)
    seat_projection_opp: Mapped[int] = mapped_column(Integer, nullable=False)
    win_probability: Mapped[float] = mapped_column(Float, nullable=False)
    constituency_leans: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )

    # Relationships
    session: Mapped["GameSession"] = relationship(back_populates="snapshots")


class PlayerDecision(Base):
    """A choice the player made in response to an event."""
    __tablename__ = "player_decisions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    session_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("game_sessions.id"), nullable=False
    )
    week_number: Mapped[int] = mapped_column(Integer, nullable=False)
    event_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("game_events.id"), nullable=False
    )
    choice_index: Mapped[int] = mapped_column(Integer, nullable=False)
    choice_text: Mapped[str] = mapped_column(Text, nullable=False)
    effects_applied: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )

    # Relationships
    session: Mapped["GameSession"] = relationship(back_populates="decisions")
    event: Mapped["GameEvent"] = relationship(back_populates="decision")


class GameEvent(Base):
    """An AI-generated or static event that the player responds to."""
    __tablename__ = "game_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    session_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("game_sessions.id"), nullable=False
    )
    week_number: Mapped[int] = mapped_column(Integer, nullable=False)
    event_type: Mapped[str] = mapped_column(String(30), nullable=False)
    headline: Mapped[str] = mapped_column(String(200), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    choices: Mapped[dict] = mapped_column(JSON, nullable=False)
    affected_states: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    generated_by: Mapped[str] = mapped_column(
        String(50), default="static_pool"
    )  # "ai_model" | "static_pool"
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )

    # Relationships
    session: Mapped["GameSession"] = relationship(back_populates="events")
    decision: Mapped[Optional["PlayerDecision"]] = relationship(
        back_populates="event", uselist=False
    )
    feedback: Mapped[list["ModelFeedback"]] = relationship(back_populates="event")


class OpponentMove(Base):
    """An AI opponent's counter-strategy move."""
    __tablename__ = "opponent_moves"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    session_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("game_sessions.id"), nullable=False
    )
    week_number: Mapped[int] = mapped_column(Integer, nullable=False)
    move_type: Mapped[str] = mapped_column(String(30), nullable=False)
    target_states: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    headline: Mapped[str] = mapped_column(String(200), nullable=False)
    effects: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )

    # Relationships
    session: Mapped["GameSession"] = relationship(back_populates="opponent_moves")


class LeaderboardEntry(Base):
    """Top scores."""
    __tablename__ = "leaderboard"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False
    )
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    player_party: Mapped[str] = mapped_column(String(200), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False)
    seat_margin: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="leaderboard_entries")


class ModelFeedback(Base):
    """User feedback on AI-generated events."""
    __tablename__ = "model_feedback"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    session_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("game_sessions.id"), nullable=False
    )
    event_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("game_events.id"), nullable=False
    )
    rating: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-5
    feedback_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )

    # Relationships
    event: Mapped["GameEvent"] = relationship(back_populates="feedback")
