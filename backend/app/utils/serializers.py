"""
MongoDB document -> JSON-safe dict conversion.

Mongo documents contain `ObjectId` and `datetime` values, neither of which
Flask's `jsonify` can serialize directly. Every route that returns a
document (or list of documents) should pass it through these helpers
instead of returning the raw PyMongo result.
"""

from bson import ObjectId
from datetime import datetime


def serialize_doc(doc):
    """Convert a single MongoDB document into a JSON-serializable dict."""
    if doc is None:
        return None

    result = {}
    for key, value in doc.items():
        if key == "_id":
            result["id"] = str(value)
        elif isinstance(value, ObjectId):
            result[key] = str(value)
        elif isinstance(value, datetime):
            result[key] = value.isoformat()
        elif isinstance(value, list):
            result[key] = [
                serialize_doc(v) if isinstance(v, dict) else
                (str(v) if isinstance(v, ObjectId) else v)
                for v in value
            ]
        elif isinstance(value, dict):
            result[key] = serialize_doc(value)
        else:
            result[key] = value
    return result


def serialize_list(docs):
    """Convert a cursor/list of MongoDB documents into a list of dicts."""
    return [serialize_doc(doc) for doc in docs]
