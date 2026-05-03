"""Google Cloud Logging integration for structured logging.

Replaces print-based logging with structured JSON logs that appear
in Google Cloud Console → Logging with proper severity levels,
request IDs, and searchable metadata.
"""
from __future__ import annotations

import logging
import os
import sys


def setup_cloud_logging():
    """Configure logging for both local dev and Cloud Run.

    On Cloud Run: Uses Google Cloud Logging with structured JSON.
    Locally: Uses standard Python logging to stdout.
    """
    log_level = logging.DEBUG if os.getenv("DEBUG", "false").lower() == "true" else logging.INFO

    # Check if running on Cloud Run (K_SERVICE env var is auto-set)
    if os.getenv("K_SERVICE"):
        try:
            import google.cloud.logging

            client = google.cloud.logging.Client()
            client.setup_logging(log_level=log_level)
            logging.info("Google Cloud Logging initialized for Cloud Run")
            return
        except Exception as e:
            print(f"Cloud Logging setup failed, falling back to stdout: {e}")

    # Local development: structured stdout logging
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(handler)

    # Suppress noisy third-party loggers
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)

    logging.info("Local logging initialized")
