"""
Lead business logic and ownership rules.
"""

from datetime import datetime
from bson import ObjectId
from bson.errors import InvalidId

from app.utils.pagination import parse_pagination


class NotFoundError(Exception):
    pass


class ForbiddenError(Exception):
    pass


def _to_object_id(id_str):
    try:
        return ObjectId(id_str)
    except (InvalidId, TypeError):
        raise NotFoundError("Lead not found.")


def create_lead(db, cleaned_data, current_user):
    if current_user["role"] == "sales_executive":
        assigned_to = ObjectId(current_user["id"])
    else:
        requested_assignee = cleaned_data.get("assignedTo")
        assigned_to = ObjectId(requested_assignee) if requested_assignee else ObjectId(current_user["id"])

    now = datetime.utcnow()
    lead_doc = {
        "companyName": cleaned_data["companyName"],
        "contactPerson": cleaned_data["contactPerson"],
        "email": cleaned_data["email"],
        "phone": cleaned_data.get("phone", ""),
        "industry": cleaned_data.get("industry", ""),
        "companySize": cleaned_data.get("companySize", ""),
        "source": cleaned_data["source"],
        "budget": cleaned_data.get("budget"),
        "requirement": cleaned_data.get("requirement", ""),
        "status": cleaned_data.get("status", "New"),
        "priority": cleaned_data.get("priority", "Medium"),
        "assignedTo": assigned_to,
        "leadScore": None,
        "leadCategory": None,
        "createdAt": now,
        "lastContactedAt": None,
        "nextFollowUpAt": None,
        "expectedValue": cleaned_data.get("expectedValue"),
        "notes": [cleaned_data["requirement"]] if cleaned_data.get("requirement") else [],
    }
    result = db.leads.insert_one(lead_doc)
    lead_doc["_id"] = result.inserted_id
    return lead_doc


def _scope_query_to_role(query, current_user):
    if current_user["role"] == "sales_executive":
        query["assignedTo"] = ObjectId(current_user["id"])
    return query


def list_leads(db, current_user, filters, search, sort_by, sort_order, page, limit_arg):
    query = {}
    _scope_query_to_role(query, current_user)

    for field in ("status", "source", "industry", "priority"):
        if filters.get(field):
            query[field] = filters[field]

    if filters.get("assignedTo") and current_user["role"] in ("admin", "manager"):
        try:
            query["assignedTo"] = ObjectId(filters["assignedTo"])
        except (InvalidId, TypeError):
            pass

    if search:
        regex = {"$regex": search, "$options": "i"}
        query["$or"] = [
            {"companyName": regex},
            {"contactPerson": regex},
            {"email": regex},
        ]

    allowed_sort_fields = {"createdAt", "companyName", "expectedValue", "priority", "status"}
    sort_field = sort_by if sort_by in allowed_sort_fields else "createdAt"
    sort_direction = -1 if sort_order == "desc" else 1

    page, limit, skip = parse_pagination({"page": page, "limit": limit_arg})

    total = db.leads.count_documents(query)
    cursor = (
        db.leads.find(query)
        .sort(sort_field, sort_direction)
        .skip(skip)
        .limit(limit)
    )
    leads = list(cursor)

    return {
        "leads": leads,
        "page": page,
        "limit": limit,
        "total": total,
        "totalPages": (total + limit - 1) // limit if limit else 0,
    }


def get_lead(db, lead_id, current_user):
    lead = db.leads.find_one({"_id": _to_object_id(lead_id)})
    if not lead:
        raise NotFoundError("Lead not found.")
    if current_user["role"] == "sales_executive" and str(lead["assignedTo"]) != current_user["id"]:
        raise ForbiddenError("You can only view leads assigned to you.")
    return lead


def update_lead(db, lead_id, cleaned_data, current_user):
    lead = get_lead(db, lead_id, current_user)

    update_fields = {k: v for k, v in cleaned_data.items() if k != "assignedTo"}
    if update_fields:
        db.leads.update_one({"_id": lead["_id"]}, {"$set": update_fields})

    return db.leads.find_one({"_id": lead["_id"]})


def update_status(db, lead_id, new_status, current_user):
    lead = get_lead(db, lead_id, current_user)
    update = {"status": new_status, "lastContactedAt": datetime.utcnow()}
    db.leads.update_one({"_id": lead["_id"]}, {"$set": update})
    return db.leads.find_one({"_id": lead["_id"]})


def assign_lead(db, lead_id, new_assignee_id, current_user):
    lead_object_id = _to_object_id(lead_id)
    lead = db.leads.find_one({"_id": lead_object_id})
    if not lead:
        raise NotFoundError("Lead not found.")

    db.leads.update_one(
        {"_id": lead_object_id},
        {"$set": {"assignedTo": ObjectId(new_assignee_id)}},
    )
    return db.leads.find_one({"_id": lead_object_id})


def delete_lead(db, lead_id):
    lead_object_id = _to_object_id(lead_id)
    result = db.leads.delete_one({"_id": lead_object_id})
    if result.deleted_count == 0:
        raise NotFoundError("Lead not found.")