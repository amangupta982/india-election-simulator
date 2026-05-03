"""Tests for authentication endpoints."""
import pytest
from httpx import AsyncClient


class TestRegistration:
    """Tests for POST /api/v1/auth/register."""

    async def test_register_success(self, client: AsyncClient):
        """Valid registration returns access token and user data."""
        response = await client.post("/api/v1/auth/register", json={
            "email": "newuser@example.com",
            "display_name": "New User",
            "password": "securepassword123",
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == "newuser@example.com"
        assert data["user"]["display_name"] == "New User"

    async def test_register_duplicate_email(self, client: AsyncClient, test_user):
        """Registering with an existing email returns 400."""
        response = await client.post("/api/v1/auth/register", json={
            "email": "test@example.com",  # same as test_user
            "display_name": "Duplicate User",
            "password": "anotherpassword",
        })
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()

    async def test_register_short_password(self, client: AsyncClient):
        """Password shorter than 6 chars is rejected by Pydantic validation."""
        response = await client.post("/api/v1/auth/register", json={
            "email": "short@example.com",
            "display_name": "Short Pass",
            "password": "12345",
        })
        assert response.status_code == 422  # Pydantic validation error

    async def test_register_missing_fields(self, client: AsyncClient):
        """Missing required fields returns 422."""
        response = await client.post("/api/v1/auth/register", json={
            "email": "missing@example.com",
        })
        assert response.status_code == 422

    async def test_register_invalid_email_format(self, client: AsyncClient):
        """Email shorter than 5 chars is rejected."""
        response = await client.post("/api/v1/auth/register", json={
            "email": "ab",
            "display_name": "Bad Email",
            "password": "password123",
        })
        assert response.status_code == 422


class TestLogin:
    """Tests for POST /api/v1/auth/login."""

    async def test_login_success(self, client: AsyncClient, test_user):
        """Valid credentials return access token."""
        response = await client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "testpassword123",
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["user"]["email"] == "test@example.com"

    async def test_login_wrong_password(self, client: AsyncClient, test_user):
        """Wrong password returns 401."""
        response = await client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "wrongpassword",
        })
        assert response.status_code == 401
        assert "invalid" in response.json()["detail"].lower()

    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Nonexistent email returns 401."""
        response = await client.post("/api/v1/auth/login", json={
            "email": "noone@example.com",
            "password": "password123",
        })
        assert response.status_code == 401


class TestProtectedRoutes:
    """Tests for JWT-protected endpoints."""

    async def test_no_token_returns_403(self, client: AsyncClient):
        """Accessing a protected route without a token returns 403."""
        response = await client.post("/api/v1/game/start", json={
            "player_party": "Bharatiya Janata Party",
            "role": "party_leader",
            "difficulty": "normal",
        })
        assert response.status_code == 403

    async def test_invalid_token_returns_401(self, client: AsyncClient):
        """Accessing a protected route with an invalid token returns 401."""
        response = await client.post(
            "/api/v1/game/start",
            json={
                "player_party": "Bharatiya Janata Party",
                "role": "party_leader",
                "difficulty": "normal",
            },
            headers={"Authorization": "Bearer invalid-token-here"},
        )
        assert response.status_code == 401

    async def test_valid_token_accepted(self, client: AsyncClient, auth_headers, seeded_constituencies):
        """A valid token grants access to protected endpoints."""
        response = await client.post(
            "/api/v1/game/start",
            json={
                "player_party": "Bharatiya Janata Party",
                "role": "party_leader",
                "difficulty": "normal",
            },
            headers=auth_headers,
        )
        assert response.status_code == 200
