"""
Authentication endpoints.

POST /api/auth/register  -> create a sales_executive account, returns a token
POST /api/auth/login     -> verify credentials, returns a token
POST /api/auth/logout    -> stateless no-op (see docstring below)
GET  /api/auth/me        -> return the current user, given a valid token
"""

from bson import ObjectId
from bson.errors import InvalidId
from flask import Blueprint, request, g

from app.utils.db import get_db
from app.utils.responses import success, error
from app.utils.serializers import serialize_user
from app.utils.validation import validate_register_payload, validate_login_payload
from app.utils.jwt_utils import generate_token
from app.middleware.auth_middleware import requires_auth
from app.services.auth_service import create_user, verify_credentials

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    errors, cleaned = validate_register_payload(data)
    if errors:
        return error("Validation failed", status_code=400, errors=errors)

    db = get_db()
    try:
        user = create_user(db, cleaned["name"], cleaned["email"], cleaned["password"])
    except ValueError as exc:
        # e.g. "email already exists" — a message that's safe to show the client
        return error(str(exc), status_code=409)

    token = generate_token(user)
    return success(
        data={"token": token, "user": serialize_user(user)},
        message="Registration successful",
        status_code=201,
    )


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    errors, cleaned = validate_login_payload(data)
    if errors:
        return error("Validation failed", status_code=400, errors=errors)

    db = get_db()
    user = verify_credentials(db, cleaned["email"], cleaned["password"])
    if not user:
        # Deliberately generic — never reveal whether the email exists.
        return error("Invalid email or password.", status_code=401)

    token = generate_token(user)
    return success(
        data={"token": token, "user": serialize_user(user)},
        message="Login successful",
    )


@auth_bp.route("/logout", methods=["POST"])
def logout():
    """
    JWTs are stateless — the server never "remembers" that a token was
    issued, so there's nothing to invalidate server-side. The real logout
    action is the frontend deleting its stored token. This endpoint exists
    so the frontend has something conventional to call (and a natural
    place to add server-side token blacklisting later, if ever needed).
    """
    return success(message="Logged out. Discard the token on the client.")


@auth_bp.route("/me", methods=["GET"])
@requires_auth
def me():
    db = get_db()
    try:
        user = db.users.find_one({"_id": ObjectId(g.current_user["id"])})
    except InvalidId:
        return error("Invalid token subject.", status_code=401)

    if not user:
        return error("User not found.", status_code=404)

    return success(data=serialize_user(user), message="Current user")
