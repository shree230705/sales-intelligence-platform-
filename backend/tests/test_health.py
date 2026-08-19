"""
Sanity test for Phase 1: confirms the app factory boots and the health
endpoint responds. Later phases add fixtures (test client, test DB seeding)
in a conftest.py that auth/lead tests will reuse.
"""

import pytest
from app import create_app


@pytest.fixture
def client():
    app = create_app("testing")
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_health_check_returns_200_or_503(client):
    """
    We accept either 200 (Mongo reachable) or 503 (Mongo not running in
    this environment) — the point of this test is confirming the Flask
    app boots and the route is wired up correctly, not that a database
    happens to be running wherever pytest executes.
    """
    response = client.get("/api/health")
    assert response.status_code in (200, 503)
    body = response.get_json()
    assert "success" in body
    assert "message" in body
