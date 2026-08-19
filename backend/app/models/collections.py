"""
Collection schema validators and indexes.

MongoDB is schemaless by default, but for a system handling sales/revenue
data, letting literally anything into a collection is asking for bugs down
the line (a lead with no companyName, a proposal with a string instead of
a number for amount, etc.). We use MongoDB's native `$jsonSchema` validation
so the *database itself* rejects malformed documents, as a second line of
defense behind the API's own input validation (added in later phases with
marshmallow).

`init_db.py` reads this module and applies it to a real database.
"""

# Each entry: collection name -> (validator dict, list of index specs)
# Index specs are (keys, kwargs) tuples passed straight to
# `collection.create_index(keys, **kwargs)`.

COLLECTIONS = {
    "users": {
        "validator": {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["name", "email", "passwordHash", "role", "createdAt"],
                "properties": {
                    "name": {"bsonType": "string"},
                    "email": {"bsonType": "string"},
                    "passwordHash": {"bsonType": "string"},
                    "role": {"enum": ["admin", "manager", "sales_executive"]},
                    "createdAt": {"bsonType": "date"},
                },
            }
        },
        "indexes": [
            ({"email": 1}, {"unique": True, "name": "uniq_email"}),
        ],
    },
    "leads": {
        "validator": {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["companyName", "contactPerson", "email", "status", "source", "createdAt"],
                "properties": {
                    "companyName": {"bsonType": "string"},
                    "contactPerson": {"bsonType": "string"},
                    "email": {"bsonType": "string"},
                    "phone": {"bsonType": "string"},
                    "industry": {"bsonType": "string"},
                    "companySize": {"bsonType": "string"},
                    "source": {
                        "enum": ["LinkedIn", "Cold Call", "Email", "Referral",
                                 "Website", "Advertisement", "Networking", "Other"]
                    },
                    "budget": {"bsonType": ["double", "int", "null"]},
                    "requirement": {"bsonType": "string"},
                    "status": {
                        "enum": ["New", "Contacted", "Qualified", "Meeting Scheduled",
                                 "Proposal Sent", "Negotiation", "Won", "Lost"]
                    },
                    "priority": {"enum": ["Low", "Medium", "High"]},
                    "assignedTo": {"bsonType": ["objectId", "null"]},
                    "leadScore": {"bsonType": ["int", "double", "null"]},
                    "leadCategory": {"enum": ["Hot", "Warm", "Cold", None]},
                    "createdAt": {"bsonType": "date"},
                    "lastContactedAt": {"bsonType": ["date", "null"]},
                    "nextFollowUpAt": {"bsonType": ["date", "null"]},
                    "expectedValue": {"bsonType": ["double", "int", "null"]},
                    "notes": {"bsonType": "array"},
                },
            }
        },
        "indexes": [
            ({"status": 1}, {"name": "idx_status"}),
            ({"assignedTo": 1}, {"name": "idx_assignedTo"}),
            ({"status": 1, "priority": 1}, {"name": "idx_status_priority"}),
            ({"createdAt": -1}, {"name": "idx_createdAt"}),
        ],
    },
    "customers": {
        "validator": {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["name", "company", "email"],
                "properties": {
                    "name": {"bsonType": "string"},
                    "company": {"bsonType": "string"},
                    "email": {"bsonType": "string"},
                    "phone": {"bsonType": "string"},
                    "industry": {"bsonType": "string"},
                    "address": {"bsonType": "string"},
                    "totalDeals": {"bsonType": "int"},
                    "totalRevenue": {"bsonType": ["double", "int"]},
                    "relationshipStatus": {"enum": ["Active", "Inactive", "At Risk"]},
                    "notes": {"bsonType": "array"},
                },
            }
        },
        "indexes": [
            ({"industry": 1}, {"name": "idx_industry"}),
            ({"relationshipStatus": 1}, {"name": "idx_relationshipStatus"}),
        ],
    },
    "opportunities": {
        "validator": {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["leadId", "stage", "value", "createdAt"],
                "properties": {
                    "leadId": {"bsonType": "objectId"},
                    "stage": {
                        "enum": ["Lead", "Qualified", "Meeting", "Proposal",
                                 "Negotiation", "Won", "Lost"]
                    },
                    "value": {"bsonType": ["double", "int"]},
                    "assignedTo": {"bsonType": ["objectId", "null"]},
                    "createdAt": {"bsonType": "date"},
                    "updatedAt": {"bsonType": "date"},
                },
            }
        },
        "indexes": [
            ({"stage": 1}, {"name": "idx_stage"}),
            ({"leadId": 1}, {"name": "idx_leadId"}),
        ],
    },
    "followups": {
        "validator": {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["leadId", "scheduledDate", "status"],
                "properties": {
                    "leadId": {"bsonType": "objectId"},
                    "scheduledDate": {"bsonType": "date"},
                    "scheduledTime": {"bsonType": "string"},
                    "notes": {"bsonType": "string"},
                    "status": {"enum": ["pending", "completed", "overdue"]},
                    "createdBy": {"bsonType": ["objectId", "null"]},
                },
            }
        },
        "indexes": [
            ({"scheduledDate": 1}, {"name": "idx_scheduledDate"}),
            ({"status": 1}, {"name": "idx_status"}),
        ],
    },
    "proposals": {
        "validator": {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["customerId", "amount", "status"],
                "properties": {
                    "customerId": {"bsonType": "objectId"},
                    "opportunityId": {"bsonType": ["objectId", "null"]},
                    "amount": {"bsonType": ["double", "int"]},
                    "proposalDate": {"bsonType": "date"},
                    "validUntil": {"bsonType": "date"},
                    "status": {
                        "enum": ["Draft", "Sent", "Viewed", "Accepted", "Rejected", "Expired"]
                    },
                    "notes": {"bsonType": "string"},
                },
            }
        },
        "indexes": [
            ({"status": 1}, {"name": "idx_status"}),
            ({"customerId": 1}, {"name": "idx_customerId"}),
        ],
    },
    "competitors": {
        "validator": {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["name", "industry"],
                "properties": {
                    "name": {"bsonType": "string"},
                    "industry": {"bsonType": "string"},
                    "pricing": {"bsonType": "string"},
                    "features": {"bsonType": "array"},
                    "strengths": {"bsonType": "array"},
                    "weaknesses": {"bsonType": "array"},
                    "marketPosition": {"bsonType": "string"},
                    "rating": {"bsonType": ["double", "int"]},
                    "notes": {"bsonType": "string"},
                },
            }
        },
        "indexes": [
            ({"industry": 1}, {"name": "idx_industry"}),
        ],
    },
    "targets": {
        "validator": {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["period", "targetAmount", "periodStart", "periodEnd"],
                "properties": {
                    "userId": {"bsonType": ["objectId", "null"]},
                    "period": {"enum": ["monthly", "quarterly", "annual"]},
                    "targetAmount": {"bsonType": ["double", "int"]},
                    "achievedAmount": {"bsonType": ["double", "int"]},
                    "periodStart": {"bsonType": "date"},
                    "periodEnd": {"bsonType": "date"},
                },
            }
        },
        "indexes": [
            ({"userId": 1}, {"name": "idx_userId"}),
            ({"periodStart": 1, "periodEnd": 1}, {"name": "idx_period_range"}),
        ],
    },
    "notifications": {
        "validator": {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["userId", "message", "type", "isRead", "createdAt"],
                "properties": {
                    "userId": {"bsonType": "objectId"},
                    "message": {"bsonType": "string"},
                    "type": {"bsonType": "string"},
                    "isRead": {"bsonType": "bool"},
                    "createdAt": {"bsonType": "date"},
                },
            }
        },
        "indexes": [
            ({"userId": 1, "isRead": 1}, {"name": "idx_userId_isRead"}),
        ],
    },
    "requirements": {
        "validator": {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["customerId", "rawText", "createdAt"],
                "properties": {
                    "customerId": {"bsonType": "objectId"},
                    "rawText": {"bsonType": "string"},
                    "extractedKeywords": {"bsonType": "array"},
                    "category": {"bsonType": "string"},
                    "recommendedProduct": {"bsonType": "string"},
                    "createdAt": {"bsonType": "date"},
                },
            }
        },
        "indexes": [
            ({"customerId": 1}, {"name": "idx_customerId"}),
        ],
    },
}
