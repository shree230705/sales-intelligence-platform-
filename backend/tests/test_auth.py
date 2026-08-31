"""
Tests the full auth flow against the isolated `testing` database (see
app/config.py's TestingConfig and tests/conftest.py). Each test registers
its own user rather than relying on seed data, so the suite is
self-contained and safe to run repeatedly.
"""

import uuid


def _unique_email():
    return f"test_{uuid.uuid4().hex[:10]}@example.com"


def test_register_creates_user_and_returns_token(client):
    email = _unique_email()
    response = client.post("/api/auth/register", json={
        "name": "Test User",
        "email": email,
        "password": "SecurePass123",
    })
    assert response.status_code == 201
    body = response.get_json()
    assert body["success"] is True
    assert "token" in body["data"]
    assert body["data"]["user"]["email"] == email
    assert body["data"]["user"]["role"] == "sales_executive"
    # The password hash must never be present in an API response.
    assert "passwordHash" not in body["data"]["user"]


def test_register_rejects_duplicate_email(client):
    email = _unique_email()
    payload = {"name": "Test User", "email": email, "password": "SecurePass123"}
    first = client.post("/api/auth/register", json=payload)
    assert first.status_code == 201

    second = client.post("/api/auth/register", json=payload)
    assert second.status_code == 409


def test_register_rejects_short_password(client):
    response = client.post("/api/auth/register", json={
        "name": "Test User",
        "email": _unique_email(),
        "password": "short",
    })
    assert response.status_code == 400
    body = response.get_json()
    assert "password" in body["errors"]


def test_login_with_correct_credentials_returns_token(client):
    email = _unique_email()
    client.post("/api/auth/register", json={
        "name": "Test User", "email": email, "password": "SecurePass123",
    })

    response = client.post("/api/auth/login", json={
        "email": email, "password": "SecurePass123",
    })
    assert response.status_code == 200
    assert "token" in response.get_json()["data"]


def test_login_with_wrong_password_returns_401(client):
    email = _unique_email()
    client.post("/api/auth/register", json={
        "name": "Test User", "email": email, "password": "SecurePass123",
    })

    response = client.post("/api/auth/login", json={
        "email": email, "password": "WrongPassword",
    })
    assert response.status_code == 401


def test_me_requires_a_token(client):
    response = client.get("/api/auth/me")
    assert response.status_code == 401


def test_me_returns_current_user_with_valid_token(client):
    email = _unique_email()
    register_response = client.post("/api/auth/register", json={
        "name": "Test User", "email": email, "password": "SecurePass123",
    })
    token = register_response.get_json()["data"]["token"]

    response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.get_json()["data"]["email"] == email


def test_debug_counts_requires_admin_role(client):
    email = _unique_email()
    register_response = client.post("/api/auth/register", json={
        "name": "Test User", "email": email, "password": "SecurePass123",
    })
    token = register_response.get_json()["data"]["token"]

    # A freshly registered user is always "sales_executive", never admin —
    # so this must be forbidden.
    response = client.get("/api/debug/counts", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403
