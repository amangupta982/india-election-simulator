"""Security and input validation tests."""
import pytest


class TestAuthSecurity:
    """Verify authentication is enforced on protected routes."""

    @pytest.mark.asyncio
    async def test_start_game_requires_auth(self, client):
        """POST /game/start without token returns 401 or 403."""
        response = await client.post("/api/v1/game/start", json={
            "player_party": "Bharatiya Janata Party",
            "role": "campaign_manager",
        })
        assert response.status_code in [401, 403]

    @pytest.mark.asyncio
    async def test_decision_requires_auth(self, client):
        """POST /game/{id}/decision without token returns 401 or 403."""
        response = await client.post("/api/v1/game/fake-id/decision", json={
            "event_id": "fake-event", "choice_index": 0,
        })
        assert response.status_code in [401, 403]

    @pytest.mark.asyncio
    async def test_invalid_token_rejected(self, client):
        """Requests with invalid JWT are rejected."""
        headers = {"Authorization": "Bearer invalid.token.here"}
        response = await client.post("/api/v1/game/start", json={
            "player_party": "Bharatiya Janata Party",
            "role": "campaign_manager",
        }, headers=headers)
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_expired_token_format(self, client):
        """Malformed Bearer tokens are rejected."""
        headers = {"Authorization": "NotBearer sometoken"}
        response = await client.post("/api/v1/game/start", json={
            "player_party": "Bharatiya Janata Party",
            "role": "campaign_manager",
        }, headers=headers)
        assert response.status_code in [401, 403]

    @pytest.mark.asyncio
    async def test_leaderboard_is_public(self, client):
        """GET /leaderboard does NOT require auth."""
        response = await client.get("/api/v1/leaderboard")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_health_is_public(self, client):
        """GET /health does NOT require auth."""
        response = await client.get("/health")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_constituencies_list_is_public(self, client, seeded_constituencies):
        """GET /constituencies does NOT require auth."""
        response = await client.get("/api/v1/constituencies")
        assert response.status_code == 200


class TestInputValidation:
    """Verify Pydantic schema validation on inputs."""

    @pytest.mark.asyncio
    async def test_start_game_empty_body(self, client, auth_headers):
        """POST /game/start with empty body returns 422."""
        response = await client.post("/api/v1/game/start", json={}, headers=auth_headers)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_start_game_missing_party(self, client, auth_headers):
        """POST /game/start without player_party returns 422."""
        response = await client.post("/api/v1/game/start", json={
            "role": "campaign_manager",
        }, headers=auth_headers)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_decision_missing_event_id(self, client, auth_headers):
        """POST /game/{id}/decision without event_id returns 422."""
        response = await client.post("/api/v1/game/some-id/decision", json={
            "choice_index": 0,
        }, headers=auth_headers)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_decision_negative_choice_index(self, client, auth_headers):
        """Negative choice index is rejected."""
        response = await client.post("/api/v1/game/some-id/decision", json={
            "event_id": "some-event", "choice_index": -1,
        }, headers=auth_headers)
        assert response.status_code in [400, 422]

    @pytest.mark.asyncio
    async def test_register_missing_email(self, client):
        """POST /auth/register without email returns 422."""
        response = await client.post("/api/v1/auth/register", json={
            "password": "testpassword123",
        })
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_register_short_password(self, client):
        """POST /auth/register with short password returns 422."""
        response = await client.post("/api/v1/auth/register", json={
            "email": "test@test.com", "password": "ab",
        })
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_login_missing_fields(self, client):
        """POST /auth/login with missing fields returns 422."""
        response = await client.post("/api/v1/auth/login", json={})
        assert response.status_code == 422


class TestConfigSettings:
    """Tests for application configuration."""

    def test_settings_have_defaults(self):
        """Settings have sensible defaults."""
        from app.config import get_settings
        s = get_settings()
        assert s.starting_budget_crore > 0
        assert 0 < s.starting_approval <= 100
        assert s.majority_threshold == 272
        assert s.campaign_weeks == 8

    def test_jwt_secret_is_set(self):
        """JWT secret key is configured."""
        from app.config import get_settings
        s = get_settings()
        assert len(s.jwt_secret_key) > 0

    def test_debug_mode_in_tests(self):
        """Debug mode is enabled during tests."""
        from app.config import get_settings
        s = get_settings()
        assert s.debug is True
