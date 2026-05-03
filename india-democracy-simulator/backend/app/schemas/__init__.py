"""Pydantic v2 request/response schemas for all API endpoints."""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# ─── Enums ────────────────────────────────────────────────────────────────────

class RoleEnum(str, Enum):
    PARTY_LEADER = "party_leader"
    CAMPAIGN_MANAGER = "campaign_manager"
    SWING_VOTER = "swing_voter"
    ELECTION_COMMISSION = "election_commission"


class DifficultyEnum(str, Enum):
    EASY = "easy"
    NORMAL = "normal"
    HARD = "hard"
    EXPERT = "expert"


class SeatClassEnum(str, Enum):
    SUPER_SWING = "super_swing"
    SWING = "swing"
    SAFE = "safe"


# ─── Auth ─────────────────────────────────────────────────────────────────────

class UserRegister(BaseModel):
    email: str = Field(..., min_length=5, max_length=255)
    display_name: str = Field(..., min_length=2, max_length=100)
    password: str = Field(..., min_length=6, max_length=128)


class UserLogin(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: str
    email: str
    display_name: str
    avatar_url: Optional[str] = None
    total_games: int = 0
    wins: int = 0
    favorite_role: Optional[str] = None
    preferred_party: Optional[str] = None

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ─── Constituency ─────────────────────────────────────────────────────────────

class ConstituencyResponse(BaseModel):
    id: str
    state_ut: str
    name: str
    const_no: int
    actual_winner_2024: str
    winning_party_2024: str
    runner_up_2024: str
    runner_up_party_2024: str
    actual_margin_2024: int
    seat_class: str
    default_lean: dict
    region: str

    model_config = {"from_attributes": True}


class ConstituencyListResponse(BaseModel):
    total: int
    constituencies: list[ConstituencyResponse]


# ─── Game ─────────────────────────────────────────────────────────────────────

class GameStartRequest(BaseModel):
    player_party: str = Field(..., min_length=2)
    role: RoleEnum
    difficulty: DifficultyEnum = DifficultyEnum.NORMAL


class ChoiceEffect(BaseModel):
    seat_delta: int = 0
    budget_delta_crore: float = 0.0
    approval_delta: float = 0.0
    state_effects: dict[str, float] = Field(default_factory=dict)


class EventChoice(BaseModel):
    text: str
    effect: ChoiceEffect


class GameEventResponse(BaseModel):
    id: str
    week_number: int
    event_type: str
    headline: str
    body: str
    choices: list[EventChoice]
    affected_states: Optional[list[str]] = None
    civics_lesson: Optional[str] = None

    model_config = {"from_attributes": True}


class OpponentMoveResponse(BaseModel):
    id: str
    week_number: int
    move_type: str
    target_states: Optional[list[str]] = None
    headline: str
    effects: dict

    model_config = {"from_attributes": True}


class SeatProjection(BaseModel):
    party: str
    projected_seats: int
    win_probability: float
    state_breakdown: dict[str, int] = Field(default_factory=dict)


class GameStateResponse(BaseModel):
    session_id: str
    week_number: int
    status: str
    player_party: str
    role: str
    difficulty: str
    budget_remaining: float
    approval_rating: float
    seat_projection_you: int
    seat_projection_opp: int
    win_probability: float
    current_event: Optional[GameEventResponse] = None
    recent_opponent_moves: list[OpponentMoveResponse] = Field(default_factory=list)
    alliance_status: dict = Field(default_factory=dict)
    state_projections: dict[str, dict] = Field(default_factory=dict)
    decisions_made: int = 0
    total_weeks: int = 8


class GameStartResponse(BaseModel):
    session_id: str
    initial_state: GameStateResponse
    available_parties: list[str]
    message: str


class DecisionRequest(BaseModel):
    event_id: str
    choice_index: int = Field(..., ge=0, le=3)


class DecisionResponse(BaseModel):
    new_state: GameStateResponse
    effects_applied: ChoiceEffect
    opponent_move: Optional[OpponentMoveResponse] = None
    civics_lesson: Optional[str] = None
    message: str


# ─── Results ──────────────────────────────────────────────────────────────────

class PostMortemSection(BaseModel):
    title: str
    content: str
    civics_principles: list[str] = Field(default_factory=list)


class PostMortemResponse(BaseModel):
    session_id: str
    won_majority: bool
    final_seats_you: int
    final_seats_opp: int
    player_party: str
    sections: list[PostMortemSection]
    key_turning_points: list[dict]
    state_results: dict[str, dict]


# ─── Leaderboard ──────────────────────────────────────────────────────────────

class LeaderboardEntryResponse(BaseModel):
    rank: int
    display_name: str
    score: int
    player_party: str
    role: str
    seat_margin: int
    created_at: datetime

    model_config = {"from_attributes": True}


class LeaderboardResponse(BaseModel):
    entries: list[LeaderboardEntryResponse]
    total: int


# ─── Feedback ─────────────────────────────────────────────────────────────────

class FeedbackRequest(BaseModel):
    session_id: str
    event_id: str
    rating: int = Field(..., ge=1, le=5)
    feedback_text: Optional[str] = None


class FeedbackResponse(BaseModel):
    id: str
    message: str = "Feedback submitted successfully"
