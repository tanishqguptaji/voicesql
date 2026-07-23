# VoiceSQL — API Design

Status: Finalized Day 2. Implement exactly this contract on Day 3 (`/query`, `/health`) and optionally Day 8 (`/run-sql`). No implementation in this document — spec only.

## Overview

| Method | Endpoint | Auth | Purpose |
|---|---|---|---|
| GET | `/health` | None | Liveness check for deployment monitoring |
| GET | `/` | None | Serves the frontend (`index.html`) |
| POST | `/query` | None | Core endpoint: NL question → SQL → results |
| POST | `/run-sql` | None | *(Optional, Day 8 stretch)* Re-run a user-edited SQL query safely |

No authentication anywhere in v1.0 — this is a public, accountless demo tool per the PRD's explicit scope.

---

## `GET /health`

**Purpose:** Confirms the server is up. Used for deployment verification (Day 2, Day 9, Day 10).

**Request:** none

**Response — 200:**
```json
{ "status": "ok" }
```

**Validation:** none
**Auth:** none
**Error cases:** none expected — if the server can't respond, the host reports it as down at the infrastructure level.

---

## `GET /`

**Purpose:** Serves the single-page frontend (`frontend/index.html`) and its static assets (`style.css`, `app.js`).

**Request:** none
**Response — 200:** HTML page
**Validation / Auth / Errors:** none — static file serving.

---

## `POST /query`

**Purpose:** The core product feature. Takes a natural language question, asks Claude to translate it into SQL using the known schema, validates the SQL is safe, executes it, and returns both the SQL and the results.

**Request:**
```json
{ "question": "Show me the top 5 customers by total spending" }
```

| Field | Type | Required | Constraints |
|---|---|---|---|
| question | string | yes | 1–500 characters, non-empty after trimming whitespace |

**Response — 200 (success):**
```json
{
  "sql": "SELECT c.name, SUM(oi.quantity * oi.unit_price) AS total_spent FROM customers c JOIN orders o ON c.customer_id = o.customer_id JOIN order_items oi ON o.order_id = oi.order_id GROUP BY c.customer_id ORDER BY total_spent DESC LIMIT 5",
  "results": [
    { "name": "Alice Kumar", "total_spent": 1204.50 },
    { "name": "Bob Rao", "total_spent": 980.00 }
  ]
}
```

**Validation:**
- `question` missing or empty → reject before calling Claude.
- `question` over 500 characters → reject before calling Claude (prevents prompt abuse / runaway cost).

**Authentication:** none.

**Error cases:**

| Status | Condition | Response body |
|---|---|---|
| 400 | `question` missing/empty | `{ "error": "Please ask a question." }` |
| 400 | `question` too long | `{ "error": "That question is too long, try rephrasing more briefly." }` |
| 400 | AI generated non-SELECT / unsafe SQL | `{ "error": "Couldn't safely process that question." }` |
| 422 | AI returned SQL that fails to execute (invalid syntax, unknown column) | `{ "error": "Couldn't understand that question, try rephrasing." }` |
| 500 | Unexpected DB execution failure | `{ "error": "Something went wrong running that query." }` |
| 503 | Claude API unreachable or times out | `{ "error": "AI service temporarily unavailable, try again." }` |

Every error case returns JSON with a single human-readable `error` field — the frontend never has to parse different shapes for different failures.

---

## `POST /run-sql` *(Optional — Day 8 stretch feature only)*

**Purpose:** Lets a user edit the generated SQL in the transparency panel and re-run it, without going through the AI translation step again.

**Request:**
```json
{ "sql": "SELECT * FROM products WHERE category = 'Electronics'" }
```

| Field | Type | Required | Constraints |
|---|---|---|---|
| sql | string | yes | Non-empty; must pass the same safety guard as `/query` |

**Response — 200:**
```json
{ "results": [ { "product_id": 3, "name": "Wireless Mouse", "category": "Electronics", "price": 24.99 } ] }
```

**Validation:** identical `sql_guard.is_safe_select()` check used in `/query` — this endpoint reuses that function, it does not duplicate the logic.

**Authentication:** none.

**Error cases:**

| Status | Condition | Response body |
|---|---|---|
| 400 | `sql` missing/empty | `{ "error": "Please provide a query." }` |
| 400 | Unsafe/non-SELECT SQL | `{ "error": "Only read-only SELECT queries are allowed." }` |
| 500 | Execution failure (bad syntax, unknown column) | `{ "error": "That query couldn't be run — check the syntax." }` |

**Note:** This endpoint is explicitly optional per the Blueprint's Day 8 plan. Build it only if Day 8 is ahead of schedule; skipping it does not affect v1.0's Definition of Success.

---

## Cross-Cutting Notes

- All responses are `Content-Type: application/json` except `GET /` which serves HTML.
- No endpoint requires or accepts an `Authorization` header in v1.0.
- Rate limiting is out of scope for v1.0 (single-user demo tool, not public-scale).
- CORS is not needed — frontend and backend are served from the same Flask app (same origin).
