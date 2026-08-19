"""
Seeds MongoDB with realistic (fully fictional) sample data across every
collection, so Phase 3 (auth) and Phase 4 (lead management) have real data
to work against from the start.

Run AFTER init_db.py:
    cd backend
    python scripts/init_db.py
    python scripts/seed_data.py

Safe to re-run: it clears each collection before reseeding rather than
appending duplicates.
"""

import csv
import os
import random
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import bcrypt
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
random.seed(42)

DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data"
)


def get_db():
    mongo_uri = os.environ.get("MONGO_URI", "mongodb://localhost:27017/sales_platform")
    client = MongoClient(mongo_uri)
    return client, client.get_default_database()


def hash_password(plain_text):
    return bcrypt.hashpw(plain_text.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def seed_users(db):
    """
    Seeds one user per role so Phase 3 (login) has real accounts to test
    against immediately. Password is the same for all seed accounts —
    this is clearly a development fixture, never real credentials, and
    is documented in README so nobody mistakes it for something secret.
    """
    db.users.delete_many({})
    seed_password = "Password123!"
    password_hash = hash_password(seed_password)

    users = [
        {"name": "Ananya Admin", "email": "admin@salesplatform.dev", "passwordHash": password_hash,
         "role": "admin", "createdAt": datetime.utcnow()},
        {"name": "Manoj Manager", "email": "manager@salesplatform.dev", "passwordHash": password_hash,
         "role": "manager", "createdAt": datetime.utcnow()},
        {"name": "Sara Sales", "email": "sales1@salesplatform.dev", "passwordHash": password_hash,
         "role": "sales_executive", "createdAt": datetime.utcnow()},
        {"name": "Rahul Sales", "email": "sales2@salesplatform.dev", "passwordHash": password_hash,
         "role": "sales_executive", "createdAt": datetime.utcnow()},
    ]
    result = db.users.insert_many(users)
    print(f"  seeded {len(result.inserted_ids)} users (dev password for all: '{seed_password}')")
    return result.inserted_ids


def seed_leads(db, sales_user_ids):
    db.leads.delete_many({})
    csv_path = os.path.join(DATA_DIR, "sample_leads.csv")
    leads = []
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            leads.append({
                "companyName": row["companyName"],
                "contactPerson": row["contactPerson"],
                "email": row["email"],
                "phone": row["phone"],
                "industry": row["industry"],
                "companySize": row["companySize"],
                "source": row["source"],
                "budget": float(row["budget"]),
                "requirement": row["requirement"],
                "status": row["status"],
                "priority": row["priority"],
                "assignedTo": random.choice(sales_user_ids),
                "leadScore": None,
                "leadCategory": None,
                "createdAt": datetime.strptime(row["createdAt"], "%Y-%m-%d"),
                "lastContactedAt": datetime.strptime(row["lastContactedAt"], "%Y-%m-%d"),
                "nextFollowUpAt": datetime.strptime(row["nextFollowUpAt"], "%Y-%m-%d"),
                "expectedValue": float(row["expectedValue"]),
                "notes": [row["notes"]],
            })
    result = db.leads.insert_many(leads)
    print(f"  seeded {len(result.inserted_ids)} leads from sample_leads.csv")
    return result.inserted_ids


def seed_customers(db):
    db.customers.delete_many({})
    companies = [
        ("Solace Health Systems", "Healthcare"), ("Ledgerline Finance", "Finance"),
        ("Pinebridge Consulting", "Technology"), ("Aurora Foodworks", "Retail"),
        ("Ironclad Security Co", "Technology"), ("Meridian Textiles", "Manufacturing"),
        ("Skyline Property Partners", "Real Estate"), ("Harborlight Media", "Technology"),
        ("Crestpoint Insurance", "Finance"), ("Nimbus Cloud Services", "Technology"),
    ]
    contacts = ["Tanvi Deshmukh", "Aditya Bhatt", "Neha Joshi", "Siddharth Rao", "Pooja Menon",
                "Kabir Singh", "Radhika Pillai", "Yash Trivedi", "Divya Krishnan", "Manav Kohli"]
    statuses = ["Active", "Active", "Active", "At Risk", "Inactive"]

    customers = []
    for i, (company, industry) in enumerate(companies):
        total_deals = random.randint(1, 8)
        customers.append({
            "name": contacts[i],
            "company": company,
            "email": f"{contacts[i].lower().replace(' ', '.')}@{company.lower().replace(' ', '')[:12]}.com",
            "phone": f"+91-8{random.randint(100000000, 999999999)}",
            "industry": industry,
            "address": f"{random.randint(10, 999)} {random.choice(['MG Road', 'Park Street', 'Anna Salai', 'FC Road'])}, India",
            "totalDeals": total_deals,
            "totalRevenue": total_deals * random.choice([150000, 300000, 500000]),
            "relationshipStatus": random.choice(statuses),
            "notes": ["Existing customer since onboarding."],
        })
    result = db.customers.insert_many(customers)
    print(f"  seeded {len(result.inserted_ids)} customers")
    return result.inserted_ids


def seed_opportunities(db, lead_ids, sales_user_ids):
    db.opportunities.delete_many({})
    stages = ["Lead", "Qualified", "Meeting", "Proposal", "Negotiation", "Won", "Lost"]
    opportunities = []
    for lead_id in random.sample(lead_ids, min(15, len(lead_ids))):
        created = datetime.utcnow() - timedelta(days=random.randint(1, 60))
        opportunities.append({
            "leadId": lead_id,
            "stage": random.choice(stages),
            "value": random.choice([100000, 250000, 500000, 750000, 1500000]),
            "assignedTo": random.choice(sales_user_ids),
            "createdAt": created,
            "updatedAt": created + timedelta(days=random.randint(0, 10)),
        })
    result = db.opportunities.insert_many(opportunities)
    print(f"  seeded {len(result.inserted_ids)} opportunities")
    return result.inserted_ids


def seed_followups(db, lead_ids, sales_user_ids):
    db.followups.delete_many({})
    followups = []
    for lead_id in random.sample(lead_ids, min(10, len(lead_ids))):
        scheduled = datetime.utcnow() + timedelta(days=random.randint(-5, 14))
        followups.append({
            "leadId": lead_id,
            "scheduledDate": scheduled,
            "scheduledTime": random.choice(["10:00 AM", "11:30 AM", "2:00 PM", "4:30 PM"]),
            "notes": "Follow up on requirement discussion and next steps.",
            "status": "overdue" if scheduled < datetime.utcnow() else "pending",
            "createdBy": random.choice(sales_user_ids),
        })
    result = db.followups.insert_many(followups)
    print(f"  seeded {len(result.inserted_ids)} follow-ups")


def seed_proposals(db, customer_ids, opportunity_ids):
    db.proposals.delete_many({})
    statuses = ["Draft", "Sent", "Viewed", "Accepted", "Rejected", "Expired"]
    proposals = []
    for i in range(10):
        proposal_date = datetime.utcnow() - timedelta(days=random.randint(1, 30))
        proposals.append({
            "customerId": random.choice(customer_ids),
            "opportunityId": random.choice(opportunity_ids) if opportunity_ids else None,
            "amount": random.choice([150000, 300000, 450000, 900000]),
            "proposalDate": proposal_date,
            "validUntil": proposal_date + timedelta(days=30),
            "status": random.choice(statuses),
            "notes": "Standard proposal terms — 30-day validity.",
        })
    result = db.proposals.insert_many(proposals)
    print(f"  seeded {len(result.inserted_ids)} proposals")


def seed_competitors(db):
    db.competitors.delete_many({})
    competitors = [
        {"name": "CloudCRM Pro", "industry": "Technology", "pricing": "$49/user/month",
         "features": ["Lead scoring", "Pipeline management", "Email integration"],
         "strengths": ["Strong integrations", "Established brand"],
         "weaknesses": ["Expensive at scale", "Steep learning curve"],
         "marketPosition": "Market leader", "rating": 4.3,
         "notes": "Primary competitor for mid-market deals."},
        {"name": "SalesTrack Lite", "industry": "Technology", "pricing": "$19/user/month",
         "features": ["Basic CRM", "Contact management"],
         "strengths": ["Low cost", "Simple onboarding"],
         "weaknesses": ["Limited automation", "No ML scoring"],
         "marketPosition": "Budget challenger", "rating": 3.8,
         "notes": "Wins on price with small teams."},
        {"name": "LeadForge", "industry": "Technology", "pricing": "$79/user/month",
         "features": ["AI lead scoring", "Advanced analytics", "API access"],
         "strengths": ["Strong ML features", "Enterprise-ready"],
         "weaknesses": ["High price", "Complex setup"],
         "marketPosition": "Premium/enterprise", "rating": 4.5,
         "notes": "Closest feature competitor to our ML scoring."},
        {"name": "PipelineHQ", "industry": "Technology", "pricing": "$35/user/month",
         "features": ["Kanban pipeline", "Proposal tracking"],
         "strengths": ["Clean UI", "Fast support"],
         "weaknesses": ["No competitor tracking module"],
         "marketPosition": "Mid-market", "rating": 4.1,
         "notes": "Comparable pipeline UX."},
        {"name": "DealFlow", "industry": "Technology", "pricing": "$59/user/month",
         "features": ["Forecasting", "Territory management"],
         "strengths": ["Strong reporting"],
         "weaknesses": ["Outdated interface", "Slow mobile app"],
         "marketPosition": "Enterprise legacy", "rating": 3.6,
         "notes": "Losing market share to newer entrants."},
    ]
    result = db.competitors.insert_many(competitors)
    print(f"  seeded {len(result.inserted_ids)} competitors")


def seed_targets(db):
    db.targets.delete_many({})
    now = datetime.utcnow()
    period_start = now.replace(day=1)
    next_month = (period_start + timedelta(days=32)).replace(day=1)
    targets = [
        {"userId": None, "period": "monthly", "targetAmount": 1000000, "achievedAmount": 750000,
         "periodStart": period_start, "periodEnd": next_month - timedelta(days=1)},
    ]
    result = db.targets.insert_many(targets)
    print(f"  seeded {len(result.inserted_ids)} target(s)")


def main():
    client, db = get_db()
    try:
        db.command("ping")
    except Exception as exc:
        print(f"Could not connect to MongoDB: {exc}")
        sys.exit(1)

    print(f"Seeding database: {db.name}\n")

    user_ids = seed_users(db)
    sales_user_ids = user_ids[2:]  # the two sales_executive accounts

    lead_ids = seed_leads(db, sales_user_ids)
    customer_ids = seed_customers(db)
    opportunity_ids = seed_opportunities(db, lead_ids, sales_user_ids)
    seed_followups(db, lead_ids, sales_user_ids)
    seed_proposals(db, customer_ids, opportunity_ids)
    seed_competitors(db)
    seed_targets(db)

    print("\nSeeding complete.")
    print("Dev login accounts (all use password 'Password123!'):")
    print("  admin@salesplatform.dev       (admin)")
    print("  manager@salesplatform.dev     (manager)")
    print("  sales1@salesplatform.dev      (sales_executive)")
    print("  sales2@salesplatform.dev      (sales_executive)")
    client.close()


if __name__ == "__main__":
    main()
