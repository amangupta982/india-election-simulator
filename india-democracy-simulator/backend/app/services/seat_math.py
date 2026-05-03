"""
Lok Sabha Seat Calculation Engine — Monte Carlo simulation.

Core engine that models 543 constituencies with lean scores,
applies player/opponent effects, and runs Monte Carlo simulations
to project seat counts and win probabilities.
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Optional

from app.config import get_settings

settings = get_settings()


@dataclass
class ConstituencyState:
    """Runtime state of a single constituency during a game."""
    name: str
    state_ut: str
    const_no: int
    seat_class: str  # super_swing, swing, safe
    region: str
    winning_party_2024: str
    runner_up_party_2024: str
    actual_margin_2024: int
    lean_score: float  # -1.0 (certain loss) to +1.0 (certain win)
    volatility: float  # how much random noise this seat gets

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "state_ut": self.state_ut,
            "seat_class": self.seat_class,
            "lean_score": round(self.lean_score, 4),
            "winning_party_2024": self.winning_party_2024,
        }


@dataclass
class SimulationResult:
    """Result of a Monte Carlo simulation run."""
    projected_seats_player: int
    projected_seats_opponent: int
    projected_seats_others: int
    win_probability: float
    state_breakdown: dict[str, dict[str, int]]  # state -> {player: N, opp: N, others: N}
    confidence_interval: tuple[int, int]  # 5th and 95th percentile
    swing_seats_won: int
    super_swing_seats_won: int


class SeatMathEngine:
    """
    Monte Carlo simulation engine for Lok Sabha seat projections.

    Manages constituency lean scores and runs probabilistic simulations
    to project seat counts. All math grounded in real 2024 election data.
    """

    def __init__(
        self,
        player_party: str,
        constituencies: list[dict],
        difficulty: str = "normal",
    ):
        self.player_party = player_party
        self.difficulty = difficulty
        self.total_seats = settings.total_lok_sabha_seats
        self.majority = settings.majority_threshold
        self.iterations = settings.monte_carlo_iterations

        # Difficulty modifiers
        self._difficulty_multipliers = {
            "easy": 1.3,
            "normal": 1.0,
            "hard": 0.7,
            "expert": 0.5,
        }

        # Initialize constituency states from DB data
        self.constituencies: list[ConstituencyState] = []
        self._initialize_constituencies(constituencies)

    def _initialize_constituencies(self, raw_constituencies: list[dict]) -> None:
        """Set initial lean scores based on 2024 actual results."""
        for c in raw_constituencies:
            winning_party = c["winning_party_2024"]
            seat_class = c["seat_class"]

            # Base lean: positive = favors player, negative = favors opponent
            if winning_party == self.player_party:
                base_lean = self._initial_lean_for_class(seat_class, positive=True)
            else:
                base_lean = self._initial_lean_for_class(seat_class, positive=False)

            # Volatility: how much random noise affects this seat
            volatility = self._volatility_for_class(seat_class)

            self.constituencies.append(ConstituencyState(
                name=c["name"],
                state_ut=c["state_ut"],
                const_no=c["const_no"],
                seat_class=seat_class,
                region=c["region"],
                winning_party_2024=winning_party,
                runner_up_party_2024=c["runner_up_party_2024"],
                actual_margin_2024=c["actual_margin_2024"],
                lean_score=base_lean,
                volatility=volatility,
            ))

    @staticmethod
    def _initial_lean_for_class(seat_class: str, positive: bool) -> float:
        """Set initial lean based on seat competitiveness."""
        leans = {
            "super_swing": 0.1,
            "swing": 0.4,
            "safe": 0.8,
        }
        base = leans.get(seat_class, 0.5)
        return base if positive else -base

    @staticmethod
    def _volatility_for_class(seat_class: str) -> float:
        """Super-swing seats have highest randomness."""
        return {
            "super_swing": 0.35,
            "swing": 0.20,
            "safe": 0.08,
        }.get(seat_class, 0.15)

    def apply_rally_effect(
        self, constituency_name: str, intensity: float = 0.15
    ) -> int:
        """
        Direct rally in a specific constituency.
        Returns number of constituencies affected.
        """
        multiplier = self._difficulty_multipliers.get(self.difficulty, 1.0)
        adjusted = intensity * multiplier
        count = 0
        for c in self.constituencies:
            if c.name == constituency_name:
                c.lean_score = max(-1.0, min(1.0, c.lean_score + adjusted))
                count += 1
        return count

    def apply_state_ad_spend(
        self, state: str, intensity: float = 0.05
    ) -> int:
        """
        State-wide advertising spend affects all constituencies in a state.
        Returns number of constituencies affected.
        """
        multiplier = self._difficulty_multipliers.get(self.difficulty, 1.0)
        adjusted = intensity * multiplier
        count = 0
        for c in self.constituencies:
            if c.state_ut == state:
                c.lean_score = max(-1.0, min(1.0, c.lean_score + adjusted))
                count += 1
        return count

    def apply_alliance_effect(
        self, target_states: list[str], party_lean_bonus: float = 0.2
    ) -> int:
        """
        Alliance with a regional party boosts lean in their stronghold states.
        """
        multiplier = self._difficulty_multipliers.get(self.difficulty, 1.0)
        adjusted = party_lean_bonus * multiplier
        count = 0
        for c in self.constituencies:
            if c.state_ut in target_states:
                c.lean_score = max(-1.0, min(1.0, c.lean_score + adjusted))
                count += 1
        return count

    def apply_crisis_effect(
        self, affected_states: list[str], severity: float = -0.15
    ) -> int:
        """
        Crisis/scam reduces lean across affected states.
        Severity should be negative (typically -0.10 to -0.25).
        """
        count = 0
        for c in self.constituencies:
            if c.state_ut in affected_states:
                c.lean_score = max(-1.0, min(1.0, c.lean_score + severity))
                count += 1
        return count

    def apply_state_effects(self, state_effects: dict[str, float]) -> None:
        """Apply a dict of {state: lean_delta} effects."""
        for state, delta in state_effects.items():
            for c in self.constituencies:
                if c.state_ut == state:
                    c.lean_score = max(-1.0, min(1.0, c.lean_score + delta))

    def apply_choice_effects(self, effects: dict) -> None:
        """Apply the full effects dict from an event choice."""
        # Global approval/seat delta translates to a small lean shift everywhere
        approval_delta = effects.get("approval_delta", 0)
        if approval_delta != 0:
            global_shift = approval_delta * 0.003  # 10% approval = +0.03 lean
            for c in self.constituencies:
                c.lean_score = max(-1.0, min(1.0, c.lean_score + global_shift))

        # State-specific effects
        state_effects = effects.get("state_effects", {})
        if state_effects:
            self.apply_state_effects(state_effects)

    def run_simulation(self, seed: Optional[int] = None) -> SimulationResult:
        """
        Run Monte Carlo simulation across all constituencies.

        For each iteration, sample each constituency's outcome from a
        normal distribution centered on its lean_score with volatility
        as the standard deviation.
        """
        rng = random.Random(seed)
        seat_counts: list[int] = []
        state_tallies: dict[str, list[int]] = {}

        for _ in range(self.iterations):
            player_seats = 0
            opp_seats = 0
            others_seats = 0
            state_player: dict[str, int] = {}

            for c in self.constituencies:
                # Sample outcome: lean_score + noise
                outcome = rng.gauss(c.lean_score, c.volatility)

                if c.state_ut not in state_player:
                    state_player[c.state_ut] = 0

                if outcome > 0:
                    player_seats += 1
                    state_player[c.state_ut] += 1
                elif outcome < -0.6:
                    # Strong opposition lean — opponent wins
                    opp_seats += 1
                else:
                    # Mild opposition lean — could be opponent or third party
                    if rng.random() < 0.7:
                        opp_seats += 1
                    else:
                        others_seats += 1

            seat_counts.append(player_seats)
            for state, count in state_player.items():
                if state not in state_tallies:
                    state_tallies[state] = []
                state_tallies[state].append(count)

        # Aggregate results
        avg_seats = int(sum(seat_counts) / len(seat_counts))
        win_count = sum(1 for s in seat_counts if s >= self.majority)
        win_prob = win_count / self.iterations

        seat_counts_sorted = sorted(seat_counts)
        p5 = seat_counts_sorted[int(0.05 * self.iterations)]
        p95 = seat_counts_sorted[int(0.95 * self.iterations)]

        # State breakdown (averages)
        state_breakdown: dict[str, dict[str, int]] = {}
        for state, tallies in state_tallies.items():
            avg_state = int(sum(tallies) / len(tallies))
            total_in_state = sum(
                1 for c in self.constituencies if c.state_ut == state
            )
            state_breakdown[state] = {
                "player": avg_state,
                "opponent": total_in_state - avg_state,
                "total": total_in_state,
            }

        # Count swing seats won
        swing_won = sum(
            1 for c in self.constituencies
            if c.seat_class == "swing" and c.lean_score > 0
        )
        super_swing_won = sum(
            1 for c in self.constituencies
            if c.seat_class == "super_swing" and c.lean_score > 0
        )

        opp_avg = self.total_seats - avg_seats - int(
            sum(1 for c in self.constituencies if c.lean_score < -0.6) * 0.3
            / self.iterations * self.iterations
        )
        # Simplified: opponent gets remainder
        opp_avg = max(0, self.total_seats - avg_seats)

        return SimulationResult(
            projected_seats_player=avg_seats,
            projected_seats_opponent=opp_avg,
            projected_seats_others=0,
            win_probability=round(win_prob, 4),
            state_breakdown=state_breakdown,
            confidence_interval=(p5, p95),
            swing_seats_won=swing_won,
            super_swing_seats_won=super_swing_won,
        )

    def get_top_swing_constituencies(self, n: int = 10) -> list[dict]:
        """Return the most contestable constituencies (lean closest to 0)."""
        sorted_by_contest = sorted(
            self.constituencies, key=lambda c: abs(c.lean_score)
        )
        return [c.to_dict() for c in sorted_by_contest[:n]]

    def get_state_summary(self) -> dict[str, dict]:
        """Get a summary of seat projections by state."""
        summary: dict[str, dict] = {}
        for c in self.constituencies:
            if c.state_ut not in summary:
                summary[c.state_ut] = {
                    "total": 0, "leaning_player": 0,
                    "leaning_opponent": 0, "toss_up": 0,
                }
            summary[c.state_ut]["total"] += 1
            if c.lean_score > 0.2:
                summary[c.state_ut]["leaning_player"] += 1
            elif c.lean_score < -0.2:
                summary[c.state_ut]["leaning_opponent"] += 1
            else:
                summary[c.state_ut]["toss_up"] += 1
        return summary

    def get_all_constituency_leans(self) -> dict[str, float]:
        """Return a dict of constituency_name -> lean_score for snapshotting."""
        return {c.name: round(c.lean_score, 4) for c in self.constituencies}
