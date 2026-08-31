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


LEAD_SOURCES = {"LinkedIn", "Cold Call", "Email", "Referral", "Website",
                 "Advertisement", "Networking", "Other"}
LEAD_STATUSES = {"New", "Contacted", "Qualified", "Meeting Scheduled",
                  "Proposal Sent", "Negotiation", "Won", "Lost"}
LEAD_PRIORITIES = {"Low", "Medium", "High"}


def validate_lead_payload(data, partial=False):
    errors = {}
    cleaned = {}

    def field_present(name):
        return not partial or name in data

    if field_present("companyName"):
        company_name = (data.get("companyName") or "").strip()
        if len(company_name) < 2:
            errors["companyName"] = "Company name must be at least 2 characters."
        cleaned["companyName"] = company_name

    if field_present("contactPerson"):
        contact_person = (data.get("contactPerson") or "").strip()
        if len(contact_person) < 2:
            errors["contactPerson"] = "Contact person must be at least 2 characters."
        cleaned["contactPerson"] = contact_person

    if field_present("email"):
        email = (data.get("email") or "").strip().lower()
        if not EMAIL_REGEX.match(email):
            errors["email"] = "A valid email address is required."
        cleaned["email"] = email

    if field_present("phone"):
        cleaned["phone"] = (data.get("phone") or "").strip()

    if field_present("industry"):
        cleaned["industry"] = (data.get("industry") or "").strip()

    if field_present("companySize"):
        cleaned["companySize"] = (data.get("companySize") or "").strip()

    if field_present("source"):
        source = data.get("source")
        if source not in LEAD_SOURCES:
            errors["source"] = f"Source must be one of: {', '.join(sorted(LEAD_SOURCES))}."
        cleaned["source"] = source

    if field_present("budget"):
        try:
            cleaned["budget"] = float(data.get("budget")) if data.get("budget") not in (None, "") else None
        except (TypeError, ValueError):
            errors["budget"] = "Budget must be a number."

    if field_present("requirement"):
        cleaned["requirement"] = (data.get("requirement") or "").strip()

    if field_present("status"):
        status = data.get("status", "New")
        if status not in LEAD_STATUSES:
            errors["status"] = f"Status must be one of: {', '.join(sorted(LEAD_STATUSES))}."
        cleaned["status"] = status

    if field_present("priority"):
        priority = data.get("priority", "Medium")
        if priority not in LEAD_PRIORITIES:
            errors["priority"] = f"Priority must be one of: {', '.join(sorted(LEAD_PRIORITIES))}."
        cleaned["priority"] = priority

    if field_present("expectedValue"):
        try:
            raw = data.get("expectedValue")
            cleaned["expectedValue"] = float(raw) if raw not in (None, "") else None
        except (TypeError, ValueError):
            errors["expectedValue"] = "Expected value must be a number."

    if not partial:
        for required in ("companyName", "contactPerson", "email", "source"):
            if not cleaned.get(required) and required not in errors:
                errors[required] = "This field is required."

    return errors, cleaned
