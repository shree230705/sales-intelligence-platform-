"""
Customer management endpoints.

POST   /api/customers            -> create a customer
GET    /api/customers            -> list customers (filter/search/paginate)
GET    /api/customers/<id>       -> view a single customer (includes notes/history)
PUT    /api/customers/<id>       -> update customer fields
POST   /api/customers/<id>/notes -> add a note to a customer's history
DELETE /api/customers/<id>       -> delete a customer (admin/manager only)
"""

from flask import Blueprint, request, g

from app.utils.db import get_db
from app.utils.responses import success, error
from app.utils.serializers import serialize_doc, serialize_list
from app.utils.validation import validate_customer_payload
from app.middleware.auth_middleware import requires_auth, requires_role
from app.services.customer_service import (
    create_customer, list_customers, get_customer, update_customer,
    add_note, delete_customer, NotFoundError,
)

customer_bp = Blueprint("customers", __name__, url_prefix="/api/customers")


@customer_bp.route("", methods=["POST"])
@requires_auth
def create():
    data = request.get_json(silent=True) or {}
    errors, cleaned = validate_customer_payload(data, partial=False)
    if errors:
        return error("Validation failed", status_code=400, errors=errors)

    db = get_db()
    customer = create_customer(db, cleaned)
    return success(data=serialize_doc(customer), message="Customer created", status_code=201)


@customer_bp.route("", methods=["GET"])
@requires_auth
def list_all():
    db = get_db()
    args = request.args

    filters = {
        "industry": args.get("industry"),
        "relationshipStatus": args.get("relationshipStatus"),
    }
    result = list_customers(
        db,
        filters=filters,
        search=args.get("search"),
        sort_by=args.get("sortBy", "createdAt"),
        sort_order=args.get("sortOrder", "desc"),
        page=args.get("page", 1),
        limit_arg=args.get("limit", 20),
    )
    return success(data={
        "customers": serialize_list(result["customers"]),
        "pagination": {
            "page": result["page"],
            "limit": result["limit"],
            "total": result["total"],
            "totalPages": result["totalPages"],
        },
    }, message="Customers retrieved")


@customer_bp.route("/<customer_id>", methods=["GET"])
@requires_auth
def get_one(customer_id):
    db = get_db()
    try:
        customer = get_customer(db, customer_id)
    except NotFoundError as exc:
        return error(str(exc), status_code=404)
    return success(data=serialize_doc(customer), message="Customer retrieved")


@customer_bp.route("/<customer_id>", methods=["PUT"])
@requires_auth
def update(customer_id):
    data = request.get_json(silent=True) or {}
    errors, cleaned = validate_customer_payload(data, partial=True)
    if errors:
        return error("Validation failed", status_code=400, errors=errors)

    db = get_db()
    try:
        customer = update_customer(db, customer_id, cleaned)
    except NotFoundError as exc:
        return error(str(exc), status_code=404)
    return success(data=serialize_doc(customer), message="Customer updated")


@customer_bp.route("/<customer_id>/notes", methods=["POST"])
@requires_auth
def add_customer_note(customer_id):
    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()
    if not text:
        return error("Validation failed", status_code=400, errors={"text": "Note text is required."})

    db = get_db()
    try:
        customer = add_note(db, customer_id, text, g.current_user)
    except NotFoundError as exc:
        return error(str(exc), status_code=404)
    return success(data=serialize_doc(customer), message="Note added")


@customer_bp.route("/<customer_id>", methods=["DELETE"])
@requires_role("admin", "manager")
def delete(customer_id):
    db = get_db()
    try:
        delete_customer(db, customer_id)
    except NotFoundError as exc:
        return error(str(exc), status_code=404)
    return success(message="Customer deleted")