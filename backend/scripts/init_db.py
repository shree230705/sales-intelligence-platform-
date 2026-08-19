"""
Initializes MongoDB: creates each collection (if missing) with schema
validation attached, and creates every index defined in
app/models/collections.py.

This is deliberately idempotent — running it twice does not error or
duplicate anything:
- If a collection already exists, we use `collMod` to update its validator
  instead of trying to create it again.
- `create_index` with the same spec + name is a no-op if it already exists.

Usage:
    cd backend
    python scripts/init_db.py
"""

import os
import sys

# Allow running this script directly (`python scripts/init_db.py`) by
# adding the backend/ directory to the path so `import app...` resolves.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pymongo import MongoClient
from pymongo.errors import OperationFailure
from dotenv import load_dotenv

from app.models.collections import COLLECTIONS

load_dotenv()


def get_client_and_db():
    mongo_uri = os.environ.get("MONGO_URI", "mongodb://localhost:27017/sales_platform")
    client = MongoClient(mongo_uri)
    db = client.get_default_database()
    return client, db


def apply_collection(db, name, definition):
    existing_names = db.list_collection_names()

    if name not in existing_names:
        db.create_collection(name, validator=definition["validator"])
        print(f"  created collection '{name}' with validation")
    else:
        try:
            db.command("collMod", name, validator=definition["validator"])
            print(f"  updated validator on existing collection '{name}'")
        except OperationFailure as exc:
            print(f"  WARNING: could not update validator on '{name}': {exc}")

    collection = db[name]
    for keys, kwargs in definition["indexes"]:
        collection.create_index(list(keys.items()), **kwargs)
    print(f"  ensured {len(definition['indexes'])} index(es) on '{name}'")


def main():
    client, db = get_client_and_db()
    try:
        db.command("ping")
    except Exception as exc:
        print(f"Could not connect to MongoDB at the configured MONGO_URI: {exc}")
        sys.exit(1)

    print(f"Connected to database: {db.name}")
    for name, definition in COLLECTIONS.items():
        apply_collection(db, name, definition)

    print("\nDone. Collections and indexes are set up.")
    client.close()


if __name__ == "__main__":
    main()
