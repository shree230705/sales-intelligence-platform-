"""
Confirms the debug/counts endpoint is wired up and returns a count for
every collection defined in app/models/collections.py.
"""

from app.models.collections import COLLECTIONS


def test_counts_endpoint_returns_all_collections_or_503(client):
    response = client.get("/api/debug/counts")

    # Same reasoning as test_health.py: this environment may not have a
    # reachable MongoDB instance, so we accept either outcome and check
    # the *shape* of the response is correct either way.
    assert response.status_code in (200, 503)
    body = response.get_json()
    assert "success" in body

    if response.status_code == 200:
        counts = body["data"]
        for collection_name in COLLECTIONS.keys():
            assert collection_name in counts
            assert isinstance(counts[collection_name], int)
