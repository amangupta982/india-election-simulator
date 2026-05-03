"""Tests for the opponent AI counter-strategy system."""
import pytest
from app.services.opponent_ai import OpponentAI, BATTLEGROUND_STATES


class TestOpponentInit:
    def test_opponent_has_budget(self):
        ai = OpponentAI("Indian National Congress", "Bharatiya Janata Party")
        assert ai.state.budget_crore == 400.0

    def test_opponent_targets_battlegrounds(self):
        ai = OpponentAI("Indian National Congress", "Bharatiya Janata Party")
        assert len(ai.state.target_states) > 0


class TestCounterMoves:
    def test_generates_valid_move(self):
        ai = OpponentAI("Indian National Congress", "Bharatiya Janata Party")
        move = ai.generate_counter_move(
            {"event_type": "rally", "affected_states": ["Uttar Pradesh"]},
            week_number=3, player_strong_states=["Uttar Pradesh"],
        )
        assert "move_type" in move
        assert "headline" in move
        assert "effects" in move
        assert move["week_number"] == 3

    def test_budget_depletes(self):
        ai = OpponentAI("Indian National Congress", "Bharatiya Janata Party")
        initial = ai.state.budget_crore
        ai.generate_counter_move(
            {"event_type": "rally", "affected_states": ["Bihar"]},
            week_number=2, player_strong_states=["Bihar"],
        )
        assert ai.state.budget_crore < initial

    def test_late_game_aggressive(self):
        ai = OpponentAI("Indian National Congress", "Bharatiya Janata Party")
        move = ai.generate_counter_move(
            {"event_type": "rally", "affected_states": ["Maharashtra"]},
            week_number=7, player_strong_states=["Maharashtra"],
        )
        aggressive_types = {"pm_event", "attack_ad", "booth_agent_deploy"}
        assert move["move_type"] in aggressive_types

    def test_effects_have_approval_delta(self):
        ai = OpponentAI("Indian National Congress", "Bharatiya Janata Party")
        move = ai.generate_counter_move(
            {"event_type": "media", "affected_states": ["Delhi"]},
            week_number=4, player_strong_states=["Delhi"],
        )
        assert "approval_delta" in move["effects"]

    def test_moves_history_tracked(self):
        ai = OpponentAI("Indian National Congress", "Bharatiya Janata Party")
        ai.generate_counter_move(
            {"event_type": "rally", "affected_states": ["UP"]},
            week_number=1, player_strong_states=["UP"],
        )
        assert len(ai.state.moves_history) == 1

    def test_no_affected_states_uses_battleground(self):
        ai = OpponentAI("Indian National Congress", "Bharatiya Janata Party")
        move = ai.generate_counter_move(
            {"event_type": "scam", "affected_states": []},
            week_number=3, player_strong_states=[],
        )
        assert len(move["target_states"]) > 0

    def test_get_state(self):
        ai = OpponentAI("Indian National Congress", "Bharatiya Janata Party")
        state = ai.get_state()
        assert state["party"] == "Indian National Congress"
        assert "budget_crore" in state
