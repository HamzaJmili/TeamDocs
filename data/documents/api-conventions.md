# API conventions

Category: Engineering

Fictional Northstar demonstration content. Not a real company policy.

## Authentication

Northstar internal APIs use short-lived bearer tokens issued by the identity service. Never include tokens in URLs or application logs. Validate token scope on every protected route and return 401 for missing or invalid credentials.

## Pagination

List endpoints use cursor pagination with a default page size of 25 and a maximum page size of 100. Responses include items and next_cursor fields. Clients should stop when next_cursor is null.

## Errors and retries

API errors return a request_id, a stable error code, and a human-readable message. Retry 429 and transient 503 responses with exponential backoff and jitter. Do not retry non-idempotent writes unless the endpoint supports an idempotency key.
