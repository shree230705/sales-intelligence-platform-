"""
Application configuration.

All secrets and environment-specific values are read from environment
variables (populated from a .env file locally, or from real environment
variables in production/Docker). Nothing sensitive is hardcoded here.
"""

import os
from datetime import timedelta
from dotenv import load_dotenv
load_dotenv()


class Config:
    """Base configuration shared by all environments."""

    # --- Flask ---
    FLASK_ENV = os.environ.get("FLASK_ENV", "development")
    DEBUG = FLASK_ENV == "development"

    # --- MongoDB ---
    MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/sales_platform")

    # --- JWT ---
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=8)
    JWT_ALGORITHM = "HS256"

    # --- CORS ---
    # Comma-separated list of allowed frontend origins.
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "http://localhost:5173").split(",")

    def __init__(self):
        if not self.JWT_SECRET_KEY:
            raise RuntimeError(
                "JWT_SECRET_KEY is not set. Copy .env.example to .env and "
                "provide a real secret before starting the server."
            )


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    """Used by the pytest suite — points at a separate test database."""

    TESTING = True
    MONGO_URI = os.environ.get("TEST_MONGO_URI", "mongodb://localhost:27017/sales_platform_test")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "test-secret-key-not-for-production")


class ProductionConfig(Config):
    DEBUG = False


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}
