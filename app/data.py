from __future__ import annotations

LOGS = [
    {
        "id": "LOG-101",
        "service": "payment-api",
        "content": "14:31:04 ERROR database connection acquisition timed out after 5000ms",
    },
    {
        "id": "LOG-102",
        "service": "payment-api",
        "content": "14:31:06 WARN active database connections 5/5; pending requests 47",
    },
    {
        "id": "LOG-103",
        "service": "payment-api",
        "content": "14:31:09 ERROR POST /payments returned 504 in 8012ms",
    },
    {
        "id": "LOG-201",
        "service": "auth-api",
        "content": "14:30:55 WARN token refresh failed for expired test session",
    },
    {
        "id": "LOG-301",
        "service": "payment-worker",
        "content": "09:12:10 ERROR queue consumer stalled; last heartbeat 65s ago",
    },
]

RUNBOOKS = [
    {
        "id": "RUNBOOK-DB-01",
        "title": "Database connection pool exhaustion",
        "content": (
            "When requests time out and all database connections are active, compare the pool "
            "configuration with the latest deployment. Roll back an accidental reduction or "
            "restore the approved pool size after human approval."
        ),
    },
    {
        "id": "RUNBOOK-QUEUE-01",
        "title": "Stalled payment queue consumer",
        "content": (
            "When the payment worker heartbeat is missing and queue depth grows, inspect the "
            "consumer and restart the worker only after an operator approves the action."
        ),
    },
    {
        "id": "RUNBOOK-AUTH-01",
        "title": "Authentication failures",
        "content": (
            "Check signing-key rotation, clock skew and token expiry when authentication failures "
            "increase across multiple users."
        ),
    },
]

DEMO_INCIDENTS = [
    {
        "title": "Payment requests are timing out",
        "description": "Customers cannot complete payments and latency rose sharply after a deployment.",
        "service": "payment-api",
    },
    {
        "title": "Payment worker stopped consuming",
        "description": "The payment queue is growing and the worker has stopped reporting heartbeats.",
        "service": "payment-worker",
    },
]

