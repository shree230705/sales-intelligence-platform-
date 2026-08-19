"""
One-off generator for data/sample_leads.csv.

Run once (already run to produce the committed CSV) via:
    python scripts/generate_sample_leads.py
Not part of the app's runtime — kept for transparency/reproducibility so
anyone reading the repo can see exactly how the sample data was produced
(fully fictional companies/contacts, no real personal data).
"""

import csv
import os
import random
from datetime import datetime, timedelta

random.seed(42)

COMPANIES = [
    "Brightwave Analytics", "Northfield Logistics", "Cobalt Retail Group",
    "Vertex Manufacturing", "Solace Health Systems", "Ledgerline Finance",
    "Pinebridge Consulting", "Aurora Foodworks", "Ironclad Security Co",
    "Meridian Textiles", "Skyline Property Partners", "Harborlight Media",
    "Crestpoint Insurance", "Nimbus Cloud Services", "Fernwood Agritech",
    "Rockridge Construction", "Bluepeak Telecom", "Amberline Cosmetics",
    "Westgate Automotive", "Cedarview Education", "Redstone Mining Co",
    "Silverline Logistics", "Oakhaven Realty", "Tidewater Shipping",
    "Granite Hill Robotics", "Copperfield Legal", "Willowmere Hospitality",
    "Stonebridge Energy", "Maplewood Retail", "Falconbridge Aerospace",
]

CONTACTS = [
    "Ananya Rao", "Devraj Mehta", "Priya Nair", "Karan Malhotra", "Sneha Kapoor",
    "Arjun Verma", "Ishita Sharma", "Rohan Gupta", "Meera Iyer", "Vikram Chauhan",
    "Tanvi Deshmukh", "Aditya Bhatt", "Neha Joshi", "Siddharth Rao", "Pooja Menon",
    "Kabir Singh", "Radhika Pillai", "Yash Trivedi", "Divya Krishnan", "Manav Kohli",
    "Aisha Khan", "Rahul Saxena", "Nandini Pillai", "Varun Choudhary", "Simran Kaur",
    "Aryan Bose", "Lakshmi Subramaniam", "Nikhil Bansal", "Riya D'Souza", "Harsh Vardhan",
]

INDUSTRIES = ["Technology", "Healthcare", "Retail", "Manufacturing", "Finance",
              "Logistics", "Education", "Real Estate", "Hospitality", "Energy"]
COMPANY_SIZES = ["1-10", "11-50", "51-200", "201-500", "500+"]
SOURCES = ["LinkedIn", "Cold Call", "Email", "Referral", "Website",
           "Advertisement", "Networking", "Other"]
STATUSES = ["New", "Contacted", "Qualified", "Meeting Scheduled",
            "Proposal Sent", "Negotiation", "Won", "Lost"]
PRIORITIES = ["Low", "Medium", "High"]
REQUIREMENTS = [
    "Needs a CRM to replace spreadsheet-based lead tracking",
    "Looking for an AI chatbot for customer support integration",
    "Wants a data dashboard for real-time sales visibility",
    "Requires an inventory management system with barcode scanning",
    "Seeking a marketing automation tool for email campaigns",
    "Needs API integration between their ERP and e-commerce platform",
    "Wants a mobile app for field sales reps",
    "Looking for a document management and e-signature solution",
    "Requires a customer support ticketing system",
    "Wants predictive analytics for demand forecasting",
]

rows = []
base_date = datetime(2026, 5, 1)

for i in range(30):
    created = base_date + timedelta(days=random.randint(0, 90))
    last_contacted = created + timedelta(days=random.randint(1, 20))
    next_followup = last_contacted + timedelta(days=random.randint(1, 14))
    company = COMPANIES[i]
    contact = CONTACTS[i]
    email_name = contact.lower().replace(" ", ".").replace("'", "")
    domain = company.lower().replace(" ", "").replace(",", "")[:14]

    rows.append({
        "companyName": company,
        "contactPerson": contact,
        "email": f"{email_name}@{domain}.com",
        "phone": f"+91-9{random.randint(100000000, 999999999)}",
        "industry": random.choice(INDUSTRIES),
        "companySize": random.choice(COMPANY_SIZES),
        "source": random.choice(SOURCES),
        "budget": random.choice([50000, 100000, 250000, 500000, 1000000, 2000000]),
        "requirement": random.choice(REQUIREMENTS),
        "status": random.choice(STATUSES),
        "priority": random.choice(PRIORITIES),
        "createdAt": created.strftime("%Y-%m-%d"),
        "lastContactedAt": last_contacted.strftime("%Y-%m-%d"),
        "nextFollowUpAt": next_followup.strftime("%Y-%m-%d"),
        "expectedValue": random.choice([75000, 150000, 300000, 600000, 1200000]),
        "notes": "Initial outreach logged; awaiting further engagement.",
    })

out_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "sample_leads.csv")
os.makedirs(os.path.dirname(out_path), exist_ok=True)

with open(out_path, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)

print(f"Wrote {len(rows)} leads to {out_path}")
