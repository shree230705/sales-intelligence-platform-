"""
Customer business logic.

Unlike leads, customers are NOT owned by one rep -- once a lead becomes a
customer, it's treated as a shared team account. Any authenticated user
can view, create, and update customers; only admin/manager can delete one.

totalDeals/totalRevenue are manually settable for now (default 0 on
creation). Once the Proposals/Deals module exists (Phase 7), these
should be computed automatically from real deal records rather than
edited by hand -- noted honestly here rather than pretending this is
already wired up.
"""

from datetime import datetime
from bson import ObjectId
from bson.errors import InvalidId

from app.utils.pagination import parse_pagination


class NotFoundError(Exception):
    pass


def _to_object_id(id_str):
    try:
        return ObjectId(id_str)
    except (InvalidId, TypeError):
        raise NotFoundError("Customer not found.")


def create_customer(db, cleaned_data):
    now = datetime.utcnow()
    customer_doc = {
        "name": cleaned_data["name"],
        "company": cleaned_data["company"],
        "email": cleaned_data["email"],
        "phone": cleaned_data.get("phone", ""),
        "industry": cleaned_data.get("industry", ""),
        "address": cleaned_data.get("address", ""),
        "totalDeals": 0,
        "totalRevenue": 0,
        "relationshipStatus": cleaned_data.get("relationshipStatus", "Active"),
        "notes": [],
        "createdAt": now,
    }
    result = db.customers.insert_one(customer_doc)
    customer_doc["_id"] = result.inserted_id
    return customer_doc


def list_customers(db, filters, search, sort_by, sort_order, page, limit_arg):
    query = {}

    for field in ("industry", "relationshipStatus"):
        if filters.get(field):
            query[field] = filters[field]

    if search:
        regex = {"$regex": search, "$options": "i"}
        query["$or"] = [
            {"name": regex},
            {"company": regex},
            {"email": regex},
        ]

    allowed_sort_fields = {"createdAt", "name", "company", "totalRevenue", "relationshipStatus"}
    sort_field = sort_by if sort_by in allowed_sort_fields else "createdAt"
    sort_direction = -1 if sort_order == "desc" else 1

    page, limit, skip = parse_pagination({"page": page, "limit": limit_arg})

    total = db.customers.count_documents(query)
    cursor = (
        db.customers.find(query)
        .sort(sort_field, sort_direction)
        .skip(skip)
        .limit(limit)
    )
    customers = list(cursor)

    return {
        "customers": customers,
        "page": page,
        "limit": limit,
        "total": total,
        "totalPages": (total + limit - 1) // limit if limit else 0,
    }


def get_customer(db, customer_id):
    customer = db.customers.find_one({"_id": _to_object_id(customer_id)})
    if not customer:
        raise NotFoundError("Customer not found.")
    return customer


def update_customer(db, customer_id, cleaned_data):
    customer_object_id = _to_object_id(customer_id)
    existing = db.customers.find_one({"_id": customer_object_id})
    if not existing:
        raise NotFoundError("Customer not found.")

    if cleaned_data:
        db.customers.update_one({"_id": customer_object_id}, {"$set": cleaned_data})

    return db.customers.find_one({"_id": customer_object_id})


def add_note(db, customer_id, text, author_user):
    customer_object_id = _to_object_id(customer_id)
    existing = db.customers.find_one({"_id": customer_object_id})
    if not existing:
        raise NotFoundError("Customer not found.")

    note = {
        "text": text,
        "addedAt": datetime.utcnow(),
        "addedBy": author_user["email"],
    }
    db.customers.update_one({"_id": customer_object_id}, {"$push": {"notes": note}})
    return db.customers.find_one({"_id": customer_object_id})


def delete_customer(db, customer_id):
    customer_object_id = _to_object_id(customer_id)
    result = db.customers.delete_one({"_id": customer_object_id})
    if result.deleted_count == 0:
        raise NotFoundError("Customer not found.")