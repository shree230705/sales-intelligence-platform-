# Database Schema

MongoDB database: `sales_platform` (set via `MONGO_URI`).

> Collections are created implicitly by MongoDB the first time a document
> is inserted. This document describes the planned shape of each
> collection; it's updated to match reality as each phase implements the
> corresponding module.

## Planned Collections

### `users`
```
{
  _id, name, email, passwordHash, role ("admin" | "manager" | "sales_executive"),
  createdAt
}
```

### `leads`
```
{
  _id, companyName, contactPerson, email, phone, industry, companySize,
  source, budget, requirement, status, priority,
  assignedTo (-> users._id), leadScore, leadCategory,
  createdAt, lastContactedAt, nextFollowUpAt, expectedValue, notes: []
}
```

### `customers`
```
{
  _id, name, company, email, phone, industry, address,
  totalDeals, totalRevenue, relationshipStatus, notes: []
}
```

### `opportunities`
```
{ _id, leadId (-> leads._id), stage, value, assignedTo (-> users._id), createdAt, updatedAt }
```

### `followups`
```
{ _id, leadId (-> leads._id), scheduledDate, scheduledTime, notes, status, createdBy (-> users._id) }
```

### `proposals`
```
{ _id, customerId (-> customers._id), opportunityId (-> opportunities._id), amount, proposalDate, validUntil, status, notes }
```

### `competitors`
```
{ _id, name, industry, pricing, features: [], strengths: [], weaknesses: [], marketPosition, rating, notes }
```

### `targets`
```
{ _id, userId (-> users._id, null = company-wide), period, targetAmount, achievedAmount, periodStart, periodEnd }
```

### `notifications`
```
{ _id, userId (-> users._id), message, type, isRead, createdAt }
```

### `requirements`
```
{ _id, customerId (-> customers._id), rawText, extractedKeywords: [], category, recommendedProduct, createdAt }
```

## Relationships

References use MongoDB `ObjectId`s rather than embedding, since each of
these entities (leads, opportunities, proposals, etc.) is queried, updated,
and paginated independently. This is standard normalization logic applied
in a document database.

## Indexes (added as each module is built)

Planned:
- `leads`: index on `status`, `assignedTo`, compound index on `(status, priority)`
- `users`: unique index on `email`
- `followups`: index on `scheduledDate` (for today's/overdue queries)
