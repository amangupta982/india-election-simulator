"""Seed 563 constituencies from CSV into SQLite."""
import asyncio
import sys
import os
import uuid
import json

import pandas as pd
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

# Add parent to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.config import get_settings

settings = get_settings()
DATABASE_URL = settings.database_url

REGION_MAP = {
    "North": ["Uttar Pradesh", "Rajasthan", "Haryana", "Punjab", "Himachal Pradesh",
              "Uttarakhand", "Jammu & Kashmir", "Delhi", "Chandigarh"],
    "South": ["Tamil Nadu", "Kerala", "Karnataka", "Andhra Pradesh", "Telangana",
              "Puducherry", "Lakshadweep"],
    "East": ["West Bengal", "Odisha", "Jharkhand", "Bihar"],
    "West": ["Maharashtra", "Gujarat", "Goa",
             "Dadra & Nagar Haveli and Daman & Diu", "Dadra and Nagar Haveli and Daman and Diu"],
    "Northeast": ["Assam", "Manipur", "Meghalaya", "Mizoram", "Nagaland",
                   "Tripura", "Arunachal Pradesh", "Sikkim"],
    "Central": ["Madhya Pradesh", "Chhattisgarh"],
}


def get_region(state: str) -> str:
    for region, states in REGION_MAP.items():
        if state in states:
            return region
    return "UTs"


def classify_seat(margin: int) -> str:
    if margin < 5000:
        return "super_swing"
    if margin < 50000:
        return "swing"
    return "safe"


def lean_score(party: str, margin: int) -> dict:
    score = min(margin / 800000, 1.0)
    return {"party": party, "lean_score": round(score, 4)}


async def seed():
    csv_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw", "Indian_General_Elections_2024.csv")
    if not os.path.exists(csv_path):
        csv_path = os.path.join(os.path.dirname(__file__), "..", "..", "model", "data", "raw", "Indian_General_Elections_2024.csv")

    print(f"Loading CSV from: {os.path.abspath(csv_path)}")
    df = pd.read_csv(csv_path, encoding="latin-1")
    df["Margin"] = pd.to_numeric(df["Margin"], errors="coerce").fillna(0).astype(int)

    print(f"Found {len(df)} rows in CSV")

    # SQLite needs check_same_thread=False
    connect_args = {}
    if DATABASE_URL.startswith("sqlite"):
        connect_args = {"check_same_thread": False}

    engine = create_async_engine(DATABASE_URL, echo=False, connect_args=connect_args)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with engine.begin() as conn:
        # Create table if not exists
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS constituencies (
                id VARCHAR(36) PRIMARY KEY,
                state_ut VARCHAR(100) NOT NULL,
                name VARCHAR(200) NOT NULL,
                const_no INTEGER NOT NULL,
                seats INTEGER DEFAULT 1,
                actual_winner_2024 VARCHAR(200) NOT NULL,
                winning_party_2024 VARCHAR(200) NOT NULL,
                runner_up_2024 VARCHAR(200) NOT NULL,
                runner_up_party_2024 VARCHAR(200) NOT NULL,
                actual_margin_2024 INTEGER NOT NULL,
                seat_class VARCHAR(20) NOT NULL,
                default_lean JSON NOT NULL,
                region VARCHAR(20) NOT NULL
            )
        """))

    async with session_factory() as session:
        # Clear existing data
        await session.execute(text("DELETE FROM constituencies"))

        count = 0
        for _, row in df.iterrows():
            state = row["State/UT"].strip()
            margin = int(row["Margin"])
            winning_party = str(row["Leading Party"]).strip()

            def safe_str(val):
                if pd.isna(val):
                    return "N/A"
                return str(val).strip()

            lean_data = lean_score(winning_party, margin)
            await session.execute(text("""
                INSERT INTO constituencies (id, state_ut, name, const_no, seats,
                    actual_winner_2024, winning_party_2024, runner_up_2024,
                    runner_up_party_2024, actual_margin_2024, seat_class, default_lean, region)
                VALUES (:id, :state_ut, :name, :const_no, 1,
                    :winner, :w_party, :runner, :r_party, :margin, :seat_class, :lean, :region)
            """), {
                "id": str(uuid.uuid4()),
                "state_ut": state,
                "name": safe_str(row["Constituency"]),
                "const_no": int(row["Const. No."]),
                "winner": safe_str(row["Leading Candidate"]),
                "w_party": winning_party,
                "runner": safe_str(row["Trailing Candidate"]),
                "r_party": safe_str(row["Trailing Party"]),
                "margin": margin,
                "seat_class": classify_seat(margin),
                "lean": json.dumps(lean_data),
                "region": get_region(state),
            })
            count += 1

        await session.commit()
        print(f"✅ Seeded {count} constituencies from CSV")

        # Print summary
        result = await session.execute(text(
            "SELECT seat_class, COUNT(*) FROM constituencies GROUP BY seat_class ORDER BY seat_class"
        ))
        for row in result.all():
            print(f"  {row[0]}: {row[1]} seats")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
