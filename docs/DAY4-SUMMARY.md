# VoiceSQL — Day 4 Summary: Core Backend (NL → SQL)

## Objective
Build and test the `/query` endpoint end-to-end: a natural language question goes in, safe SQL and real results come out. Tested via PowerShell's `Invoke-RestMethod` (curl's role, per the Blueprint), no UI involved yet.

## What Was Completed

### `backend/sql_guard.py`
- `is_safe_select()`: validates any SQL string is a single, read-only `SELECT` statement. Rejects `INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, stacked statements (`SELECT ...; DROP ...`), and empty/invalid input.
- `clean_sql()`: strips markdown code fences an AI model sometimes wraps SQL in.
- Verified with 9 test cases including a destructive stacked-statement attempt — all passed.

### `backend/nl_to_sql.py`
- `translate(question)`: sends the question + the full database schema to an AI model, returns cleaned SQL text.
- Contains the system prompt with schema grounding and 5 few-shot examples covering simple lookups, aggregation, joins, and relative dates.

### `backend/app.py`
- Added the `/query` POST route: validates the question, calls `translate()`, validates the result with `is_safe_select()`, executes with `db.run_query()`, returns JSON.
- Implements every error case from `docs/API.md`: empty question (400), question too long (400), AI failure (503), unsafe SQL (400), execution failure (422).
- All 6 logic paths verified with automated tests before manual testing began.

### Live Verification
- "Show all customers" → correct SQL, correct 15-row result.
- "Which customer has spent the most money?" → correct 3-table join + `GROUP BY` + `ORDER BY` + `LIMIT`, correctly identified Chetan Mehta as the top spender.
- Empty question → correctly rejected with `"Please ask a question."`.

## ⚠️ Significant Deviation from the Day 2 Architecture: AI Provider Changed

The Day 2 Architecture doc specified the Claude API for NL→SQL translation. During implementation today, three real-world blockers were hit in sequence:

1. **Claude API (Anthropic):** Requires a paid credit balance before any request works — there is no free tier at all, even for testing. Blocked immediately (`credit balance is too low`).
2. **Gemini API (Google):** Free tier exists, but the specific Google Cloud project tied to the API key hit `429 RESOURCE_EXHAUSTED` (quota limit 0) on `gemini-2.0-flash`, then `404` on `gemini-1.5-flash` (model retired), then `403 PERMISSION_DENIED` on `gemini-2.5-flash` (project-level access denial that persisted even after enabling the API and creating a fresh project).
3. **Groq API:** Free tier, no Google-Cloud-style project system, no credit card anywhere in signup. Initially hit the same `httpx` version conflict seen with Anthropic's SDK (fixed by pinning `httpx==0.27.2`). Once fixed, worked immediately and reliably.

**Final decision, approved before implementation:** use **Groq** (`openai/gpt-oss-20b` model) for NL→SQL translation. This is a genuine architecture change from Day 2's plan, made necessary by external account/billing constraints rather than a technical flaw in the original design. The rest of the architecture — Flask, SQLite, the safety guard, the `/query` contract — is completely unchanged.

### Files affected by the provider switch
- `backend/nl_to_sql.py` — rewritten to call Groq instead of Claude.
- `backend/app.py` — `/health` now checks `GROQ_API_KEY` instead of `ANTHROPIC_API_KEY`.
- `backend/requirements.txt` — `groq` and pinned `httpx==0.27.2` replace `anthropic`.
- `frontend/app.js` — health status label updated to reference Groq.
- `.env` — `GROQ_API_KEY` replaces `ANTHROPIC_API_KEY`.

## Debugging Log (for future reference)
| Symptom | Root cause | Fix |
|---|---|---|
| `TypeError: Client.__init__() got an unexpected keyword argument 'proxies'` | Installed `httpx` version too new for the pinned SDK version (hit with both `anthropic` and `groq` SDKs) | Pin `httpx==0.27.2` in `requirements.txt` |
| PowerShell `curl` mangling JSON body | PowerShell aliases `curl` to `Invoke-WebRequest`, which parses quotes differently than real curl | Use `Invoke-RestMethod` with single-quoted `-Body` instead |
| Claude API: `credit balance too low` | No free tier on Anthropic's API | Switched provider (see above) |
| Gemini: `429 RESOURCE_EXHAUSTED`, then `404 NOT_FOUND`, then `403 PERMISSION_DENIED` | Google Cloud project-level free tier eligibility issues, model retirement | Switched provider (see above) |

## ✅ Verified Working
- `/health` — server, database, and API key all confirmed live.
- `/query` — simple lookup, complex join+aggregation, and validation error all confirmed working with real API calls.

## 🚧 Ready to Build Tomorrow
Per the Blueprint's "Day 4 — Frontend UI" section: the mic button, transcript display, results table, and SQL panel — using the Web Speech API, with mock data first before wiring to the now-working `/query` endpoint.

## 🎯 Tomorrow's Objective
Build the full visual interface and get real browser speech-to-text working. No backend changes required — today's `/query` endpoint is stable and ready to be called by tomorrow's UI.
