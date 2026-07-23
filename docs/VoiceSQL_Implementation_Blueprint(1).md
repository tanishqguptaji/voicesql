# VoiceSQL — 9-Day Implementation Blueprint (Days 2–10)

**This document is the single source of truth for the rest of the capstone.** Each day below is self-contained: paste that day's section into a fresh AI conversation and it has enough context to continue building without re-planning or re-designing anything.

> **Day 2 Update:** Full technical specs are now finalized in `docs/`: `ARCHITECTURE.md`, `SCHEMA.md`, `API.md`, `UI-WIREFRAMES.md`, `PROJECT-STRUCTURE.md`. Days 3–8 below should follow those documents exactly for schema fields, endpoint contracts, error responses, and UI states — no design decisions remain open. The `/run-sql` endpoint mentioned as an optional Day 8 stretch now has a full spec in `API.md` if there's time to build it.

## Project Snapshot (same in every day's context)

- **Product:** VoiceSQL — speak a question in plain English, get the SQL + the results, no SQL knowledge needed.
- **User:** Solo developer building a portfolio capstone; demo audience is recruiters/reviewers.
- **Time budget:** ~2 hours/day.
- **Locked tech stack (finalized Day 2, do not change without explicit re-plan):**
  - Frontend: single-page HTML/CSS/JavaScript, using the browser-native **Web Speech API** for speech-to-text (Chrome only, no external speech service, no cost).
  - Backend: **Python + Flask**, one main `/query` endpoint.
  - AI translation: **Claude API** (Anthropic), prompted with the DB schema, to convert NL → SQL.
  - Database: **SQLite**, preloaded sample e-commerce dataset (`customers`, `products`, `orders`, `order_items`).
  - Safety: backend rejects any non-`SELECT` SQL before execution.
  - Deployment: free-tier host with a public URL (finalized Day 2 — Render is the working assumption for a Flask app).
- **Priority order for polish:** 1) Voice UX, 2) Complex query handling, 3) SQL transparency.
- **Out of scope for v1.0:** accounts/auth, custom DB uploads, multi-turn follow-ups, charts, editable SQL (stretch only), mobile app, paid tools.

---

## Day 2 — Setup: Environment, Stack Lock-In, Sample Database

### 🎯 Objective
Finalize the tech stack, set up the local dev environment, create the sample database, and get a "hello world" version deployed live — deploying early de-risks Day 10.

### 📖 What I'll learn
Project scaffolding for a Flask + SQLite app, designing a small relational schema, and deploying a minimal Flask app to a free host before any real features exist.

### 🛠 Features to build
- Working local Flask server.
- Sample SQLite database with realistic e-commerce data.
- A trivial live deployment (even just "Hello VoiceSQL" on the deployed URL).

### 📝 Step-by-step implementation plan
1. Create project folder `voicesql/` with subfolders `backend/`, `frontend/`, `database/`.
2. Set up a Python virtual environment; install `flask`, `anthropic`, `python-dotenv`.
3. Create `database/build_db.py`: a script that creates `database/sample.db` (SQLite) with 4 tables:
   - `customers(customer_id, name, email, city, signup_date)`
   - `products(product_id, name, category, price)`
   - `orders(order_id, customer_id, order_date, status)`
   - `order_items(order_item_id, order_id, product_id, quantity, unit_price)`
   Seed with ~15 customers, ~15 products, ~40 orders, ~80 order_items with varied dates (spanning several months) so date-filtered questions have real answers.
4. Write `backend/app.py` with a single route `/` returning "VoiceSQL backend running" and a `/health` route returning JSON `{status: "ok"}`.
5. Get an Anthropic API key (guided step — see manual task below) and store it in a local `.env` file (never commit this file).
6. Initialize a git repo, add `.gitignore` (must include `.env`, `*.db` is fine to include since it's sample data, `venv/`).
7. Push to GitHub (guided step).
8. Create a free account on the chosen host (Render) and deploy the skeleton Flask app (guided step) so `/health` is reachable at a public URL.

### 📂 Files and folders to create or modify
```
voicesql/
  backend/
    app.py
    requirements.txt
  database/
    build_db.py
    sample.db          (generated)
  frontend/             (empty for now, used from Day 4)
  .env                  (local only, not committed)
  .gitignore
  README.md
```

### 🔗 APIs, libraries, services, or tools to integrate
- Anthropic Claude API (key setup only today, not called yet).
- Flask, python-dotenv (pip packages).
- GitHub (version control).
- Render free tier (deployment target).

### 🧪 Testing tasks
- Run `build_db.py` and confirm `sample.db` is created with all 4 tables populated (spot-check with `sqlite3 sample.db ".tables"` and a couple of `SELECT` counts).
- Run Flask locally, hit `/health` in the browser, confirm JSON response.
- Hit the deployed `/health` URL from the browser and confirm the same response live.

### 🐞 Common issues and debugging tips
- **`ModuleNotFoundError`**: virtual environment not activated — check the terminal prompt shows `(venv)`.
- **Render deploy fails**: usually a missing `requirements.txt` or wrong start command — Render needs `gunicorn` in requirements and a start command like `gunicorn backend.app:app`.
- **SQLite file not found on deploy**: confirm the DB file path is relative to the app's working directory, not your local machine's absolute path.

### ✅ End-of-day checklist
- [ ] Local Flask app runs and `/health` responds.
- [ ] `sample.db` exists with all 4 tables and realistic seed data.
- [ ] Anthropic API key obtained and stored in `.env` (not committed).
- [ ] Code pushed to GitHub.
- [ ] `/health` reachable at a public Render URL.

### 📸 Expected project state and screenshots to capture
- Screenshot of terminal showing `sample.db` tables/counts.
- Screenshot of `/health` responding in browser, both locally and on the live Render URL.

### ➡️ Handoff notes for Day 3
Stack is locked: Flask backend, SQLite sample DB with 4 tables, Claude API key ready, live skeleton deployed. Day 3 builds the actual `/query` endpoint and the NL→SQL prompt — no more setup decisions needed.

---

## Day 3 — Core Backend: NL → SQL Translation Endpoint

### 🎯 Objective
Build and test the backend brain: an endpoint that takes a natural language question and returns a safe, correct SQL query plus results — tested via curl/Postman, no UI yet.

### 📖 What I'll learn
Schema-aware prompt engineering for reliable SQL generation, and building a basic safety validation layer before executing AI-generated code against a real database.

### 🛠 Features to build
- `/query` POST endpoint accepting `{ "question": "..." }`.
- A system prompt that gives Claude the exact schema and instructs it to output only a single `SELECT` statement.
- A validator that rejects anything that isn't a pure `SELECT`.
- Query execution against `sample.db` and JSON response with both `sql` and `results`.

### 📝 Step-by-step implementation plan
1. In `backend/`, create `schema.py` exporting a Python string with the full CREATE TABLE statements (or a plain-English schema description) for `customers`, `products`, `orders`, `order_items` — this gets embedded in every prompt.
2. Create `nl_to_sql.py` with a function `translate(question: str) -> str` that calls the Claude API with a system prompt like: *"You are a SQL generator for this SQLite schema: {schema}. Given a question, output ONLY the SQL SELECT query, no explanation, no markdown fences."*
3. Create `sql_guard.py` with a function `is_safe_select(sql: str) -> bool` that checks (case-insensitive) the query starts with `SELECT` and contains none of `INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, `ATTACH`, `PRAGMA`, `;` followed by more text (no stacked statements).
4. Create `db.py` with `run_query(sql: str) -> list[dict]` using `sqlite3`, returning rows as dictionaries (use `conn.row_factory = sqlite3.Row`).
5. Wire it all into `app.py`'s `/query` route: receive question → `translate()` → `is_safe_select()` (reject with 400 + friendly message if false) → `run_query()` → return `{ "sql": ..., "results": ... }` as JSON. Wrap in try/except so a bad query returns a clean error, never a crash.
6. Test with curl or Postman using ~6 questions of increasing difficulty (see testing tasks).

### 📂 Files and folders to create or modify
```
backend/
  app.py          (add /query route)
  schema.py        (new)
  nl_to_sql.py      (new)
  sql_guard.py      (new)
  db.py            (new)
```

### 🔗 APIs, libraries, services, or tools to integrate
- Anthropic Claude API (`anthropic` Python SDK) — this is the first day it's actually called.
- `sqlite3` (Python standard library).

### 🧪 Testing tasks
Test via curl/Postman with questions like:
1. "Show all customers" (simple SELECT *)
2. "Show products under $50" (filter)
3. "List the 5 most recent orders" (ORDER BY + LIMIT)
4. "What is the total revenue from all orders?" (aggregation, SUM, join order_items)
5. "Which customer has spent the most money?" (join + GROUP BY + ORDER BY + LIMIT)
6. "Show me all products in the Electronics category ordered by price" (filter + sort)
- Also test one deliberately malicious-style prompt like "delete all customers" to confirm `sql_guard.py` blocks it and returns a friendly error, not a crash.

### 🐞 Common issues and debugging tips
- **Claude wraps SQL in markdown fences (```sql ... ```)**: strip fences in `translate()` before returning — check for and remove leading/trailing triple backticks.
- **Column name mismatches**: if Claude invents a column that doesn't exist, the schema string is likely incomplete — double check `schema.py` lists every column exactly as created.
- **Empty results on a valid question**: check the seed data in `sample.db` actually covers that case (e.g., no orders in the date range asked about).

### ✅ End-of-day checklist
- [ ] `/query` endpoint works locally for all 6 test questions.
- [ ] Unsafe/destructive queries are blocked with a clean error, not executed.
- [ ] Errors (bad question, DB error) return JSON with a clear message, never a 500 crash with no body.

### 📸 Expected project state and screenshots to capture
- Screenshot of a curl/Postman call with a simple question and its JSON response (sql + results).
- Screenshot of the aggregation question (#5) working correctly — this is your hardest test case.

### ➡️ Handoff notes for Day 4
Backend `/query` endpoint is fully functional and tested via API calls — no frontend yet. Day 4 builds the browser UI (mic button, transcript, results table, SQL panel) but does NOT wire it to the backend yet; that wiring happens Day 5.

---

## Day 4 — Frontend UI: Voice Capture and Layout

### 🎯 Objective
Build the complete visual interface — mic button, transcript display, results table, SQL panel — and get real browser speech-to-text working, all with mocked/static data (no backend calls yet).

### 📖 What I'll learn
Using the browser's native Web Speech API for microphone capture and transcription, and structuring a clean single-page UI without a frontend framework.

### 🛠 Features to build
- Mic button with three visual states: idle, listening, processing.
- Live transcript display of what was heard.
- Static/mock results table and SQL panel (hardcoded sample data for now) to validate the layout.

### 📝 Step-by-step implementation plan
1. Create `frontend/index.html` with: a header ("VoiceSQL"), a large mic button, a transcript text area, a results table container, and a collapsible "Show SQL" panel.
2. Create `frontend/style.css`: clean, modern layout — center-aligned mic button, subtle color palette, readable monospace font for the SQL panel.
3. Create `frontend/app.js`:
   - Check `window.SpeechRecognition || window.webkitSpeechRecognition` exists; if not, show a message "Please use Chrome."
   - On mic button click: start `SpeechRecognition`, change button to "listening" state (e.g., pulsing animation).
   - On `onresult`: display the transcript text; change button to "processing" state.
   - On `onerror`/`onend` with no result: reset button to idle and show "Didn't catch that, try again."
4. Populate the results table and SQL panel with **hardcoded mock data** (e.g., 3 fake rows) just to confirm the layout renders well — this proves the UI works before wiring real data Day 5.
5. Serve `frontend/` as static files from Flask (add a route or use `static_folder` in `app.py`) so it's part of the same deployable app.

### 📂 Files and folders to create or modify
```
frontend/
  index.html   (new)
  style.css    (new)
  app.js       (new)
backend/
  app.py       (serve frontend as static files)
```

### 🔗 APIs, libraries, services, or tools to integrate
- Browser Web Speech API (`SpeechRecognition` / `webkitSpeechRecognition`) — no install needed, built into Chrome.

### 🧪 Testing tasks
- Click mic, speak a sentence, confirm the transcript appears correctly in Chrome.
- Test the "no speech detected" / error path by clicking mic and staying silent.
- Resize the browser window to confirm layout doesn't break (basic responsiveness).
- Confirm the mock results table and SQL panel display and look clean.

### 🐞 Common issues and debugging tips
- **Mic permission blocked**: Chrome will prompt for mic access on first use — if silently denied, check the site permissions icon in the address bar.
- **`SpeechRecognition` undefined**: only Chrome/Chromium and some Edge versions support this reliably — confirm you're testing in Chrome.
- **Recognition stops after a few seconds of silence**: this is expected browser behavior; handle `onend` gracefully rather than treating it as an error.

### ✅ End-of-day checklist
- [ ] Mic button captures real speech and displays an accurate transcript.
- [ ] All 3 button states (idle/listening/processing) are visually distinct.
- [ ] Mock results table and SQL panel render cleanly.
- [ ] Frontend is served from the same Flask app (single deployable unit).

### 📸 Expected project state and screenshots to capture
- Screenshot of the idle state.
- Screenshot of the listening state with a live transcript.
- Screenshot of the mock results table + SQL panel.

### ➡️ Handoff notes for Day 5
UI is fully built and voice capture works, but everything after the transcript is still mock data. Day 5 replaces the mock data with a real fetch call to the Day 3 `/query` backend endpoint — this is the integration day.

---

## Day 5 — Integration: Connect Frontend to Backend End-to-End

### 🎯 Objective
Replace all mock data with real calls to the `/query` backend so the full pipeline works: speak → transcribe → translate to SQL → execute → display real results.

### 📖 What I'll learn
Wiring a JS frontend to a Flask backend with `fetch`, handling asynchronous loading states, and end-to-end debugging across the full stack.

### 🛠 Features to build
- Real `fetch('/query', {...})` call triggered after transcript is captured.
- Loading spinner/state while waiting for the backend response.
- Real results table and SQL panel populated from the API response.
- Basic error display in the UI (not just console) for backend failures.

### 📝 Step-by-step implementation plan
1. In `app.js`, after `onresult` gives a transcript, call `fetch('/query', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({question: transcript}) })`.
2. Show a loading indicator ("Thinking...") while the fetch is pending; disable the mic button during this time.
3. On success: parse JSON, render the `results` array as an HTML table (dynamically build `<table>` rows/columns from the object keys — don't hardcode column names since they vary by question) and put `sql` text into the SQL panel.
4. On failure (network error or backend's own error JSON): show a friendly inline message in the UI (e.g., "Couldn't process that question, try rephrasing") — never a raw error or blank screen.
5. Add a small "Ask Another Question" reset button that clears transcript/results and returns the mic button to idle.
6. Test the full loop for all 6 questions from Day 3, now spoken aloud instead of curl.
7. Redeploy to Render and test the full loop again on the live URL (catches any local-vs-deployed environment differences early).

### 📂 Files and folders to create or modify
```
frontend/
  app.js       (add fetch integration, loading/error states)
  style.css    (loading spinner styling)
backend/
  app.py       (confirm CORS is not an issue since frontend is same-origin)
```

### 🔗 APIs, libraries, services, or tools to integrate
- None new — this day is pure integration of Day 3 backend + Day 4 frontend.

### 🧪 Testing tasks
- Speak all 6 Day 3 test questions aloud through the real UI and confirm correct results each time.
- Deliberately mumble/say something nonsensical to confirm graceful error handling.
- Test on the live Render URL, not just localhost.
- Test clicking "Ask Another Question" and confirm state resets cleanly.

### 🐞 Common issues and debugging tips
- **Fetch works locally but fails on Render**: check the fetch URL is a relative path (`/query`) not `http://localhost:5000/query`.
- **CORS errors**: shouldn't occur since frontend is served by the same Flask app (same origin) — if they do, you likely have a hardcoded absolute URL somewhere.
- **Slow response with no feedback**: confirm the loading state actually shows immediately on button click, not just after the fetch resolves.

### ✅ End-of-day checklist
- [ ] Full voice → SQL → results loop works end-to-end, locally and live.
- [ ] Loading state is visible during processing.
- [ ] Errors show a friendly in-UI message, no blank screens or console-only errors.
- [ ] "Ask Another Question" resets state cleanly.

### 📸 Expected project state and screenshots to capture
- Screenshot of a full successful cycle: transcript + real results table + real SQL panel, on the live URL.
- Screenshot of the graceful error state.

### ➡️ Handoff notes for Day 6
The app is now fully functional end-to-end with basic questions. Day 6 is dedicated entirely to strengthening the AI's handling of complex/tricky questions (joins, multi-condition filters, aggregations) — this is priority #2 in the project's polish ranking.

---

## Day 6 — Complex Query Handling & Prompt Hardening

### 🎯 Objective
Significantly improve the AI's reliability on complex natural language questions — this is the second-highest priority feature per your ranking.

### 📖 What I'll learn
Iterative prompt engineering with few-shot examples, and how to systematically test and improve an LLM-powered feature.

### 🛠 Features to build
- An improved system prompt with few-shot examples covering joins, aggregations, and multi-condition filters.
- A documented test set of 12–15 questions spanning difficulty levels, with pass/fail tracking.

### 📝 Step-by-step implementation plan
1. Write out 12–15 target questions spanning: simple lookups, single filters, sorting/limits, two-table joins, three-table joins, aggregations (SUM/COUNT/AVG), GROUP BY with HAVING-style logic, and date range filters (e.g., "last month," "this year").
2. Run each through the current `/query` endpoint and log which succeed vs. fail (create `testing/test_questions.md` documenting question → expected result → actual result → pass/fail).
3. For failures, inspect the generated SQL to find the pattern (e.g., AI doesn't know how to join `order_items` to `products` to get category-level totals).
4. Improve `nl_to_sql.py`'s system prompt: add 3–5 few-shot examples directly in the prompt showing a natural language question and its correct SQL, covering the failure patterns found.
5. Add an explicit instruction for relative dates: tell the prompt today's reference date and how to compute "last month" / "this year" in SQLite date functions (`date('now', '-1 month')` etc.).
6. Re-run the full test set until at least 10 of 12–15 questions pass reliably.
7. Lock in a final curated list of 8–10 demo questions (the ones that work best) — this becomes your Day 10 demo script.

### 📂 Files and folders to create or modify
```
backend/
  nl_to_sql.py         (expanded system prompt with few-shot examples)
testing/
  test_questions.md    (new — test log, doubles as future demo script source)
```

### 🔗 APIs, libraries, services, or tools to integrate
- None new — pure prompt/backend refinement of existing Claude API integration.

### 🧪 Testing tasks
- Full pass through all 12–15 test questions, logged with pass/fail in `test_questions.md`.
- Specifically verify a 3-table join question (e.g., "Which product category generated the most revenue?").
- Specifically verify a relative-date question (e.g., "How many orders were placed last month?").

### 🐞 Common issues and debugging tips
- **AI hallucinates a column/table**: reinforce the exact schema is fed in every call; check `schema.py` didn't drift from the real DB.
- **Ambiguous questions produce wrong joins**: add a few-shot example showing the correct join path for your specific schema.
- **Date math wrong**: confirm you're passing the current date into the prompt rather than relying on the model's own notion of "today."

### ✅ End-of-day checklist
- [ ] At least 10 of 12–15 test questions pass reliably.
- [ ] A 3-table join question works correctly.
- [ ] A relative-date question works correctly.
- [ ] Final list of 8–10 demo questions selected and documented.

### 📸 Expected project state and screenshots to capture
- Screenshot of `test_questions.md` showing the pass/fail log.
- Screenshot of the toughest passing query (join + aggregation) with results.

### ➡️ Handoff notes for Day 7
Query intelligence is now solid and a demo question list exists. Day 7 shifts focus to priority #1: polishing the voice UX itself (this is where the demo's "wow factor" should be strongest).

---

## Day 7 — Voice UX Polish (Top Priority Feature)

### 🎯 Objective
Make the voice interaction feel smooth, responsive, and delightful — this is the #1 priority for polish per your ranking, since it's the first thing a reviewer experiences.

### 📖 What I'll learn
Micro-interaction design (animations, state transitions) and handling real-world speech recognition edge cases gracefully.

### 🛠 Features to build
- Smooth mic button animation while listening (e.g., pulsing ring).
- A brief transcript confirmation step before sending to the backend, so users can catch misheard words.
- A one-click "retry" if the transcript looks wrong, without reloading the page.
- Subtle sound or visual cue when listening starts/stops.

### 📝 Step-by-step implementation plan
1. Add a CSS pulsing/glow animation to the mic button during the "listening" state (`@keyframes` scaling + opacity).
2. After `onresult`, instead of immediately calling the backend, show the transcript with two buttons: "Ask This" and "Try Again" — giving the user a chance to confirm or redo before spending an AI call.
3. Wire "Try Again" to restart `SpeechRecognition` cleanly, resetting any prior transcript.
4. Add a short transition/fade animation between states (idle → listening → confirm → processing → results) so the UI never jumps abruptly.
5. Handle the case where `SpeechRecognition` returns low-confidence or empty results with a clear "Didn't catch that" message and auto-focus back on the mic button.
6. Test on a few different phrasings/pacing (fast talking, pausing mid-sentence) to make sure the experience holds up.
7. Redeploy and test the polished flow on the live URL.

### 📂 Files and folders to create or modify
```
frontend/
  app.js       (confirm-before-send flow, retry logic)
  style.css    (animations, transitions)
```

### 🔗 APIs, libraries, services, or tools to integrate
- None new — refinement of existing Web Speech API integration.

### 🧪 Testing tasks
- Test the full listening → confirm → ask flow multiple times in a row without page reload.
- Test "Try Again" after a bad transcript.
- Test speaking quickly, then slowly, then with a mid-sentence pause.
- Verify animations don't lag or stutter.

### 🐞 Common issues and debugging tips
- **Animation janky/stutters**: prefer CSS `transform`/`opacity` transitions over animating `width`/`height` (better browser performance).
- **Recognition restarts oddly on "Try Again"**: make sure the previous `SpeechRecognition` instance is fully stopped (`.stop()` or `.abort()`) before starting a new one.
- **State gets stuck in "processing"**: add a safety timeout that resets to idle if no response after ~15 seconds.

### ✅ End-of-day checklist
- [ ] Mic button animates smoothly through all states.
- [ ] Transcript confirmation step works and "Try Again" resets cleanly.
- [ ] No stuck states after repeated use.
- [ ] Live deployed version reflects all polish.

### 📸 Expected project state and screenshots to capture
- Screenshot of the listening animation mid-pulse.
- Screenshot of the transcript confirmation step ("Ask This" / "Try Again").

### ➡️ Handoff notes for Day 8
Voice UX is now polished and this is the strongest part of the demo. Day 8 adds polish to the SQL transparency panel (priority #3) and, only if time remains, the optional editable-SQL stretch feature.

---

## Day 8 — SQL Transparency Polish

### 🎯 Objective
Make the "Generated SQL" panel genuinely useful and trustworthy — clear formatting, syntax highlighting, and (time permitting) an editable/re-runnable query box.

### 📖 What I'll learn
Basic client-side syntax highlighting and, if time allows, safely re-running a user-edited query through the same safety guard built on Day 3.

### 🛠 Features to build
- Formatted, syntax-highlighted SQL display (keywords in a distinct color/weight).
- A "Copy SQL" button.
- Stretch (only if ahead of schedule): an editable textarea version of the SQL panel with a "Run Edited Query" button that goes through the same `/query`-style safety validation.

### 📝 Step-by-step implementation plan
1. Improve the SQL panel's HTML/CSS: monospace font, line spacing, and a light background box distinct from the results table.
2. Add lightweight manual syntax highlighting: a small JS function that wraps SQL keywords (`SELECT`, `FROM`, `WHERE`, `JOIN`, `GROUP BY`, `ORDER BY`, `LIMIT`) in a `<span>` with a highlight class — no external library needed for this scope.
3. Add a "Copy SQL" button using `navigator.clipboard.writeText()`.
4. **If ahead of schedule only:** add a new backend route `/run-sql` that accepts raw SQL text, runs it through the existing `sql_guard.is_safe_select()`, executes if safe, and returns results — then add a "Run Edited Query" button in the frontend wired to this route. If behind schedule, skip this and move on — it was explicitly scoped as optional.
5. Redeploy and verify the SQL panel looks correct on the live URL.

### 📂 Files and folders to create or modify
```
frontend/
  app.js       (syntax highlighting, copy button, optional edit/run)
  style.css    (SQL panel styling)
backend/
  app.py       (optional /run-sql route, reuses sql_guard.py from Day 3)
```

### 🔗 APIs, libraries, services, or tools to integrate
- Browser `navigator.clipboard` API (built-in, no install).

### 🧪 Testing tasks
- Confirm SQL keywords are visually distinct for a complex query (join + aggregation).
- Click "Copy SQL" and paste elsewhere to confirm it copied correctly.
- If the edit/run stretch feature was built: test editing a query safely, and test that a destructive edit (e.g., adding a DELETE) is still blocked by `sql_guard.py`.

### 🐞 Common issues and debugging tips
- **Highlighting breaks on lowercase keywords**: make the keyword match case-insensitive but preserve the original casing in the output.
- **Clipboard API blocked**: some browsers require a secure context (HTTPS) — should be fine on Render's default HTTPS, but won't work over plain `http://localhost` in some setups; test on the deployed HTTPS URL if local fails.

### ✅ End-of-day checklist
- [ ] SQL panel is clearly formatted and readable.
- [ ] "Copy SQL" works.
- [ ] (If built) edited queries are still blocked from destructive operations.

### 📸 Expected project state and screenshots to capture
- Screenshot of a highlighted SQL query next to its results.

### ➡️ Handoff notes for Day 9
All three priority features (voice UX, complex queries, SQL transparency) are now built and polished. Day 9 is dedicated to full regression testing, bug fixing, and final UI polish — no new features.

---

## Day 9 — Full Testing & Bug Fixing Pass

### 🎯 Objective
Systematically test the entire app end-to-end, fix any bugs found, and do a final visual polish pass. No new features today — this is quality hardening before deployment day.

### 📖 What I'll learn
Structured manual QA for a full-stack app, and prioritizing bug fixes under limited remaining time.

### 🛠 Features to build
None — this is a testing and stabilization day.

### 📝 Step-by-step implementation plan
1. Re-run the full 8–10 demo question list from Day 6 end-to-end on the live deployed URL, timing each response.
2. Test edge cases: extremely short questions ("customers"), off-topic questions ("what's the weather"), and silence/no-speech.
3. Test on a fresh browser profile/incognito window to catch any state that accidentally depended on browser cache.
4. Review every screen for visual polish: consistent spacing, no overlapping elements, readable font sizes, mobile-reasonable layout (even though desktop is the target, it shouldn't look broken on a laptop trackpad resize).
5. Fix bugs in priority order: crashes > incorrect results on demo questions > visual polish > nice-to-haves.
6. Write `README.md`: project description, tech stack, how to run locally, link to the live demo, and the list of example questions to try.
7. Commit and push all fixes; redeploy final version.

### 📂 Files and folders to create or modify
```
README.md              (finalize)
(bug fixes across backend/ and frontend/ as needed)
```

### 🔗 APIs, libraries, services, or tools to integrate
None new.

### 🧪 Testing tasks
- Full regression pass on all 8–10 demo questions, live URL.
- Edge case testing (off-topic, silence, very short questions).
- Cross-check the app in a fresh incognito window.
- Full README read-through for clarity and typos.

### 🐞 Common issues and debugging tips
- **Works locally, fails live**: always diagnose against the deployed logs (Render's log viewer) rather than assuming — environment differences are the most common late-stage bug source.
- **Intermittent AI response variance**: if a demo question is sometimes right, sometimes wrong, add a firmer few-shot example for that exact pattern rather than leaving it to chance.

### ✅ End-of-day checklist
- [ ] All 8–10 demo questions work reliably on the live URL.
- [ ] No crashes on edge-case input.
- [ ] README is complete and accurate.
- [ ] All fixes committed and redeployed.

### 📸 Expected project state and screenshots to capture
- Screenshot of the final polished home/idle screen.
- Screenshot of README.md rendered on GitHub.

### ➡️ Handoff notes for Day 10
The product is feature-complete, tested, and stable. Day 10 is final deployment verification, demo preparation, and capstone submission — no code changes expected unless a last-minute bug appears.

---

## Day 10 — Final Deployment, Demo Prep & Submission

### 🎯 Objective
Confirm the live deployment is rock-solid, prepare a tight demo script, capture final screenshots/recording, and submit the completed capstone.

### 📖 What I'll learn
How to present a technical project confidently and concisely, and the discipline of a final pre-launch checklist.

### 🛠 Features to build
None — deployment verification and presentation prep only.

### 📝 Step-by-step implementation plan
1. Do one final full test of the live URL from a completely fresh device/browser if possible (or at minimum a fresh incognito window).
2. Prepare a 90–120 second demo script: 1 simple question, 1 filtered question, 1 complex join/aggregation question — using the curated list from Day 6.
3. Record a short screen-capture demo video (or prepare to demo live) as a backup in case live mic access is unreliable in a presentation setting.
4. Finalize the Pitch Deck talking points against the actual working product (swap any placeholder claims for what's actually true of the shipped v1.0).
5. Do a final review of the PRD's "Day 10 Definition of Success" section from Day 1 and confirm every bullet is met.
6. Push final code, confirm the GitHub repo is clean and the README is the front door to the project.
7. Submit the capstone per the AB Talks Challenge submission instructions.

### 📂 Files and folders to create or modify
None expected — verification and packaging only.

### 🔗 APIs, libraries, services, or tools to integrate
None new.

### 🧪 Testing tasks
- Full live demo run-through, timed, at least twice.
- Confirm the deployed URL is stable (no sleep/cold-start surprises — note Render free tier may cold-start after inactivity; do a warm-up request a few minutes before any live demo).

### 🐞 Common issues and debugging tips
- **Free-tier host cold start delay**: hit the live URL yourself 2–3 minutes before demoing so it's already "warm."
- **Mic doesn't work in a screen-share/presentation context**: have the pre-recorded video as a fallback.

### ✅ End-of-day checklist
- [ ] Live URL confirmed stable and warm.
- [ ] Demo script rehearsed at least twice.
- [ ] Backup video recorded.
- [ ] Pitch deck talking points match the real product.
- [ ] Capstone submitted.

### 📸 Expected project state and screenshots to capture
- Screenshot/recording of the full live demo flow, start to finish.
- Final screenshot of the deployed app's URL bar showing it's publicly live.

### ➡️ Handoff notes (post-capstone / maintenance)
v1.0 is shipped. Future scope (not part of this capstone, for reference only): support for user-uploaded custom databases, multi-turn conversational follow-ups, editable SQL as a first-class feature, and result visualizations/charts.
