"""Tests for constituency data endpoints."""
import pytest
from httpx import AsyncClient


class TestListConstituencies:
    async def test_list_all(self, client: AsyncClient, seeded_constituencies):
        response = await client.get("/api/v1/constituencies")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 10
        assert len(data["constituencies"]) == 10

    async def test_filter_by_state(self, client: AsyncClient, seeded_constituencies):
        response = await client.get("/api/v1/constituencies?state=Uttar Pradesh")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        for c in data["constituencies"]:
            assert c["state_ut"] == "Uttar Pradesh"

    async def test_filter_by_seat_class(self, client: AsyncClient, seeded_constituencies):
        response = await client.get("/api/v1/constituencies?seat_class=super_swing")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        for c in data["constituencies"]:
            assert c["seat_class"] == "super_swing"

    async def test_empty_state_filter(self, client: AsyncClient, seeded_constituencies):
        response = await client.get("/api/v1/constituencies?state=Nonexistent")
        assert response.status_code == 200
        assert response.json()["total"] == 0


class TestSwingConstituencies:
    async def test_swing_endpoint(self, client: AsyncClient, seeded_constituencies):
        response = await client.get("/api/v1/constituencies/swing")
        assert response.status_code == 200
        data = response.json()
        for c in data["constituencies"]:
            assert c["seat_class"] in ["swing", "super_swing"]

    async def test_swing_sorted_by_margin(self, client: AsyncClient, seeded_constituencies):
        response = await client.get("/api/v1/constituencies/swing")
        data = response.json()
        margins = [c["actual_margin_2024"] for c in data["constituencies"]]
        assert margins == sorted(margins)
