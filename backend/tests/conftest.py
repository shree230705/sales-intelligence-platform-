"""
Shared pytest fixtures.

`test_health.py` (Phase 1) defined its own inline client fixture. This
conftest.py centralizes it so every test module — this phase's
test_debug_routes.py, and auth/lead tests in later phases — reuses the
same test app wired to the `testing` config (see app/config.py), which
points at a separate `sales_platform_test` database rather than dev data.
"""

import pytest
from app import create_app


@pytest.fixture
def app():
    application = create_app("testing")
    application.config["TESTING"] = True
    yield application


@pytest.fixture
def client(app):
    with app.test_client() as client:
        yield client
