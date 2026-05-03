"""Shared test fixtures for India Democracy Simulator backend tests."""
import os
import pytest
import asyncio
from typing import AsyncGenerator
from unittest.mock import patch

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

# Override settings BEFORE importing app modules
os.environ["DATABASE_URL"] = "sqlite+aiosqlite://"
os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-testing-only"
os.environ["DEBUG"] = "true"

from app.database import Base, get_db
from app.config import get_settings, Settings
from app.models import User, Constituency
from app.main import app as fastapi_app
from app.routers.auth import create_token, pwd_context

from httpx import AsyncClient, ASGITransport


# ─── Engine & Session ────────────────────────────────────────────

TEST_DATABASE_URL = "sqlite+aiosqlite://"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionFactory = async_sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


# ─── Fixtures ────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def event_loop():
    """Use a single event loop for all session-scoped tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
async def setup_database():
    """Create all tables before each test, drop after."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide an async DB session for testing."""
    async with TestSessionFactory() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Provide an httpx AsyncClient wired to the test database."""

    async def override_get_db():
        yield db_session

    fastapi_app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    fastapi_app.dependency_overrides.clear()


@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user in the database."""
    user = User(
        email="test@example.com",
        display_name="Test Player",
        hashed_password=pwd_context.hash("testpassword123"),
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.commit()
    return user


@pytest.fixture
def auth_token(test_user: User) -> str:
    """Generate a valid JWT token for the test user."""
    return create_token(str(test_user.id))


@pytest.fixture
def auth_headers(auth_token: str) -> dict:
    """HTTP headers with Bearer token."""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
async def seeded_constituencies(db_session: AsyncSession) -> list[Constituency]:
    """Seed 10 test constituencies covering different seat classes."""
    test_data = [
        {"name": "Varanasi", "state_ut": "Uttar Pradesh", "const_no": 1,
         "actual_winner_2024": "Narendra Modi", "winning_party_2024": "Bharatiya Janata Party",
         "runner_up_2024": "Ajay Rai", "runner_up_party_2024": "Indian National Congress",
         "actual_margin_2024": 152513, "seat_class": "safe",
         "default_lean": {"BJP": 0.8, "INC": -0.8}, "region": "North"},
        {"name": "Amethi", "state_ut": "Uttar Pradesh", "const_no": 2,
         "actual_winner_2024": "Kishori Lal Sharma", "winning_party_2024": "Indian National Congress",
         "runner_up_2024": "Smriti Irani", "runner_up_party_2024": "Bharatiya Janata Party",
         "actual_margin_2024": 167196, "seat_class": "safe",
         "default_lean": {"INC": 0.8, "BJP": -0.8}, "region": "North"},
        {"name": "Lucknow", "state_ut": "Uttar Pradesh", "const_no": 3,
         "actual_winner_2024": "Rajnath Singh", "winning_party_2024": "Bharatiya Janata Party",
         "runner_up_2024": "Ravidas Mehrotra", "runner_up_party_2024": "Samajwadi Party",
         "actual_margin_2024": 90000, "seat_class": "safe",
         "default_lean": {"BJP": 0.7, "SP": -0.7}, "region": "North"},
        {"name": "Mumbai North West", "state_ut": "Maharashtra", "const_no": 4,
         "actual_winner_2024": "Ravindra Waikar", "winning_party_2024": "Shiv Sena",
         "runner_up_2024": "Amol Kirtikar", "runner_up_party_2024": "Shiv Sena (Uddhav Balasaheb Thackrey)",
         "actual_margin_2024": 48, "seat_class": "super_swing",
         "default_lean": {"SS": 0.05, "SSUBT": -0.05}, "region": "West"},
        {"name": "Attingal", "state_ut": "Kerala", "const_no": 5,
         "actual_winner_2024": "Adoor Prakash", "winning_party_2024": "Indian National Congress",
         "runner_up_2024": "V Joy", "runner_up_party_2024": "Communist Party of India (Marxist)",
         "actual_margin_2024": 684, "seat_class": "super_swing",
         "default_lean": {"INC": 0.05, "CPIM": -0.05}, "region": "South"},
        {"name": "Chandigarh", "state_ut": "Chandigarh", "const_no": 6,
         "actual_winner_2024": "Manish Tewari", "winning_party_2024": "Indian National Congress",
         "runner_up_2024": "Sanjay Tandon", "runner_up_party_2024": "Bharatiya Janata Party",
         "actual_margin_2024": 2504, "seat_class": "super_swing",
         "default_lean": {"INC": 0.08, "BJP": -0.08}, "region": "North"},
        {"name": "Patna Sahib", "state_ut": "Bihar", "const_no": 7,
         "actual_winner_2024": "Ravi Shankar Prasad", "winning_party_2024": "Bharatiya Janata Party",
         "runner_up_2024": "Anand Mohan", "runner_up_party_2024": "Indian National Congress",
         "actual_margin_2024": 65000, "seat_class": "swing",
         "default_lean": {"BJP": 0.4, "INC": -0.4}, "region": "East"},
        {"name": "Kolkata Dakshin", "state_ut": "West Bengal", "const_no": 8,
         "actual_winner_2024": "Mala Roy", "winning_party_2024": "All India Trinamool Congress",
         "runner_up_2024": "Debasish Kumar", "runner_up_party_2024": "Bharatiya Janata Party",
         "actual_margin_2024": 120000, "seat_class": "safe",
         "default_lean": {"TMC": 0.8, "BJP": -0.8}, "region": "East"},
        {"name": "Chennai South", "state_ut": "Tamil Nadu", "const_no": 9,
         "actual_winner_2024": "Thamizhachi Thangapandian", "winning_party_2024": "Dravida Munnetra Kazhagam",
         "runner_up_2024": "T Navukkarasu", "runner_up_party_2024": "Bharatiya Janata Party",
         "actual_margin_2024": 250000, "seat_class": "safe",
         "default_lean": {"DMK": 0.9, "BJP": -0.9}, "region": "South"},
        {"name": "Jaipur Rural", "state_ut": "Rajasthan", "const_no": 10,
         "actual_winner_2024": "Rao Rajendra Singh", "winning_party_2024": "Bharatiya Janata Party",
         "runner_up_2024": "Pratap Singh", "runner_up_party_2024": "Indian National Congress",
         "actual_margin_2024": 45000, "seat_class": "swing",
         "default_lean": {"BJP": 0.4, "INC": -0.4}, "region": "West"},
    ]

    constituencies = []
    for data in test_data:
        c = Constituency(**data)
        db_session.add(c)
        constituencies.append(c)
    await db_session.flush()
    await db_session.commit()
    return constituencies
