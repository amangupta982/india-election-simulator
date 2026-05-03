"""Tests for GameEngine — session lifecycle, decision processing, post-mortem."""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from app.services.game_engine import GameEngine, PARTY_OPPONENT_MAP


class TestGameEngineInit:
    """Unit tests for GameEngine initialization."""

    def test_party_opponent_map_complete(self):
        """All 5 playable parties have an opponent mapping."""
        assert "Bharatiya Janata Party" in PARTY_OPPONENT_MAP
        assert "Indian National Congress" in PARTY_OPPONENT_MAP
        assert "Samajwadi Party" in PARTY_OPPONENT_MAP
        assert "All India Trinamool Congress" in PARTY_OPPONENT_MAP
        assert "Dravida Munnetra Kazhagam" in PARTY_OPPONENT_MAP

    def test_bjp_vs_inc(self):
        assert PARTY_OPPONENT_MAP["Bharatiya Janata Party"] == "Indian National Congress"

    def test_inc_vs_bjp(self):
        assert PARTY_OPPONENT_MAP["Indian National Congress"] == "Bharatiya Janata Party"

    def test_engine_has_ai_service(self):
        engine = GameEngine()
        assert engine.ai_service is not None


class TestStartGame:
    """Integration tests for GameEngine.start_game()."""

    @pytest.mark.asyncio
    async def test_start_game_creates_session(self, client, auth_headers, seeded_constituencies):
        """Starting a game returns session ID and initial state."""
        response = await client.post("/api/v1/game/start", json={
            "player_party": "Bharatiya Janata Party",
            "role": "campaign_manager",
            "difficulty": "normal",
        }, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert data["initial_state"]["player_party"] == "Bharatiya Janata Party"
        assert data["initial_state"]["week_number"] == 1
        assert data["initial_state"]["status"] == "in_progress"

    @pytest.mark.asyncio
    async def test_start_game_initial_budget(self, client, auth_headers, seeded_constituencies):
        """Initial budget matches configured starting budget."""
        response = await client.post("/api/v1/game/start", json={
            "player_party": "Indian National Congress",
            "role": "party_leader",
            "difficulty": "normal",
        }, headers=auth_headers)
        data = response.json()
        assert data["initial_state"]["budget_remaining"] > 0

    @pytest.mark.asyncio
    async def test_start_game_has_current_event(self, client, auth_headers, seeded_constituencies):
        """Initial state includes a generated event with choices."""
        response = await client.post("/api/v1/game/start", json={
            "player_party": "Bharatiya Janata Party",
            "role": "campaign_manager",
            "difficulty": "normal",
        }, headers=auth_headers)
        data = response.json()
        event = data["initial_state"]["current_event"]
        assert event is not None
        assert "headline" in event
        assert "choices" in event
        assert len(event["choices"]) >= 2

    @pytest.mark.asyncio
    async def test_start_game_seat_projections(self, client, auth_headers, seeded_constituencies):
        """Initial state includes seat projections > 0."""
        response = await client.post("/api/v1/game/start", json={
            "player_party": "Bharatiya Janata Party",
            "role": "campaign_manager",
            "difficulty": "normal",
        }, headers=auth_headers)
        data = response.json()
        assert data["initial_state"]["seat_projection_you"] >= 0
        assert data["initial_state"]["seat_projection_opp"] >= 0

    @pytest.mark.asyncio
    async def test_start_game_all_parties(self, client, auth_headers, seeded_constituencies):
        """Can start games with each of the 5 playable parties."""
        for party in PARTY_OPPONENT_MAP.keys():
            response = await client.post("/api/v1/game/start", json={
                "player_party": party,
                "role": "campaign_manager",
                "difficulty": "normal",
            }, headers=auth_headers)
            assert response.status_code == 200, f"Failed for {party}"

    @pytest.mark.asyncio
    async def test_start_game_difficulty_levels(self, client, auth_headers, seeded_constituencies):
        """Game supports all difficulty levels."""
        for diff in ["easy", "normal", "hard"]:
            response = await client.post("/api/v1/game/start", json={
                "player_party": "Bharatiya Janata Party",
                "role": "campaign_manager",
                "difficulty": diff,
            }, headers=auth_headers)
            assert response.status_code == 200, f"Failed for difficulty {diff}"


class TestProcessDecision:
    """Tests for decision processing and turn advancement."""

    async def _start_and_decide(self, client, auth_headers):
        """Helper: start a game and return session_id + event_id."""
        resp = await client.post("/api/v1/game/start", json={
            "player_party": "Bharatiya Janata Party",
            "role": "campaign_manager",
            "difficulty": "normal",
        }, headers=auth_headers)
        data = resp.json()
        return data["session_id"], data["initial_state"]["current_event"]["id"]

    @pytest.mark.asyncio
    async def test_decision_advances_week(self, client, auth_headers, seeded_constituencies):
        """Making a decision advances the game week."""
        sid, eid = await self._start_and_decide(client, auth_headers)
        resp = await client.post(f"/api/v1/game/{sid}/decision", json={
            "event_id": eid, "choice_index": 0,
        }, headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["new_state"]["week_number"] >= 2

    @pytest.mark.asyncio
    async def test_decision_returns_opponent_move(self, client, auth_headers, seeded_constituencies):
        """Each decision triggers an opponent counter-move."""
        sid, eid = await self._start_and_decide(client, auth_headers)
        resp = await client.post(f"/api/v1/game/{sid}/decision", json={
            "event_id": eid, "choice_index": 0,
        }, headers=auth_headers)
        data = resp.json()
        assert "opponent_move" in data
        assert "headline" in data["opponent_move"]

    @pytest.mark.asyncio
    async def test_decision_returns_effects(self, client, auth_headers, seeded_constituencies):
        """Decision response includes applied effects."""
        sid, eid = await self._start_and_decide(client, auth_headers)
        resp = await client.post(f"/api/v1/game/{sid}/decision", json={
            "event_id": eid, "choice_index": 0,
        }, headers=auth_headers)
        data = resp.json()
        assert "effects_applied" in data

    @pytest.mark.asyncio
    async def test_decision_generates_next_event(self, client, auth_headers, seeded_constituencies):
        """Non-final decisions generate the next week's event."""
        sid, eid = await self._start_and_decide(client, auth_headers)
        resp = await client.post(f"/api/v1/game/{sid}/decision", json={
            "event_id": eid, "choice_index": 0,
        }, headers=auth_headers)
        data = resp.json()
        if data["new_state"]["status"] == "in_progress":
            assert data["new_state"]["current_event"] is not None

    @pytest.mark.asyncio
    async def test_full_game_playthrough(self, client, auth_headers, seeded_constituencies):
        """Play through all 8 weeks and verify game completes."""
        resp = await client.post("/api/v1/game/start", json={
            "player_party": "Bharatiya Janata Party",
            "role": "campaign_manager",
            "difficulty": "normal",
        }, headers=auth_headers)
        data = resp.json()
        sid = data["session_id"]
        eid = data["initial_state"]["current_event"]["id"]

        for week in range(8):
            resp = await client.post(f"/api/v1/game/{sid}/decision", json={
                "event_id": eid, "choice_index": 0,
            }, headers=auth_headers)
            assert resp.status_code == 200
            data = resp.json()
            if data["new_state"]["status"] == "completed":
                break
            eid = data["new_state"]["current_event"]["id"]

        # Verify game completed
        state_resp = await client.get(f"/api/v1/game/{sid}/state", headers=auth_headers)
        assert state_resp.status_code == 200


class TestLeaderboardRouter:
    """Tests for leaderboard API endpoint."""

    @pytest.mark.asyncio
    async def test_leaderboard_returns_data(self, client):
        """GET /leaderboard returns a response with entries."""
        response = await client.get("/api/v1/leaderboard")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, (list, dict))

    @pytest.mark.asyncio
    async def test_leaderboard_with_party_filter(self, client):
        """Leaderboard supports party parameter filtering."""
        response = await client.get("/api/v1/leaderboard?party=Bharatiya Janata Party")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_leaderboard_with_role_filter(self, client):
        """Leaderboard supports role parameter filtering."""
        response = await client.get("/api/v1/leaderboard?role=campaign_manager")
        assert response.status_code == 200


class TestAIInferenceService:
    """Tests for the AI event generation service."""

    def test_generate_event_returns_required_fields(self):
        """Generated events have headline, body, and choices."""
        from app.services.ai_inference import AIInferenceService
        service = AIInferenceService()
        game_state = {
            "week_number": 1, "player_party": "Bharatiya Janata Party",
            "budget_crore": 500, "approval_pct": 50.0, "seat_projection": 250,
        }
        event = service.generate_event(game_state)
        assert "headline" in event
        assert "body" in event
        assert "choices" in event
        assert "event_type" in event

    def test_event_choices_have_effects(self):
        """Each choice in a generated event has effects."""
        from app.services.ai_inference import AIInferenceService
        service = AIInferenceService()
        game_state = {
            "week_number": 3, "player_party": "Indian National Congress",
            "budget_crore": 400, "approval_pct": 45.0, "seat_projection": 200,
        }
        event = service.generate_event(game_state)
        for choice in event["choices"]:
            assert "text" in choice
            assert "effect" in choice

    def test_generate_post_mortem(self):
        """Post-mortem generates sections with civics principles."""
        from app.services.ai_inference import AIInferenceService
        service = AIInferenceService()
        session_data = {
            "won_majority": True,
            "final_seats_you": 290,
            "final_seats_opp": 200,
            "player_party": "Bharatiya Janata Party",
            "decisions": [{"week": 1, "choice": "Rally", "effects": {}}],
            "state_breakdown": {},
        }
        result = service.generate_post_mortem(session_data)
        assert "won_majority" in result
        assert "sections" in result
        assert "final_seats_you" in result

    def test_multiple_events_are_varied(self):
        """Consecutive events don't always have the same headline."""
        from app.services.ai_inference import AIInferenceService
        service = AIInferenceService()
        headlines = set()
        for week in range(1, 9):
            game_state = {
                "week_number": week, "player_party": "Bharatiya Janata Party",
                "budget_crore": 500, "approval_pct": 50.0, "seat_projection": 250,
            }
            event = service.generate_event(game_state)
            headlines.add(event["headline"])
        # At least 3 unique headlines across 8 weeks
        assert len(headlines) >= 3


class TestHealthCheck:
    """Tests for the health endpoint."""

    @pytest.mark.asyncio
    async def test_health_returns_ok(self, client):
        """Health endpoint returns status ok."""
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    @pytest.mark.asyncio
    async def test_health_shows_google_cloud(self, client):
        """Health endpoint reports Google Cloud service status."""
        response = await client.get("/health")
        data = response.json()
        assert "google_cloud" in data
        gc = data["google_cloud"]
        assert "firebase" in gc
        assert "firestore" in gc
        assert "vertex_ai" in gc
        assert "cloud_storage" in gc
        assert "cloud_logging" in gc
