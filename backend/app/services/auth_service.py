"""
Auth business logic — kept separate from app/routes/auth_routes.py so it
can be unit-tested or reused (e.g. by a future admin "create user" route)
without going through HTTP at all.
"""

import bcrypt
from datetime import datetime

# Public self-registration is intentionally restricted to one role.
# Admin and manager accounts are seed/fixture data for now (see
# scripts/seed_data.py); a proper "admin creates a user" endpoint is a
# natural Phase 4+ addition once role-based routes exist to protect it.
# Without this restriction, anyone could POST /api/auth/register with
# role: "admin" and grant themselves full access.
SELF_REGISTERABLE_ROLE = "sales_executive"


def create_user(db, name, email, password):
    """
    Creates a new user with a bcrypt-hashed password.
    Raises ValueError (safe to show to the client) if the email is taken.
    """
    existing = db.users.find_one({"email": email})
    if existing:
        raise ValueError("An account with this email already exists.")

    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    user_doc = {
        "name": name,
        "email": email,
        "passwordHash": password_hash,
        "role": SELF_REGISTERABLE_ROLE,
        "createdAt": datetime.utcnow(),
    }
    result = db.users.insert_one(user_doc)
    user_doc["_id"] = result.inserted_id
    return user_doc


def verify_credentials(db, email, password):
    """
    Returns the user document if email+password match, otherwise None.
    Deliberately returns None rather than raising for "not found" vs
    "wrong password" — the route layer gives an identical generic error
    for both, so we don't leak which emails are registered.
    """
    user = db.users.find_one({"email": email})
    if not user:
        return None
    if not bcrypt.checkpw(password.encode("utf-8"), user["passwordHash"].encode("utf-8")):
        return None
    return user
