"""Application configuration using Pydantic Settings."""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # App
    app_name: str = "India Democracy Simulator"
    debug: bool = True
    api_v1_prefix: str = "/api/v1"

    # Database — SQLite by default (zero config)
    database_url: str = "sqlite+aiosqlite:///./india_democracy_sim.db"
    database_echo: bool = False

    # JWT Auth
    jwt_secret_key: str = "dev-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 1440  # 24 hours

    # AI Model
    model_endpoint: str = "http://localhost:8001"
    model_timeout_seconds: int = 10
    model_max_retries: int = 3

    # Game
    total_lok_sabha_seats: int = 543
    majority_threshold: int = 272
    campaign_weeks: int = 8
    starting_budget_crore: int = 500
    starting_approval: int = 45
    monte_carlo_iterations: int = 1000

    # Google Cloud
    gcp_project_id: str = "secure-totality-495209-f6"
    gcs_bucket_name: str = "india-election-simulator-assets"
    vertex_ai_location: str = "us-central1"
    vertex_ai_model: str = "gemini-2.0-flash"
    firebase_enabled: bool = True
    firestore_enabled: bool = True

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "protected_namespaces": ()}


@lru_cache
def get_settings() -> Settings:
    return Settings()
