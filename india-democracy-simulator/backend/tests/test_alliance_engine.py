"""Tests for the alliance engine — coalition math and negotiations."""
import pytest
from app.services.alliance_engine import AllianceEngine, NDA_CORE, INDIA_BLOC_CORE


class TestDefaultAlliance:
    def test_bjp_starts_in_nda(self):
        engine = AllianceEngine("Bharatiya Janata Party")
        assert engine.bloc == "NDA"

    def test_inc_starts_in_india_bloc(self):
        engine = AllianceEngine("Indian National Congress")
        assert engine.bloc == "INDIA"

    def test_nda_has_correct_allies(self):
        engine = AllianceEngine("Bharatiya Janata Party")
        ally_names = [a.party_name for a in engine.active_allies]
        assert "Janata Dal (United)" in ally_names
        assert "Bharatiya Janata Party" not in ally_names

    def test_india_bloc_has_correct_allies(self):
        engine = AllianceEngine("Indian National Congress")
        ally_names = [a.party_name for a in engine.active_allies]
        assert "Samajwadi Party" in ally_names

    def test_unknown_party_is_independent(self):
        engine = AllianceEngine("Random Party")
        assert engine.bloc == "Independent"
        assert len(engine.active_allies) == 0


class TestAllianceMath:
    def test_total_allied_seats_positive(self):
        engine = AllianceEngine("Bharatiya Janata Party")
        assert engine.get_total_allied_seats() > 0

    def test_alliance_states_include_strongholds(self):
        engine = AllianceEngine("Bharatiya Janata Party")
        states = engine.get_alliance_states()
        assert "Bihar" in states
        assert "Andhra Pradesh" in states

    def test_lean_bonus_capped(self):
        engine = AllianceEngine("Bharatiya Janata Party")
        for bonus in engine.get_alliance_lean_bonus().values():
            assert bonus <= 0.5


class TestNegotiation:
    def test_already_allied_rejected(self):
        engine = AllianceEngine("Bharatiya Janata Party")
        result = engine.negotiate_alliance("Janata Dal (United)")
        assert result["success"] is False

    def test_unknown_party_rejected(self):
        engine = AllianceEngine("Bharatiya Janata Party")
        result = engine.negotiate_alliance("Imaginary Party")
        assert result["success"] is False

    def test_rejected_party_blocked(self):
        engine = AllianceEngine("Bharatiya Janata Party")
        engine.rejected_partners.append("Bharat Rashtriya Samithi")
        result = engine.negotiate_alliance("Bharat Rashtriya Samithi")
        assert result["success"] is False


class TestLoseAlly:
    def test_lose_existing_ally(self):
        engine = AllianceEngine("Bharatiya Janata Party")
        initial = len(engine.active_allies)
        result = engine.lose_ally("Janata Dal (United)")
        assert result["success"] is True
        assert len(engine.active_allies) == initial - 1

    def test_lose_nonexistent_ally(self):
        engine = AllianceEngine("Bharatiya Janata Party")
        result = engine.lose_ally("Random Party")
        assert result["success"] is False


class TestStatus:
    def test_status_keys(self):
        engine = AllianceEngine("Bharatiya Janata Party")
        status = engine.get_status()
        assert "bloc" in status
        assert "allies" in status
        assert "available_partners" in status
