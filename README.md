# AI-Powered Sales & Lead Management System

> Status: **Phase 1 of 14 — project scaffold complete.** Features below are
> being built incrementally; this README is updated at the end of each
> phase so it never claims something that isn't actually implemented yet.

## Overview

A CRM and sales-intelligence platform that lets a sales team manage leads,
customers, opportunities, proposals, and revenue targets — with an
ML-powered lead scoring model that predicts conversion likelihood and
explains why a lead is ranked the way it is.

## Problem Statement

Sales teams generate a lot of leads but struggle to prioritize them
consistently — which lead gets called back first often comes down to gut
feeling rather than data. This project builds a small SaaS-style platform
that centralizes lead/customer/opportunity data and uses a trained
classification model to score and rank leads by conversion probability.

## Technology Stack

- **Frontend:** React (Vite), Tailwind CSS, React Router, Axios, Recharts
- **Backend:** Python, Flask, Blueprints, JWT auth
- **Database:** MongoDB (PyMongo)
- **Data Science / ML:** pandas, NumPy, scikit-learn
- **DevOps:** Docker, Docker Compose

## System Architecture

See [`docs/architecture.md`](docs/architecture.md) for the full breakdown
of the backend layering, auth flow, and ML serving design.

## Project Structure

```
sales-intelligence-platform/
├── frontend/          # React + Vite + Tailwind SPA
├── backend/           # Flask REST API (app factory, blueprints, services)
│   └── ml/             # Model training script + serialized model (git-ignored)
├── data/               # Sample seed data (CSV)
├── docs/                # Architecture, API, and database documentation
├── docker-compose.yml
└── .env.example
```

## Installation

### Prerequisites
- Python 3.11+
- Node.js 20+
- Docker & Docker Compose (recommended — see below)

### Environment Variables

```bash
cp .env.example .env
```

Then set a real `JWT_SECRET_KEY` (see the comment in `.env.example` for how
to generate one). Never commit `.env`.

## Running Locally (without Docker)

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
python run.py
```
API runs at `http://localhost:5000`.

**Frontend:**
```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```
App runs at `http://localhost:5173`.

**MongoDB:** install and run locally, or point `MONGO_URI` in `.env` at a
free MongoDB Atlas cluster.

## Running with Docker

```bash
docker compose up --build
```

This starts MongoDB, the Flask API, and the React dev server together.
- Frontend: http://localhost:5173
- Backend: http://localhost:5000/api/health

## Verifying Phase 1 works

1. Run either the local or Docker setup above.
2. Open `http://localhost:5173` — you should see a card showing
   **"Backend: connected (connected)"**. This confirms the full chain
   (React → Axios → Flask → MongoDB) is wired correctly, not just that
   each piece runs in isolation.
3. Hit the API directly: `curl http://localhost:5000/api/health` should
   return `{"success": true, "data": {"api": "ok", "database": "connected"}, ...}`.

## Testing

```bash
cd backend
pytest
```

Phase 1 includes one test (`tests/test_health.py`) confirming the app
factory boots and the health route is registered correctly. Each
subsequent phase adds tests for its own features.

## API Documentation

See [`docs/api-documentation.md`](docs/api-documentation.md).

## Database Design

See [`docs/database-schema.md`](docs/database-schema.md).

## Machine Learning

Documented in Phase 9, once the lead-scoring model is built.

## Screenshots

Added once the UI has real pages to show (Phase 8 onward).

## Future Improvements

Tracked in [`docs/architecture.md`](docs/architecture.md#future-improvements-tracked-honestly-not-implemented-yet).

## Learning Outcomes

Documented at project completion (Phase 14), alongside interview prep
materials.

## Author

[Your Name] — B.Sc. Data Science student. Built as a portfolio project
targeting Business Development Executive roles.
