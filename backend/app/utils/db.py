"""
MongoDB connection helper.

We keep a single PyMongo client for the lifetime of the process and reuse
it everywhere (services import `get_db()` rather than opening new
connections). This matches how PyMongo is meant to be used — the client
itself manages a connection pool internally.
"""

from pymongo import MongoClient
from pymongo.database import Database
from flask import current_app, g


def get_db() -> Database:
    """
    Return the MongoDB database for the current app context.

    Using Flask's `g` object means we open the connection lazily (on first
    use within a request) and Flask handles attaching it to the current
    application/request context for us.
    """
    if "db" not in g:
        client = MongoClient(current_app.config["MONGO_URI"])
        # The database name is taken from the URI path, e.g.
        # mongodb://localhost:27017/sales_platform -> "sales_platform"
        g.db_client = client
        g.db = client.get_default_database()
    return g.db


def close_db(e=None):
    """Close the Mongo client at the end of the request/app context."""
    client = g.pop("db_client", None)
    if client is not None:
        client.close()


def init_app(app):
    """Register the teardown handler with the Flask app."""
    app.teardown_appcontext(close_db)
