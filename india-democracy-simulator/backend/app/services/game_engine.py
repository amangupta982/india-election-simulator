"""
Game Engine — session lifecycle, turn progression, and state management.
"""
from __future__ import annotations
from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import (
    GameSession, GameStateSnapshot, GameEvent, PlayerDecision,
    OpponentMove, Constituency, GameStatus, EventType,
    OpponentMoveType, LeaderboardEntry,
)
from app.services.seat_math import SeatMathEngine
from app.services.alliance_engine import AllianceEngine
from app.services.opponent_ai import OpponentAI
from app.services.ai_inference import AIInferenceService
from app.config import get_settings

settings = get_settings()

# Determine the default opponent party
PARTY_OPPONENT_MAP = {
    "Bharatiya Janata Party": "Indian National Congress",
    "Indian National Congress": "Bharatiya Janata Party",
    "Samajwadi Party": "Bharatiya Janata Party",
    "All India Trinamool Congress": "Bharatiya Janata Party",
    "Dravida Munnetra Kazhagam": "Bharatiya Janata Party",
}


class GameEngine:
    """Manages the full lifecycle of a game session."""

    def __init__(self):
        self.ai_service = AIInferenceService()

    async def start_game(
        self, db: AsyncSession, user_id: str,
        player_party: str, role: str, difficulty: str = "normal",
    ) -> dict:
        """Create a new game session and return initial state."""
        # Load all constituencies from DB
        result = await db.execute(select(Constituency))
        constituencies = result.scalars().all()
        const_dicts = [
            {
                "name": c.name, "state_ut": c.state_ut, "const_no": c.const_no,
                "seat_class": c.seat_class, "region": c.region,
                "winning_party_2024": c.winning_party_2024,
                "runner_up_party_2024": c.runner_up_party_2024,
                "actual_margin_2024": c.actual_margin_2024,
            }
            for c in constituencies
        ]

        # Initialize engines
        seat_engine = SeatMathEngine(player_party, const_dicts, difficulty)
        alliance = AllianceEngine(player_party)
        opponent_party = PARTY_OPPONENT_MAP.get(player_party, "Indian National Congress")
        opponent = OpponentAI(opponent_party, player_party)

        # Run initial simulation
        sim_result = seat_engine.run_simulation(seed=42)

        # Create game session
        session = GameSession(
            user_id=user_id, player_party=player_party,
            role=role, status=GameStatus.IN_PROGRESS.value, difficulty=difficulty,
        )
        db.add(session)
        await db.flush()

        # Create initial snapshot
        snapshot = GameStateSnapshot(
            session_id=session.id, week_number=0,
            budget_remaining=settings.starting_budget_crore,
            approval_rating=settings.starting_approval,
            seat_projection_you=sim_result.projected_seats_player,
            seat_projection_opp=sim_result.projected_seats_opponent,
            win_probability=sim_result.win_probability,
            constituency_leans=seat_engine.get_all_constituency_leans(),
        )
        db.add(snapshot)

        # Generate first event
        game_state = {
            "week_number": 1, "player_party": player_party,
            "budget_crore": settings.starting_budget_crore,
            "approval_pct": settings.starting_approval,
            "seat_projection": sim_result.projected_seats_player,
        }
        event_data = self.ai_service.generate_event(game_state)
        event = GameEvent(
            session_id=session.id, week_number=1,
            event_type=event_data["event_type"], headline=event_data["headline"],
            body=event_data["body"], choices=event_data["choices"],
            affected_states=event_data.get("affected_states", []),
            generated_by="static_pool",
        )
        db.add(event)
        await db.flush()

        return {
            "session_id": str(session.id),
            "initial_state": {
                "session_id": str(session.id), "week_number": 1,
                "status": "in_progress", "player_party": player_party,
                "role": role, "difficulty": difficulty,
                "budget_remaining": settings.starting_budget_crore,
                "approval_rating": settings.starting_approval,
                "seat_projection_you": sim_result.projected_seats_player,
                "seat_projection_opp": sim_result.projected_seats_opponent,
                "win_probability": sim_result.win_probability,
                "current_event": {
                    "id": str(event.id), "week_number": 1,
                    "event_type": event_data["event_type"],
                    "headline": event_data["headline"],
                    "body": event_data["body"],
                    "choices": event_data["choices"],
                    "affected_states": event_data.get("affected_states", []),
                    "civics_lesson": event_data.get("civics_lesson"),
                },
                "recent_opponent_moves": [],
                "alliance_status": alliance.get_status(),
                "state_projections": sim_result.state_breakdown,
                "decisions_made": 0, "total_weeks": 8,
            },
            "available_parties": list(PARTY_OPPONENT_MAP.keys()),
            "message": f"Campaign begins! You're leading {player_party} for 8 weeks. Majority = 272 seats.",
        }

    async def process_decision(
        self, db: AsyncSession, session_id: str,
        event_id: str, choice_index: int,
    ) -> dict:
        """Process a player decision and advance the game."""
        session = await db.get(GameSession, session_id)
        if not session or session.status != GameStatus.IN_PROGRESS.value:
            raise ValueError("Invalid or completed session")

        # Get current snapshot
        result = await db.execute(
            select(GameStateSnapshot)
            .where(GameStateSnapshot.session_id == session_id)
            .order_by(GameStateSnapshot.created_at.desc()).limit(1)
        )
        snapshot = result.scalar_one()

        # Get the event
        event = await db.get(GameEvent, event_id)
        if not event:
            raise ValueError("Event not found")

        choices = event.choices if isinstance(event.choices, list) else event.choices.get("choices", event.choices)
        if choice_index >= len(choices):
            raise ValueError("Invalid choice index")

        chosen = choices[choice_index]
        effect = chosen.get("effect", {})

        # Apply effects
        new_budget = snapshot.budget_remaining + effect.get("budget_delta_crore", 0)
        new_approval = max(0, min(100, snapshot.approval_rating + effect.get("approval_delta", 0)))

        # Rebuild seat engine from snapshot leans
        constituencies_result = await db.execute(select(Constituency))
        all_const = constituencies_result.scalars().all()
        const_dicts = [
            {
                "name": c.name, "state_ut": c.state_ut, "const_no": c.const_no,
                "seat_class": c.seat_class, "region": c.region,
                "winning_party_2024": c.winning_party_2024,
                "runner_up_party_2024": c.runner_up_party_2024,
                "actual_margin_2024": c.actual_margin_2024,
            }
            for c in all_const
        ]
        seat_engine = SeatMathEngine(session.player_party, const_dicts, session.difficulty)

        # Override lean scores from snapshot
        for c in seat_engine.constituencies:
            if c.name in snapshot.constituency_leans:
                c.lean_score = snapshot.constituency_leans[c.name]

        # Apply decision effects to lean scores
        seat_engine.apply_choice_effects(effect)

        # Run new simulation
        sim = seat_engine.run_simulation()
        week = snapshot.week_number + 1

        # Opponent counter-move
        opponent_party = PARTY_OPPONENT_MAP.get(session.player_party, "Indian National Congress")
        opponent = OpponentAI(opponent_party, session.player_party)
        player_strong = [s for s, d in sim.state_breakdown.items() if d.get("player", 0) > d.get("opponent", 0)]

        opp_move_data = opponent.generate_counter_move(
            {"event_type": event.event_type, "affected_states": event.affected_states or []},
            week, player_strong[:5],
        )

        # Apply opponent effects
        opp_effects = opp_move_data.get("effects", {})
        opp_state_effects = opp_effects.get("state_effects", {})
        seat_engine.apply_state_effects(opp_state_effects)
        new_approval += opp_effects.get("approval_delta", 0)
        new_approval = max(0, min(100, new_approval))

        # Re-run sim after opponent move
        sim = seat_engine.run_simulation()

        # Save decision
        decision = PlayerDecision(
            session_id=session_id, week_number=week, event_id=event_id,
            choice_index=choice_index, choice_text=chosen.get("text", ""),
            effects_applied=effect,
        )
        db.add(decision)

        # Save opponent move
        opp_move = OpponentMove(
            session_id=session_id, week_number=week,
            move_type=opp_move_data["move_type"],
            target_states=opp_move_data.get("target_states", []),
            headline=opp_move_data["headline"], effects=opp_effects,
        )
        db.add(opp_move)

        # Save new snapshot
        new_snapshot = GameStateSnapshot(
            session_id=session_id, week_number=week,
            budget_remaining=new_budget, approval_rating=new_approval,
            seat_projection_you=sim.projected_seats_player,
            seat_projection_opp=sim.projected_seats_opponent,
            win_probability=sim.win_probability,
            constituency_leans=seat_engine.get_all_constituency_leans(),
        )
        db.add(new_snapshot)

        # Check if game over
        is_final = week >= settings.campaign_weeks
        next_event = None
        civics_lesson = None

        if is_final:
            session.status = GameStatus.COMPLETED.value
            session.ended_at = datetime.utcnow()
            session.final_seats_you = sim.projected_seats_player
            session.final_seats_opp = sim.projected_seats_opponent
            session.won_majority = sim.projected_seats_player >= settings.majority_threshold
        else:
            # Generate next event
            gs = {"week_number": week + 1, "player_party": session.player_party,
                  "budget_crore": new_budget, "approval_pct": new_approval,
                  "seat_projection": sim.projected_seats_player}
            event_data = self.ai_service.generate_event(gs)
            next_ev = GameEvent(
                session_id=session_id, week_number=week + 1,
                event_type=event_data["event_type"], headline=event_data["headline"],
                body=event_data["body"], choices=event_data["choices"],
                affected_states=event_data.get("affected_states", []),
                generated_by="static_pool",
            )
            db.add(next_ev)
            await db.flush()
            next_event = {
                "id": str(next_ev.id), "week_number": week + 1,
                "event_type": event_data["event_type"],
                "headline": event_data["headline"], "body": event_data["body"],
                "choices": event_data["choices"],
                "affected_states": event_data.get("affected_states", []),
                "civics_lesson": event_data.get("civics_lesson"),
            }
            civics_lesson = event_data.get("civics_lesson")

        await db.flush()

        # Count decisions
        dec_count = await db.execute(
            select(PlayerDecision).where(PlayerDecision.session_id == session_id)
        )
        decisions_made = len(dec_count.scalars().all())

        # Get status as string
        status_str = session.status if isinstance(session.status, str) else session.status.value

        return {
            "new_state": {
                "session_id": str(session_id), "week_number": week + 1 if not is_final else week,
                "status": status_str,
                "player_party": session.player_party, "role": session.role,
                "difficulty": session.difficulty,
                "budget_remaining": new_budget, "approval_rating": new_approval,
                "seat_projection_you": sim.projected_seats_player,
                "seat_projection_opp": sim.projected_seats_opponent,
                "win_probability": sim.win_probability,
                "current_event": next_event,
                "recent_opponent_moves": [{"id": str(opp_move.id), "week_number": week,
                    "move_type": opp_move_data["move_type"],
                    "target_states": opp_move_data.get("target_states"),
                    "headline": opp_move_data["headline"], "effects": opp_effects}],
                "alliance_status": {}, "state_projections": sim.state_breakdown,
                "decisions_made": decisions_made, "total_weeks": 8,
            },
            "effects_applied": effect,
            "opponent_move": {"id": str(opp_move.id), "week_number": week,
                "move_type": opp_move_data["move_type"],
                "target_states": opp_move_data.get("target_states"),
                "headline": opp_move_data["headline"], "effects": opp_effects},
            "civics_lesson": civics_lesson,
            "message": "Results Day!" if is_final else f"Week {week} complete. {8 - week} weeks remain.",
        }

    async def get_post_mortem(self, db: AsyncSession, session_id: str) -> dict:
        """Generate post-mortem for a completed game."""
        session = await db.get(GameSession, session_id)
        if not session:
            raise ValueError("Session not found")

        # Get decisions
        result = await db.execute(
            select(PlayerDecision).where(PlayerDecision.session_id == session_id)
            .order_by(PlayerDecision.week_number)
        )
        decisions = [{"week": d.week_number, "choice": d.choice_text, "effects": d.effects_applied}
                     for d in result.scalars().all()]

        # Get final snapshot
        snap_result = await db.execute(
            select(GameStateSnapshot).where(GameStateSnapshot.session_id == session_id)
            .order_by(GameStateSnapshot.created_at.desc()).limit(1)
        )
        final_snap = snap_result.scalar_one_or_none()

        session_data = {
            "won_majority": session.won_majority or False,
            "final_seats_you": session.final_seats_you or 0,
            "final_seats_opp": session.final_seats_opp or 0,
            "player_party": session.player_party,
            "decisions": decisions,
            "state_breakdown": final_snap.constituency_leans if final_snap else {},
        }
        return self.ai_service.generate_post_mortem(session_data)
