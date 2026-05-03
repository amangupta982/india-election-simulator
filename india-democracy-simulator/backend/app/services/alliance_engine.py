"""
Alliance Engine — NDA/INDIA bloc coalition math.

Models real political alliances from the 2024 Indian General Election,
with negotiation mechanics for in-game alliance decisions.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class AlliancePartner:
    """A political party that can be part of an alliance."""
    party_name: str
    seats_2024: int
    stronghold_states: list[str]
    base_lean_bonus: float  # lean boost when allied
    loyalty: float  # 0-1, how likely to stay in alliance
    demands: str  # what they want for alliance


# Real 2024 alliance data
NDA_CORE = [
    AlliancePartner(
        party_name="Bharatiya Janata Party",
        seats_2024=248,
        stronghold_states=["Uttar Pradesh", "Gujarat", "Madhya Pradesh", "Rajasthan", "Karnataka"],
        base_lean_bonus=0.0,  # player's own party
        loyalty=1.0,
        demands="Leading party",
    ),
    AlliancePartner(
        party_name="Janata Dal (United)",
        seats_2024=19,
        stronghold_states=["Bihar"],
        base_lean_bonus=0.18,
        loyalty=0.6,
        demands="3 cabinet berths + Bihar CM support",
    ),
    AlliancePartner(
        party_name="Telugu Desam",
        seats_2024=16,
        stronghold_states=["Andhra Pradesh"],
        base_lean_bonus=0.22,
        loyalty=0.5,
        demands="Special status for Andhra Pradesh",
    ),
    AlliancePartner(
        party_name="Shiv Sena",
        seats_2024=7,
        stronghold_states=["Maharashtra"],
        base_lean_bonus=0.12,
        loyalty=0.7,
        demands="Maharashtra deputy CM post",
    ),
    AlliancePartner(
        party_name="Lok Janshakti Party(Ram Vilas)",
        seats_2024=5,
        stronghold_states=["Bihar"],
        base_lean_bonus=0.08,
        loyalty=0.65,
        demands="2 cabinet berths",
    ),
    AlliancePartner(
        party_name="Janata Dal (Secular)",
        seats_2024=2,
        stronghold_states=["Karnataka"],
        base_lean_bonus=0.06,
        loyalty=0.4,
        demands="Karnataka state support",
    ),
]

INDIA_BLOC_CORE = [
    AlliancePartner(
        party_name="Indian National Congress",
        seats_2024=100,
        stronghold_states=["Rajasthan", "Karnataka", "Telangana", "Kerala"],
        base_lean_bonus=0.0,
        loyalty=1.0,
        demands="Leading party",
    ),
    AlliancePartner(
        party_name="Samajwadi Party",
        seats_2024=37,
        stronghold_states=["Uttar Pradesh"],
        base_lean_bonus=0.25,
        loyalty=0.7,
        demands="UP CM candidacy recognition",
    ),
    AlliancePartner(
        party_name="All India Trinamool Congress",
        seats_2024=29,
        stronghold_states=["West Bengal"],
        base_lean_bonus=0.30,
        loyalty=0.4,
        demands="No INC expansion in West Bengal",
    ),
    AlliancePartner(
        party_name="Dravida Munnetra Kazhagam",
        seats_2024=22,
        stronghold_states=["Tamil Nadu"],
        base_lean_bonus=0.28,
        loyalty=0.8,
        demands="Tamil Nadu autonomy support",
    ),
    AlliancePartner(
        party_name="Nationalist Congress Party  Sharadchandra Pawar",
        seats_2024=8,
        stronghold_states=["Maharashtra"],
        base_lean_bonus=0.10,
        loyalty=0.6,
        demands="Maharashtra seat sharing",
    ),
    AlliancePartner(
        party_name="Shiv Sena (Uddhav Balasaheb Thackrey)",
        seats_2024=9,
        stronghold_states=["Maharashtra"],
        base_lean_bonus=0.12,
        loyalty=0.55,
        demands="Hindutva identity respect",
    ),
]

# Independent / swing parties that either bloc can court
SWING_PARTIES = [
    AlliancePartner(
        party_name="Bharat Rashtriya Samithi",
        seats_2024=2,
        stronghold_states=["Telangana"],
        base_lean_bonus=0.08,
        loyalty=0.3,
        demands="Telangana development funds",
    ),
    AlliancePartner(
        party_name="YSR Congress Party",
        seats_2024=4,
        stronghold_states=["Andhra Pradesh"],
        base_lean_bonus=0.10,
        loyalty=0.35,
        demands="Andhra special package",
    ),
    AlliancePartner(
        party_name="Biju Janata Dal",
        seats_2024=1,
        stronghold_states=["Odisha"],
        base_lean_bonus=0.05,
        loyalty=0.3,
        demands="Odisha state autonomy",
    ),
]


class AllianceEngine:
    """
    Manages political alliances and coalition math.

    In Indian elections, no single party usually wins 272 seats alone.
    Alliance management is the single highest-leverage game mechanic.
    """

    def __init__(self, player_party: str):
        self.player_party = player_party
        self.active_allies: list[AlliancePartner] = []
        self.rejected_partners: list[str] = []
        self.alliance_events_history: list[dict] = []

        # Determine which bloc the player is in
        self._setup_default_alliance()

    def _setup_default_alliance(self) -> None:
        """Set up the default alliance based on the player's party."""
        nda_parties = {p.party_name for p in NDA_CORE}
        india_parties = {p.party_name for p in INDIA_BLOC_CORE}

        if self.player_party in nda_parties:
            # Player is in NDA — start with core NDA allies
            self.bloc = "NDA"
            self.active_allies = [
                p for p in NDA_CORE if p.party_name != self.player_party
            ]
        elif self.player_party in india_parties:
            self.bloc = "INDIA"
            self.active_allies = [
                p for p in INDIA_BLOC_CORE if p.party_name != self.player_party
            ]
        else:
            # Independent party — no default allies
            self.bloc = "Independent"
            self.active_allies = []

    def get_total_allied_seats(self) -> int:
        """Get total seats from current alliance partners (2024 baseline)."""
        return sum(p.seats_2024 for p in self.active_allies)

    def get_alliance_states(self) -> list[str]:
        """Get all states where alliance partners have strongholds."""
        states = set()
        for p in self.active_allies:
            states.update(p.stronghold_states)
        return list(states)

    def get_alliance_lean_bonus(self) -> dict[str, float]:
        """Get lean bonuses by state from all active allies."""
        state_bonuses: dict[str, float] = {}
        for partner in self.active_allies:
            for state in partner.stronghold_states:
                current = state_bonuses.get(state, 0.0)
                state_bonuses[state] = min(current + partner.base_lean_bonus, 0.5)
        return state_bonuses

    def negotiate_alliance(
        self, party_name: str, concession_level: float = 0.5
    ) -> dict:
        """
        Attempt to bring a new party into the alliance.

        concession_level: 0.0 (no concessions) to 1.0 (full concessions)
        Returns success status and effects.
        """
        # Find the party
        target = None
        for p in SWING_PARTIES + NDA_CORE + INDIA_BLOC_CORE:
            if p.party_name == party_name:
                target = p
                break

        if target is None:
            return {"success": False, "reason": "Party not found"}

        if any(a.party_name == party_name for a in self.active_allies):
            return {"success": False, "reason": "Already allied"}

        if party_name in self.rejected_partners:
            return {"success": False, "reason": "Previously rejected — trust broken"}

        # Success probability based on loyalty + concession
        import random
        success_prob = target.loyalty * concession_level
        success = random.random() < success_prob

        result = {
            "success": success,
            "party": party_name,
            "seats": target.seats_2024,
            "stronghold_states": target.stronghold_states,
            "demands": target.demands,
            "concession_level": concession_level,
        }

        if success:
            self.active_allies.append(target)
            result["lean_bonus"] = target.base_lean_bonus
            result["reason"] = f"{party_name} joins the alliance!"
        else:
            self.rejected_partners.append(party_name)
            result["reason"] = f"{party_name} rejects the offer. Trust damaged."

        self.alliance_events_history.append(result)
        return result

    def lose_ally(self, party_name: str) -> dict:
        """An ally leaves the coalition (triggered by opponent poaching or crisis)."""
        partner = None
        for i, p in enumerate(self.active_allies):
            if p.party_name == party_name:
                partner = self.active_allies.pop(i)
                break

        if partner is None:
            return {"success": False, "reason": "Not an active ally"}

        return {
            "success": True,
            "party": party_name,
            "seats_lost": partner.seats_2024,
            "states_affected": partner.stronghold_states,
            "lean_loss": partner.base_lean_bonus,
        }

    def get_status(self) -> dict:
        """Get current alliance status for API response."""
        return {
            "bloc": self.bloc,
            "total_allied_seats": self.get_total_allied_seats(),
            "allies": [
                {
                    "party": p.party_name,
                    "seats": p.seats_2024,
                    "strongholds": p.stronghold_states,
                    "loyalty": p.loyalty,
                }
                for p in self.active_allies
            ],
            "available_partners": [
                {
                    "party": p.party_name,
                    "seats": p.seats_2024,
                    "strongholds": p.stronghold_states,
                    "demands": p.demands,
                }
                for p in SWING_PARTIES
                if p.party_name not in self.rejected_partners
                and not any(a.party_name == p.party_name for a in self.active_allies)
            ],
        }
