"""
JWT issuing and decoding.

Kept separate from auth_service.py so token mechanics (encoding, expiry,
algorithm) are isolated from user/business logic (password checking,
lookups) — either could change independently.
"""

import jwt
from datetime import datetime
from flask import current_app


def generate_token(user):
    """
    Builds a signed JWT for a user document. The payload deliberately
    carries only what's needed to authorize requests (id, email, role) —
    never the password hash, and nothing that goes stale quickly (we
    re-fetch the full user from the DB in /me rather than trusting an
    old snapshot baked into the token).
    """
    now = datetime.utcnow()
    payload = {
        "sub": str(user["_id"]),
        "email": user["email"],
        "role": user["role"],
        "iat": now,
        "exp": now + current_app.config["JWT_ACCESS_TOKEN_EXPIRES"],
    }
    return jwt.encode(
        payload,
        current_app.config["JWT_SECRET_KEY"],
        algorithm=current_app.config["JWT_ALGORITHM"],
    )


def decode_token(token):
    """
    Raises jwt.ExpiredSignatureError or jwt.InvalidTokenError on failure —
    callers (the auth middleware) are expected to catch these specifically
    so they can return a clear 401 rather than a generic 500.
    """
    return jwt.decode(
        token,
        current_app.config["JWT_SECRET_KEY"],
        algorithms=[current_app.config["JWT_ALGORITHM"]],
    )
