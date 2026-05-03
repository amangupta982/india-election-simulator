"""Tests for game lifecycle — start, decision, completion, post-mortem."""
import pytest
from httpx import AsyncClient


class TestGameStart:
    async def test_start_game_success(self, client: AsyncClient, auth_headers, seeded_constituencies):
        response = await client.post("/api/v1/game/start", json={
            "player_party": "Bharatiya Janata Party",
            "role": "party_leader", "difficulty": "normal",
        }, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert data["initial_state"]["player_party"] == "Bharatiya Janata Party"
        assert data["initial_state"]["week_number"] == 1
        assert data["initial_state"]["status"] == "in_progress"
        assert data["initial_state"]["budget_remaining"] == 500
        assert data["initial_state"]["current_event"] is not None

    async def test_start_game_all_parties(self, client: AsyncClient, auth_headers, seeded_constituencies):
        for party in ["Bharatiya Janata Party", "Indian National Congress",
                       "Samajwadi Party", "All India Trinamool Congress"]:
            response = await client.post("/api/v1/game/start", json={
                "player_party": party, "role": "campaign_manager", "difficulty": "easy",
            }, headers=auth_headers)
            assert response.status_code == 200

    async def test_start_game_all_roles(self, client: AsyncClient, auth_headers, seeded_constituencies):
        for role in ["party_leader", "campaign_manager", "swing_voter", "election_commission"]:
            response = await client.post("/api/v1/game/start", json={
                "player_party": "Bharatiya Janata Party", "role": role,
            }, headers=auth_headers)
            assert response.status_code == 200

    async def test_start_game_invalid_role(self, client: AsyncClient, auth_headers):
        response = await client.post("/api/v1/game/start", json={
            "player_party": "BJP", "role": "invalid_role",
        }, headers=auth_headers)
        assert response.status_code == 422


class TestGameDecision:
    async def _start_game(self, client, auth_headers):
        resp = await client.post("/api/v1/game/start", json={
            "player_party": "Bharatiya Janata Party",
            "role": "party_leader", "difficulty": "normal",
        }, headers=auth_headers)
        data = resp.json()
        return data["session_id"], data["initial_state"]["current_event"]["id"]

    async def test_decision_returns_new_state(self, client, auth_headers, seeded_constituencies):
        sid, eid = await self._start_game(client, auth_headers)
        response = await client.post(f"/api/v1/game/{sid}/decision", json={
            "event_id": eid, "choice_index": 0,
        }, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "new_state" in data
        assert "effects_applied" in data
        assert "opponent_move" in data

    async def test_decision_invalid_session(self, client, auth_headers):
        response = await client.post("/api/v1/game/nonexistent/decision", json={
            "event_id": "fake", "choice_index": 0,
        }, headers=auth_headers)
        assert response.status_code == 404

    async def test_decision_invalid_choice_index(self, client, auth_headers, seeded_constituencies):
        sid, eid = await self._start_game(client, auth_headers)
        response = await client.post(f"/api/v1/game/{sid}/decision", json={
            "event_id": eid, "choice_index": 99,
        }, headers=auth_headers)
        assert response.status_code in (400, 422)  # Pydantic or game engine validation


class TestGameState:
    async def test_get_state(self, client, auth_headers, seeded_constituencies):
        resp = await client.post("/api/v1/game/start", json={
            "player_party": "Bharatiya Janata Party",
            "role": "party_leader",
        }, headers=auth_headers)
        sid = resp.json()["session_id"]
        response = await client.get(f"/api/v1/game/{sid}/state", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == sid
        assert "budget_remaining" in data

    async def test_get_state_invalid_session(self, client, auth_headers):
        response = await client.get("/api/v1/game/nonexistent/state", headers=auth_headers)
        assert response.status_code == 404
