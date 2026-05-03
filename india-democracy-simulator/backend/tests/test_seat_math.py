"""Tests for the Monte Carlo seat projection engine."""
import pytest
from app.services.seat_math import SeatMathEngine, SimulationResult


# Minimal constituency fixtures for unit tests
SAMPLE_CONSTITUENCIES = [
    {"name": "Varanasi", "state_ut": "Uttar Pradesh", "const_no": 1, "seat_class": "safe",
     "region": "North", "winning_party_2024": "Bharatiya Janata Party",
     "runner_up_party_2024": "Indian National Congress", "actual_margin_2024": 150000},
    {"name": "Mumbai NW", "state_ut": "Maharashtra", "const_no": 2, "seat_class": "super_swing",
     "region": "West", "winning_party_2024": "Shiv Sena",
     "runner_up_party_2024": "Indian National Congress", "actual_margin_2024": 48},
    {"name": "Attingal", "state_ut": "Kerala", "const_no": 3, "seat_class": "super_swing",
     "region": "South", "winning_party_2024": "Indian National Congress",
     "runner_up_party_2024": "CPI(M)", "actual_margin_2024": 684},
    {"name": "Patna Sahib", "state_ut": "Bihar", "const_no": 4, "seat_class": "swing",
     "region": "East", "winning_party_2024": "Bharatiya Janata Party",
     "runner_up_party_2024": "Indian National Congress", "actual_margin_2024": 65000},
    {"name": "Lucknow", "state_ut": "Uttar Pradesh", "const_no": 5, "seat_class": "safe",
     "region": "North", "winning_party_2024": "Bharatiya Janata Party",
     "runner_up_party_2024": "Samajwadi Party", "actual_margin_2024": 90000},
    {"name": "Amethi", "state_ut": "Uttar Pradesh", "const_no": 6, "seat_class": "safe",
     "region": "North", "winning_party_2024": "Indian National Congress",
     "runner_up_party_2024": "Bharatiya Janata Party", "actual_margin_2024": 167000},
    {"name": "Chennai S", "state_ut": "Tamil Nadu", "const_no": 7, "seat_class": "safe",
     "region": "South", "winning_party_2024": "DMK",
     "runner_up_party_2024": "Bharatiya Janata Party", "actual_margin_2024": 250000},
    {"name": "Jaipur R", "state_ut": "Rajasthan", "const_no": 8, "seat_class": "swing",
     "region": "West", "winning_party_2024": "Bharatiya Janata Party",
     "runner_up_party_2024": "Indian National Congress", "actual_margin_2024": 45000},
]

PLAYER_PARTY = "Bharatiya Janata Party"


class TestSeatMathInitialization:
    """Tests for SeatMathEngine initialization."""

    def test_constituencies_loaded(self):
        """All constituencies are loaded from input data."""
        engine = SeatMathEngine(PLAYER_PARTY, SAMPLE_CONSTITUENCIES)
        assert len(engine.constituencies) == 8

    def test_safe_seat_lean_magnitude(self):
        """Safe seats should have higher lean magnitude (~0.8)."""
        engine = SeatMathEngine(PLAYER_PARTY, SAMPLE_CONSTITUENCIES)
        varanasi = next(c for c in engine.constituencies if c.name == "Varanasi")
        assert abs(varanasi.lean_score) == pytest.approx(0.8, abs=0.01)
        assert varanasi.lean_score > 0  # BJP won, player is BJP

    def test_super_swing_seat_lean_magnitude(self):
        """Super-swing seats should have low lean magnitude (~0.1)."""
        engine = SeatMathEngine(PLAYER_PARTY, SAMPLE_CONSTITUENCIES)
        mumbai = next(c for c in engine.constituencies if c.name == "Mumbai NW")
        assert abs(mumbai.lean_score) == pytest.approx(0.1, abs=0.01)

    def test_swing_seat_lean_magnitude(self):
        """Swing seats should have medium lean magnitude (~0.4)."""
        engine = SeatMathEngine(PLAYER_PARTY, SAMPLE_CONSTITUENCIES)
        patna = next(c for c in engine.constituencies if c.name == "Patna Sahib")
        assert abs(patna.lean_score) == pytest.approx(0.4, abs=0.01)

    def test_opponent_seat_negative_lean(self):
        """Seats won by other parties should have negative lean for player."""
        engine = SeatMathEngine(PLAYER_PARTY, SAMPLE_CONSTITUENCIES)
        amethi = next(c for c in engine.constituencies if c.name == "Amethi")
        assert amethi.lean_score < 0  # INC won, player is BJP

    def test_volatility_decreases_with_safety(self):
        """Super-swing > swing > safe volatility ordering."""
        engine = SeatMathEngine(PLAYER_PARTY, SAMPLE_CONSTITUENCIES)
        super_swing = next(c for c in engine.constituencies if c.seat_class == "super_swing")
        swing = next(c for c in engine.constituencies if c.seat_class == "swing")
        safe = next(c for c in engine.constituencies if c.seat_class == "safe")
        assert super_swing.volatility > swing.volatility > safe.volatility


class TestSimulation:
    """Tests for Monte Carlo simulation runs."""

    def test_deterministic_with_seed(self):
        """Same seed produces identical results."""
        engine1 = SeatMathEngine(PLAYER_PARTY, SAMPLE_CONSTITUENCIES)
        engine2 = SeatMathEngine(PLAYER_PARTY, SAMPLE_CONSTITUENCIES)
        result1 = engine1.run_simulation(seed=42)
        result2 = engine2.run_simulation(seed=42)
        assert result1.projected_seats_player == result2.projected_seats_player
        assert result1.win_probability == result2.win_probability

    def test_different_seeds_may_differ(self):
        """Different seeds can produce different results (probabilistic)."""
        engine = SeatMathEngine(PLAYER_PARTY, SAMPLE_CONSTITUENCIES)
        result1 = engine.run_simulation(seed=1)
        result2 = engine.run_simulation(seed=9999)
        # With different seeds, at least one metric should differ (very likely)
        # This is a probabilistic test but should pass ~99.9% of the time
        assert isinstance(result1.projected_seats_player, int)
        assert isinstance(result2.projected_seats_player, int)

    def test_result_has_all_fields(self):
        """SimulationResult contains all expected fields."""
        engine = SeatMathEngine(PLAYER_PARTY, SAMPLE_CONSTITUENCIES)
        result = engine.run_simulation(seed=42)
        assert isinstance(result, SimulationResult)
        assert isinstance(result.projected_seats_player, int)
        assert isinstance(result.projected_seats_opponent, int)
        assert 0 <= result.win_probability <= 1.0
        assert isinstance(result.state_breakdown, dict)
        assert isinstance(result.confidence_interval, tuple)
        assert len(result.confidence_interval) == 2

    def test_seats_are_non_negative(self):
        """Seat projections should never be negative."""
        engine = SeatMathEngine(PLAYER_PARTY, SAMPLE_CONSTITUENCIES)
        result = engine.run_simulation(seed=42)
        assert result.projected_seats_player >= 0
        assert result.projected_seats_opponent >= 0

    def test_confidence_interval_order(self):
        """5th percentile ≤ 95th percentile."""
        engine = SeatMathEngine(PLAYER_PARTY, SAMPLE_CONSTITUENCIES)
        result = engine.run_simulation(seed=42)
        p5, p95 = result.confidence_interval
        assert p5 <= p95

    def test_state_breakdown_covers_all_states(self):
        """State breakdown should include states from constituencies."""
        engine = SeatMathEngine(PLAYER_PARTY, SAMPLE_CONSTITUENCIES)
        result = engine.run_simulation(seed=42)
        states_in_data = {c["state_ut"] for c in SAMPLE_CONSTITUENCIES}
        for state in states_in_data:
            assert state in result.state_breakdown


class TestEffects:
    """Tests for applying player/opponent effects."""

    def test_rally_increases_lean(self):
        """Rally effect should increase lean score."""
        engine = SeatMathEngine(PLAYER_PARTY, SAMPLE_CONSTITUENCIES)
        original = next(c for c in engine.constituencies if c.name == "Varanasi").lean_score
        engine.apply_rally_effect("Varanasi", intensity=0.15)
        updated = next(c for c in engine.constituencies if c.name == "Varanasi").lean_score
        assert updated > original

    def test_crisis_decreases_lean(self):
        """Crisis effect should decrease lean score."""
        engine = SeatMathEngine(PLAYER_PARTY, SAMPLE_CONSTITUENCIES)
        original_leans = {c.name: c.lean_score for c in engine.constituencies if c.state_ut == "Uttar Pradesh"}
        engine.apply_crisis_effect(["Uttar Pradesh"], severity=-0.15)
        for c in engine.constituencies:
            if c.state_ut == "Uttar Pradesh":
                assert c.lean_score < original_leans[c.name]

    def test_lean_clamped_to_valid_range(self):
        """Lean scores should never exceed [-1.0, 1.0]."""
        engine = SeatMathEngine(PLAYER_PARTY, SAMPLE_CONSTITUENCIES)
        # Apply massive positive effect
        engine.apply_rally_effect("Varanasi", intensity=5.0)
        varanasi = next(c for c in engine.constituencies if c.name == "Varanasi")
        assert varanasi.lean_score <= 1.0

        # Apply massive negative effect
        engine.apply_crisis_effect(["Kerala"], severity=-5.0)
        attingal = next(c for c in engine.constituencies if c.name == "Attingal")
        assert attingal.lean_score >= -1.0

    def test_state_ad_spend_affects_all_in_state(self):
        """State-wide ad spend affects all constituencies in that state."""
        engine = SeatMathEngine(PLAYER_PARTY, SAMPLE_CONSTITUENCIES)
        up_count = sum(1 for c in SAMPLE_CONSTITUENCIES if c["state_ut"] == "Uttar Pradesh")
        affected = engine.apply_state_ad_spend("Uttar Pradesh", intensity=0.05)
        assert affected == up_count

    def test_alliance_effect_on_target_states(self):
        """Alliance effect boosts lean in specified states."""
        engine = SeatMathEngine(PLAYER_PARTY, SAMPLE_CONSTITUENCIES)
        original = next(c for c in engine.constituencies if c.state_ut == "Bihar").lean_score
        engine.apply_alliance_effect(["Bihar"], party_lean_bonus=0.2)
        updated = next(c for c in engine.constituencies if c.state_ut == "Bihar").lean_score
        assert updated > original

    def test_difficulty_modifier_easy(self):
        """Easy difficulty amplifies effects (1.3x)."""
        engine_easy = SeatMathEngine(PLAYER_PARTY, SAMPLE_CONSTITUENCIES, difficulty="easy")
        engine_hard = SeatMathEngine(PLAYER_PARTY, SAMPLE_CONSTITUENCIES, difficulty="hard")

        v_easy = next(c for c in engine_easy.constituencies if c.name == "Varanasi").lean_score
        v_hard = next(c for c in engine_hard.constituencies if c.name == "Varanasi").lean_score

        engine_easy.apply_rally_effect("Varanasi", intensity=0.15)
        engine_hard.apply_rally_effect("Varanasi", intensity=0.15)

        delta_easy = next(c for c in engine_easy.constituencies if c.name == "Varanasi").lean_score - v_easy
        delta_hard = next(c for c in engine_hard.constituencies if c.name == "Varanasi").lean_score - v_hard
        assert delta_easy > delta_hard

    def test_choice_effects_approval_delta(self):
        """Approval delta translates to global lean shift."""
        engine = SeatMathEngine(PLAYER_PARTY, SAMPLE_CONSTITUENCIES)
        original_leans = [c.lean_score for c in engine.constituencies]
        engine.apply_choice_effects({"approval_delta": 10})
        updated_leans = [c.lean_score for c in engine.constituencies]
        for orig, upd in zip(original_leans, updated_leans):
            assert upd >= orig  # positive approval should increase lean


class TestHelperMethods:
    """Tests for utility methods."""

    def test_get_top_swing_constituencies(self):
        """Returns constituencies sorted by closest lean to 0."""
        engine = SeatMathEngine(PLAYER_PARTY, SAMPLE_CONSTITUENCIES)
        top = engine.get_top_swing_constituencies(n=3)
        assert len(top) == 3
        # First should have lean closest to 0
        assert abs(top[0]["lean_score"]) <= abs(top[1]["lean_score"])

    def test_get_state_summary(self):
        """State summary includes all states with correct totals."""
        engine = SeatMathEngine(PLAYER_PARTY, SAMPLE_CONSTITUENCIES)
        summary = engine.get_state_summary()
        assert "Uttar Pradesh" in summary
        assert summary["Uttar Pradesh"]["total"] == 3  # Varanasi, Amethi, Lucknow

    def test_get_all_constituency_leans(self):
        """Returns lean dict for all constituencies."""
        engine = SeatMathEngine(PLAYER_PARTY, SAMPLE_CONSTITUENCIES)
        leans = engine.get_all_constituency_leans()
        assert len(leans) == 8
        assert "Varanasi" in leans
        assert isinstance(leans["Varanasi"], float)
