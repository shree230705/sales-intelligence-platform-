"""
Route-protection decorators.

@requires_auth   -> any logged-in user (valid, unexpired JWT)
@requires_role(*roles) -> logged-in AND role is one of the given roles

Both attach the decoded token payload to `g.current_user` as
{"id", "email", "role"} so the route handler can use it — e.g.
GET /me looks up g.current_user["id"] to fetch the full user document.
"""

from functools import wraps
import jwt as pyjwt
from flask import request, g

from app.utils.jwt_utils import decode_token
from app.utils.responses import error


def _authenticate_request():
    """
    Reads and validates the Authorization header.
    Returns None on success (and sets g.current_user), or a Flask
    response tuple to return immediately on failure.
    """
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return error("Missing or malformed Authorization header. Expected: Bearer <token>", status_code=401)

    token = auth_header.split(" ", 1)[1].strip()

    try:
        payload = decode_token(token)
    except pyjwt.ExpiredSignatureError:
        return error("Token has expired. Please log in again.", status_code=401)
    except pyjwt.InvalidTokenError:
        return error("Invalid token.", status_code=401)

    g.current_user = {
        "id": payload["sub"],
        "email": payload["email"],
        "role": payload["role"],
    }
    return None


def requires_auth(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        failure = _authenticate_request()
        if failure is not None:
            return failure
        return f(*args, **kwargs)
    return wrapper


def requires_role(*allowed_roles):
    """
    Usage: @requires_role("admin") or @requires_role("admin", "manager")
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            failure = _authenticate_request()
            if failure is not None:
                return failure
            if g.current_user["role"] not in allowed_roles:
                return error(
                    f"This action requires one of these roles: {', '.join(allowed_roles)}.",
                    status_code=403,
                )
            return f(*args, **kwargs)
        return wrapper
    return decorator
