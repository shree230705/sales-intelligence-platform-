"""
Lightweight input validation for auth endpoints.

We deliberately avoid pulling in a schema library (e.g. marshmallow) for
just two small payloads — plain functions are easier to read for a
portfolio reviewer and keep the dependency list minimal. If validation
needs grow substantially in later phases (leads have many more fields),
that's a reasonable point to introduce marshmallow schemas instead.
"""

import re

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validate_register_payload(data):
    """
    Returns (errors, cleaned_data). `errors` is an empty dict if valid.
    """
    errors = {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if len(name) < 2:
        errors["name"] = "Name must be at least 2 characters."
    if not EMAIL_REGEX.match(email):
        errors["email"] = "A valid email address is required."
    if len(password) < 8:
        errors["password"] = "Password must be at least 8 characters."

    return errors, {"name": name, "email": email, "password": password}


def validate_login_payload(data):
    errors = {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not EMAIL_REGEX.match(email):
        errors["email"] = "A valid email address is required."
    if not password:
        errors["password"] = "Password is required."

    return errors, {"email": email, "password": password}
