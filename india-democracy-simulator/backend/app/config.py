"""Application configuration using Pydantic Settings.

All settings can be overridden via environment variables.
For production, set JWT_SECRET_KEY and DATABASE_URL at minimum.
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    Attributes:
        app_name: Display name used in API docs and health endpoint.
        debug: Enable debug logging and verbose error responses.
        database_url: Async SQLAlchemy database URL.
        jwt_secret_key: Secret key for signing JWT tokens. MUST be changed in production.
        total_lok_sabha_seats: Total parliamentary constituencies (543 in India).
        majority_threshold: Seats needed to form government (272 = 543/2 + 1).
        campaign_weeks: Number of game turns per session.
        starting_budget_crore: Initial campaign budget in crores (₹).
        starting_approval: Initial voter approval percentage (0-100).
        monte_carlo_iterations: Simulations per seat projection calculation.
    """

    # App
    app_name: str = Field(default="India Democracy Simulator", description="Application display name")
    debug: bool = Field(default=True, description="Enable debug mode")
    api_v1_prefix: str = Field(default="/api/v1", description="API version prefix")

    # Database — SQLite by default (zero config)
    database_url: str = Field(default="sqlite+aiosqlite:///./india_democracy_sim.db", description="Async database URL")
    database_echo: bool = Field(default=False, description="Echo SQL queries to stdout")

    # JWT Auth
    jwt_secret_key: str = Field(default="dev-secret-key-change-in-production", description="JWT signing secret")
    jwt_algorithm: str = Field(default="HS256", description="JWT algorithm")
    jwt_expiration_minutes: int = Field(default=1440, description="Token expiry in minutes (24h)")

    # AI Model
    model_endpoint: str = Field(default="http://localhost:8001", description="AI model inference URL")
    model_timeout_seconds: int = Field(default=10, description="Model request timeout")
    model_max_retries: int = Field(default=3, description="Model request retry count")

    # Game
    total_lok_sabha_seats: int = Field(default=543, description="Total Lok Sabha constituencies")
    majority_threshold: int = Field(default=272, description="Seats needed for majority")
    campaign_weeks: int = Field(default=8, description="Turns per game session")
    starting_budget_crore: int = Field(default=500, description="Initial budget in crores")
    starting_approval: int = Field(default=45, description="Initial approval rating %")
    monte_carlo_iterations: int = Field(default=1000, description="Monte Carlo simulation runs")

    # Google Cloud
    gcp_project_id: str = Field(default="secure-totality-495209-f6", description="GCP project ID")
    gcs_bucket_name: str = Field(default="india-election-simulator-assets", description="Cloud Storage bucket")
    vertex_ai_location: str = Field(default="us-central1", description="Vertex AI region")
    vertex_ai_model: str = Field(default="gemini-2.0-flash", description="Vertex AI model ID")
    firebase_enabled: bool = Field(default=True, description="Enable Firebase Auth")
    firestore_enabled: bool = Field(default=True, description="Enable Firestore sync")

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "protected_namespaces": ()}


@lru_cache
def get_settings() -> Settings:
    """Get cached application settings singleton.

    Returns:
        Settings: The application configuration instance.
    """
    return Settings()

