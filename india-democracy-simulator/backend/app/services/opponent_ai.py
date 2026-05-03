"""
Opponent AI System — rule-based opponent strategist.

The opponent analyzes the player's last move and generates a
counter-strategy. In Phase 1, this is rule-based. In Phase 2,
it will be replaced by AI model calls.
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field

from app.models import OpponentMoveType


@dataclass
class OpponentState:
    """Runtime state of the AI opponent."""
    party: str
    budget_crore: float = 400.0
    approval_rating: float = 48.0
    target_states: list[str] = field(default_factory=list)
    moves_history: list[dict] = field(default_factory=list)


# Pre-built opponent moves for each counter-strategy type
OPPONENT_MOVE_TEMPLATES = {
    OpponentMoveType.COUNTER_RALLY: [
        {
            "headline": "Opposition stages massive counter-rally in {state}",
            "budget_cost": 15,
            "effects": {"approval_delta": -2, "state_lean_delta": -0.08},
        },
        {
            "headline": "PM holds mega roadshow across {state} constituencies",
            "budget_cost": 25,
            "effects": {"approval_delta": -3, "state_lean_delta": -0.12},
        },
        {
            "headline": "Opposition leader draws record crowd in {state} heartland",
            "budget_cost": 20,
            "effects": {"approval_delta": -2, "state_lean_delta": -0.10},
        },
    ],
    OpponentMoveType.ATTACK_AD: [
        {
            "headline": "Hard-hitting attack ad campaign targets your {state} record",
            "budget_cost": 30,
            "effects": {"approval_delta": -5, "state_lean_delta": -0.06},
        },
        {
            "headline": "Social media blitz exposes contradictions in your manifesto",
            "budget_cost": 20,
            "effects": {"approval_delta": -4, "state_lean_delta": -0.04},
        },
        {
            "headline": "TV channels run 24-hour opposition exposé on your governance",
            "budget_cost": 35,
            "effects": {"approval_delta": -6, "state_lean_delta": -0.08},
        },
    ],
    OpponentMoveType.POACH_ALLIANCE: [
        {
            "headline": "Opposition courts your ally {party} with ministerial promises",
            "budget_cost": 10,
            "effects": {"approval_delta": -1, "alliance_threat": True},
        },
        {
            "headline": "{party} leaders spotted at opposition leader's residence",
            "budget_cost": 5,
            "effects": {"approval_delta": -2, "alliance_threat": True},
        },
    ],
    OpponentMoveType.OPPO_RESEARCH: [
        {
            "headline": "Opposition releases damaging dossier on your candidates in {state}",
            "budget_cost": 15,
            "effects": {"approval_delta": -4, "state_lean_delta": -0.07},
        },
        {
            "headline": "RTI reveals irregularities in your party's {state} ticket distribution",
            "budget_cost": 10,
            "effects": {"approval_delta": -3, "state_lean_delta": -0.05},
        },
    ],
    OpponentMoveType.PM_EVENT: [
        {
            "headline": "Opposition leader announces major welfare scheme for {state}",
            "budget_cost": 40,
            "effects": {"approval_delta": -3, "state_lean_delta": -0.15},
        },
        {
            "headline": "National security event dominates news cycle, boosting opposition",
            "budget_cost": 5,
            "effects": {"approval_delta": -4, "state_lean_delta": -0.05},
        },
    ],
    OpponentMoveType.BOOTH_AGENT_DEPLOY: [
        {
            "headline": "Opposition deploys 50,000 booth agents across {state}",
            "budget_cost": 25,
            "effects": {"approval_delta": -1, "state_lean_delta": -0.10},
        },
        {
            "headline": "Ground game surge: opposition activates grassroots network in {state}",
            "budget_cost": 20,
            "effects": {"approval_delta": -1, "state_lean_delta": -0.08},
        },
    ],
}

# Key battleground states the opponent targets
BATTLEGROUND_STATES = [
    "Uttar Pradesh", "Bihar", "Maharashtra", "West Bengal",
    "Rajasthan", "Madhya Pradesh", "Karnataka", "Tamil Nadu",
]


class OpponentAI:
    """
    Rule-based AI opponent that counter-strategies against the player.

    Analyzes the player's last move and picks an appropriate response
    targeting the most impactful states.
    """

    def __init__(self, opponent_party: str, player_party: str):
        self.state = OpponentState(party=opponent_party)
        self.player_party = player_party

        # Set opponent's default target states
        self.state.target_states = BATTLEGROUND_STATES.copy()

    def generate_counter_move(
        self,
        player_decision: dict,
        week_number: int,
        player_strong_states: list[str],
    ) -> dict:
        """
        Generate an opponent counter-move based on the player's last action.

        Strategy logic:
        - If player rallied → counter-rally in the same state
        - If player spent on ads → attack ads targeting their weak states
        - If player negotiated alliance → try to poach their weakest ally
        - Late game (weeks 6-8) → more aggressive PM-level events
        """
        # Determine counter-strategy
        player_event_type = player_decision.get("event_type", "rally")
        affected_states = player_decision.get("affected_states", [])

        if not affected_states:
            affected_states = random.sample(
                BATTLEGROUND_STATES, min(2, len(BATTLEGROUND_STATES))
            )

        # Choose counter-move type based on player's action
        move_type = self._choose_move_type(player_event_type, week_number)

        # Select template
        templates = OPPONENT_MOVE_TEMPLATES.get(move_type, [])
        if not templates:
            templates = OPPONENT_MOVE_TEMPLATES[OpponentMoveType.COUNTER_RALLY]

        template = random.choice(templates)

        # Pick target state — prioritize player's strong states
        target_state = random.choice(
            player_strong_states if player_strong_states else BATTLEGROUND_STATES
        )

        # Format headline
        headline = template["headline"].format(
            state=target_state,
            party=player_decision.get("alliance_partner", "key ally"),
        )

        # Budget check
        budget_cost = template["budget_cost"]
        if self.state.budget_crore < budget_cost:
            budget_cost = max(5, int(self.state.budget_crore * 0.1))

        self.state.budget_crore -= budget_cost

        # Build effects
        effects = {
            "target_states": [target_state],
            "approval_delta": template["effects"]["approval_delta"],
            "budget_spent": budget_cost,
        }

        if "state_lean_delta" in template["effects"]:
            effects["state_effects"] = {
                target_state: template["effects"]["state_lean_delta"]
            }

        if template["effects"].get("alliance_threat"):
            effects["alliance_threat"] = True

        move = {
            "move_type": move_type.value,
            "target_states": [target_state],
            "headline": headline,
            "effects": effects,
            "week_number": week_number,
        }

        self.state.moves_history.append(move)
        return move

    def _choose_move_type(
        self, player_event_type: str, week_number: int
    ) -> OpponentMoveType:
        """Choose counter-move type based on player's action and game phase."""
        # Late game = more aggressive
        if week_number >= 7:
            return random.choice([
                OpponentMoveType.PM_EVENT,
                OpponentMoveType.ATTACK_AD,
                OpponentMoveType.BOOTH_AGENT_DEPLOY,
            ])

        # Map player events to counter-strategies
        counter_map = {
            "rally": [OpponentMoveType.COUNTER_RALLY, OpponentMoveType.ATTACK_AD],
            "alliance": [OpponentMoveType.POACH_ALLIANCE, OpponentMoveType.OPPO_RESEARCH],
            "media": [OpponentMoveType.ATTACK_AD, OpponentMoveType.PM_EVENT],
            "crisis": [OpponentMoveType.PM_EVENT, OpponentMoveType.COUNTER_RALLY],
            "scam": [OpponentMoveType.OPPO_RESEARCH, OpponentMoveType.ATTACK_AD],
            "booth": [OpponentMoveType.BOOTH_AGENT_DEPLOY, OpponentMoveType.COUNTER_RALLY],
            "caste_coalition": [OpponentMoveType.COUNTER_RALLY, OpponentMoveType.POACH_ALLIANCE],
        }

        options = counter_map.get(
            player_event_type,
            [OpponentMoveType.COUNTER_RALLY, OpponentMoveType.ATTACK_AD],
        )
        return random.choice(options)

    def get_state(self) -> dict:
        """Get opponent's current state for API responses."""
        return {
            "party": self.state.party,
            "budget_crore": self.state.budget_crore,
            "approval_rating": self.state.approval_rating,
            "moves_count": len(self.state.moves_history),
        }
