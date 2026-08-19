"""
Health check endpoint.

Useful for:
- Confirming the Flask app booted correctly
- Confirming the MongoDB connection is reachable
- Docker Compose healthchecks / uptime monitoring later on
"""

from flask import Blueprint
from app.utils.db import get_db
from app.utils.responses import success, error

health_bp = Blueprint("health", __name__, url_prefix="/api/health")


@health_bp.route("", methods=["GET"])
def health_check():
    try:
        db = get_db()
        # A cheap command that forces a round-trip to MongoDB without
        # touching any real data.
        db.command("ping")
        return success(
            data={"api": "ok", "database": "connected"},
            message="Service is healthy",
        )
    except Exception as exc:  # noqa: BLE001 — deliberate: any DB failure -> 503
        return error(message=f"Database unreachable: {exc}", status_code=503)
