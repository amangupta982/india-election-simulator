"""Vertex AI service — AI-powered event generation and campaign advice.

Uses Google's Gemini model via Vertex AI to:
1. Generate dynamic, context-aware campaign events (replaces static pool)
2. Provide AI strategic campaign advice to the player
3. Generate personalized post-mortem election analysis

Falls back to static pool when Vertex AI is unavailable (local dev).
"""
from __future__ import annotations

import json
import logging
from typing import Optional

from app.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()

_model = None


def _get_model():
    """Lazy-initialize the Vertex AI Gemini model."""
    global _model
    if _model is not None:
        return _model
    try:
        import vertexai
        from vertexai.generative_models import GenerativeModel

        vertexai.init(
            project=settings.gcp_project_id,
            location=settings.vertex_ai_location,
        )
        _model = GenerativeModel(settings.vertex_ai_model)
        logger.info(f"Vertex AI model initialized: {settings.vertex_ai_model}")
        return _model
    except Exception as e:
        logger.warning(f"Vertex AI not available: {e}")
        return None


class VertexAIService:
    """Vertex AI Gemini integration for intelligent game features."""

    @property
    def available(self) -> bool:
        return _get_model() is not None

    async def generate_dynamic_event(self, game_state: dict) -> Optional[dict]:
        """Generate a campaign event using Vertex AI Gemini.

        Creates unique, context-aware events based on the current game state,
        making each playthrough different. Falls back to None if unavailable.
        """
        model = _get_model()
        if model is None:
            return None

        try:
            prompt = f"""You are an Indian election game engine. Generate a realistic campaign event 
for an Indian Lok Sabha election simulation game.

Current game state:
- Week: {game_state.get('week_number', 1)} of 8
- Player party: {game_state.get('player_party', 'BJP')}
- Budget remaining: ₹{game_state.get('budget_crore', 500)} crore
- Approval rating: {game_state.get('approval_pct', 45)}%
- Current seat projection: {game_state.get('seat_projection', 200)}

Generate a JSON event with this exact structure:
{{
    "event_type": "rally|alliance|crisis|media|scam|booth|caste_coalition|regional_defense",
    "headline": "Short compelling headline",
    "body": "2-3 sentence description with real Indian election context",
    "choices": [
        {{
            "text": "Choice description",
            "effect": {{
                "seat_delta": 0,
                "budget_delta_crore": 0,
                "approval_delta": 0,
                "state_effects": {{"State Name": 0.05}}
            }}
        }}
    ],
    "affected_states": ["State Name"],
    "civics_lesson": "One sentence about a real Indian electoral principle"
}}

Provide exactly 4 choices with balanced trade-offs. Use real Indian states, parties, and electoral facts.
Return ONLY valid JSON, no markdown."""

            response = model.generate_content(prompt)
            text = response.text.strip()
            # Clean markdown code fences if present
            if text.startswith("```"):
                text = text.split("\n", 1)[1]
                text = text.rsplit("```", 1)[0]
            event = json.loads(text)
            event["generated_by"] = "vertex_ai"
            logger.info(f"Vertex AI generated event: {event.get('headline', 'unknown')}")
            return event
        except Exception as e:
            logger.error(f"Vertex AI event generation failed: {e}")
            return None

    async def generate_campaign_advice(self, game_state: dict) -> Optional[str]:
        """Generate AI strategic advice for the player.

        Analyzes the current game state and provides personalized campaign
        strategy recommendations, like having a real political strategist.
        """
        model = _get_model()
        if model is None:
            return None

        try:
            prompt = f"""You are a senior Indian political campaign strategist. 
Analyze this game state and give 2-3 sentences of strategic advice.

Game state:
- Party: {game_state.get('player_party', 'BJP')}
- Week {game_state.get('week_number', 1)} of 8
- Seat projection: {game_state.get('seat_projection_you', 200)}/543 (need 272 for majority)
- Opponent projection: {game_state.get('seat_projection_opp', 300)}
- Budget: ₹{game_state.get('budget_remaining', 500)} crore
- Approval: {game_state.get('approval_rating', 45)}%
- Win probability: {game_state.get('win_probability', 0.3) * 100:.0f}%

Give practical, specific advice about which states to focus on, 
whether to spend on rallies or save budget, and alliance strategy.
Keep it under 100 words. Be direct and strategic."""

            response = model.generate_content(prompt)
            advice = response.text.strip()
            logger.info("Vertex AI generated campaign advice")
            return advice
        except Exception as e:
            logger.error(f"Vertex AI advice generation failed: {e}")
            return None

    async def generate_ai_post_mortem(self, session_data: dict) -> Optional[str]:
        """Generate AI-powered post-game analysis.

        Creates a personalized narrative analysis of the election outcome,
        referencing specific decisions the player made.
        """
        model = _get_model()
        if model is None:
            return None

        try:
            won = session_data.get("won_majority", False)
            seats = session_data.get("final_seats_you", 0)
            party = session_data.get("player_party", "the party")
            decisions = session_data.get("decisions", [])
            decision_summary = "; ".join(
                [f"Week {d.get('week', '?')}: {d.get('choice', '?')}" for d in decisions[:5]]
            )

            prompt = f"""Analyze this Indian election simulation result in 3-4 sentences.

Result: {party} won {seats}/543 seats ({'majority achieved' if won else 'fell short of 272'}).
Key decisions: {decision_summary}

Reference real Indian electoral dynamics (FPTP, coalition math, swing seats).
Be specific about what worked and what didn't. Keep under 150 words."""

            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"Vertex AI post-mortem failed: {e}")
            return None


# Singleton instance
vertex_ai_service = VertexAIService()
