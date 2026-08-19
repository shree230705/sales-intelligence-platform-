# API Documentation

> Updated at the end of each phase to document only endpoints that actually
> exist and have been tested.

## Base URL

- Local: `http://localhost:5000`
- All endpoints are prefixed with `/api`

## Response Shape

Every endpoint returns this shape (see `backend/app/utils/responses.py`):

```json
{
  "success": true,
  "message": "Human-readable message",
  "data": { }
}
```

Errors:

```json
{
  "success": false,
  "message": "What went wrong",
  "errors": null
}
```

## Endpoints (Phase 1)

### `GET /api/health`

Confirms the API is running and MongoDB is reachable.

**Request:** none

**Response — 200 OK:**
```json
{
  "success": true,
  "message": "Service is healthy",
  "data": { "api": "ok", "database": "connected" }
}
```

**Response — 503 Service Unavailable** (MongoDB unreachable):
```json
{
  "success": false,
  "message": "Database unreachable: <error detail>",
  "errors": null
}
```

---

Endpoints for auth, leads, customers, opportunities, follow-ups, proposals,
competitors, targets, analytics, notifications, and ML scoring are added
here as each phase implements and tests them.
