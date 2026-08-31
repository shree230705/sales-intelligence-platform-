"""
Lead management endpoints.
"""

from flask import Blueprint, request, g

from app.utils.db import get_db
from app.utils.responses import success, error
from app.utils.serializers import serialize_doc, serialize_list
from app.utils.validation import validate_lead_payload, LEAD_STATUSES
from app.middleware.auth_middleware import requires_auth, requires_role
from app.services.lead_service import (
    create_lead, list_leads, get_lead, update_lead,
    update_status, assign_lead, delete_lead,
    NotFoundError, ForbiddenError,
)

lead_bp = Blueprint("leads", __name__, url_prefix="/api/leads")


@lead_bp.route("", methods=["POST"])
@requires_auth
def create():
    data = request.get_json(silent=True) or {}
    errors, cleaned = validate_lead_payload(data, partial=False)
    if errors:
        return error("Validation failed", status_code=400, errors=errors)

    db = get_db()
    lead = create_lead(db, cleaned, g.current_user)
    return success(data=serialize_doc(lead), message="Lead created", status_code=201)


@lead_bp.route("", methods=["GET"])
@requires_auth
def list_all():
    db = get_db()
    args = request.args

    filters = {
        "status": args.get("status"),
        "source": args.get("source"),
        "industry": args.get("industry"),
        "priority": args.get("priority"),
        "assignedTo": args.get("assignedTo"),
    }
    result = list_leads(
        db, g.current_user,
        filters=filters,
        search=args.get("search"),
        sort_by=args.get("sortBy", "createdAt"),
        sort_order=args.get("sortOrder", "desc"),
        page=args.get("page", 1),
        limit_arg=args.get("limit", 20),
    )
    return success(data={
        "leads": serialize_list(result["leads"]),
        "pagination": {
            "page": result["page"],
            "limit": result["limit"],
            "total": result["total"],
            "totalPages": result["totalPages"],
        },
    }, message="Leads retrieved")


@lead_bp.route("/<lead_id>", methods=["GET"])
@requires_auth
def get_one(lead_id):
    db = get_db()
    try:
        lead = get_lead(db, lead_id, g.current_user)
    except NotFoundError as exc:
        return error(str(exc), status_code=404)
    except ForbiddenError as exc:
        return error(str(exc), status_code=403)
    return success(data=serialize_doc(lead), message="Lead retrieved")


@lead_bp.route("/<lead_id>", methods=["PUT"])
@requires_auth
def update(lead_id):
    data = request.get_json(silent=True) or {}
    errors, cleaned = validate_lead_payload(data, partial=True)
    if errors:
        return error("Validation failed", status_code=400, errors=errors)

    db = get_db()
    try:
        lead = update_lead(db, lead_id, cleaned, g.current_user)
    except NotFoundError as exc:
        return error(str(exc), status_code=404)
    except ForbiddenError as exc:
        return error(str(exc), status_code=403)
    return success(data=serialize_doc(lead), message="Lead updated")


@lead_bp.route("/<lead_id>/status", methods=["PATCH"])
@requires_auth
def change_status(lead_id):
    data = request.get_json(silent=True) or {}
    new_status = data.get("status")
    if new_status not in LEAD_STATUSES:
        return error(
            "Validation failed", status_code=400,
            errors={"status": f"Status must be one of: {', '.join(sorted(LEAD_STATUSES))}."},
        )

    db = get_db()
    try:
        lead = update_status(db, lead_id, new_status, g.current_user)
    except NotFoundError as exc:
        return error(str(exc), status_code=404)
    except ForbiddenError as exc:
        return error(str(exc), status_code=403)
    return success(data=serialize_doc(lead), message="Lead status updated")


@lead_bp.route("/<lead_id>/assign", methods=["PATCH"])
@requires_role("admin", "manager")
def reassign(lead_id):
    data = request.get_json(silent=True) or {}
    new_assignee_id = data.get("assignedTo")
    if not new_assignee_id:
        return error("Validation failed", status_code=400, errors={"assignedTo": "This field is required."})

    db = get_db()
    try:
        lead = assign_lead(db, lead_id, new_assignee_id, g.current_user)
    except NotFoundError as exc:
        return error(str(exc), status_code=404)
    return success(data=serialize_doc(lead), message="Lead reassigned")


@lead_bp.route("/<lead_id>", methods=["DELETE"])
@requires_role("admin", "manager")
def delete(lead_id):
    db = get_db()
    try:
        delete_lead(db, lead_id)
    except NotFoundError as exc:
        return error(str(exc), status_code=404)
    return success(message="Lead deleted")