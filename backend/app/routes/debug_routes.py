"""
Development-only route for verifying database state.

This is NOT part of the permanent public API surface described in the
project spec — it exists so that during development (and for anyone
reviewing this repo) it's possible to confirm data actually landed in
MongoDB after running scripts/seed_data.py, without needing a Mongo GUI.

Once real authentication exists (Phase 3), this route should be restricted
to the admin role, or removed before any production deployment.
"""

from flask import Blueprint
from app.utils.db import get_db
from app.utils.responses import success, error
from app.models.collections import COLLECTIONS

debug_bp = Blueprint("debug", __name__, url_prefix="/api/debug")


@debug_bp.route("/counts", methods=["GET"])
def collection_counts():
    try:
        db = get_db()
        counts = {name: db[name].count_documents({}) for name in COLLECTIONS.keys()}
        return success(data=counts, message="Document counts per collection")
    except Exception as exc:  # noqa: BLE001
        return error(message=f"Could not read collection counts: {exc}", status_code=503)
