# VoiceSQL — Project Structure

Status: Finalized Day 2. Folders `backend/`, `database/`, `frontend/`, `docs/`, `testing/` already exist locally (created Day 2). This document is the map for where every future file goes.

```
voicesql/
├── backend/
│   ├── app.py               # ✅ Built Day 3 — Flask app: /, /health today; /query, /run-sql added Day 4/8
│   ├── schema.py             # ✅ Built Day 3 — DB schema string, fed into every AI prompt
│   ├── nl_to_sql.py           # ⏳ Day 4 — Claude API call + system prompt (few-shot examples added Day 6)
│   ├── sql_guard.py           # ⏳ Day 4 — SELECT-only safety validator, reused by /query and /run-sql
│   ├── db.py                 # ✅ Built Day 3 — sqlite3 connection + query execution helper
│   └── requirements.txt       # ✅ Built Day 3 — flask, anthropic, python-dotenv, gunicorn
├── database/
│   ├── build_db.py            # ✅ Built Day 3 — creates and seeds sample.db
│   └── sample.db              # ✅ Generated Day 3 — 15 customers, 15 products, 40 orders, 80 order_items
├── frontend/
│   ├── index.html            # ✅ Placeholder Day 3 — full 6-state UI built Day 4
│   ├── style.css              # ✅ Placeholder Day 3 — full layout/animations built Day 4/7
│   └── app.js                # ✅ Placeholder Day 3 (health check only) — voice + fetch logic built Day 4/5
├── docs/
│   ├── ARCHITECTURE.md        # Day 2
│   ├── SCHEMA.md              # Day 2
│   ├── API.md                 # Day 2
│   ├── UI-WIREFRAMES.md       # Day 2
│   ├── PROJECT-STRUCTURE.md    # This document
│   ├── SETUP.md               # ✅ Built Day 3 — install/run instructions
│   ├── ENVIRONMENT.md          # ✅ Built Day 3 — env vars, tools, config reference
│   ├── DAY3-SUMMARY.md         # ✅ Built Day 3
│   └── PROJECT-LOG.md          # Running daily log, updated at the end of each day
├── testing/
│   └── test_questions.md      # ⏳ Day 6 — test question log + final curated demo question list
├── venv/                     # ✅ Created Day 3 — local virtual environment, gitignored
├── .env                      # ✅ Created Day 3 — local only, gitignored — holds ANTHROPIC_API_KEY
├── .gitignore                 # Created by GitHub on repo init (Python template); verified Day 3 to exclude .env, venv/
└── README.md                  # ⏳ Finalized Day 9
```

## Folder Responsibilities

**`backend/`** — everything server-side: the Flask app, the AI translation call, the safety guard, and DB access. This is where Day 3 (core backend) and Day 6 (prompt hardening) work happens. Nothing in here should know about HTML/CSS — it only speaks JSON.

**`database/`** — owns the data layer. `build_db.py` is a one-time (or re-runnable) script; `sample.db` is the actual data file the backend reads from. Kept separate from `backend/` so the data layer could theoretically be swapped (e.g., a different sample dataset) without touching backend logic.

**`frontend/`** — everything the browser loads: one HTML file, one stylesheet, one script. No build step, no framework — served directly as static files by Flask. This is where Day 4 (UI + voice), Day 5 (integration), Day 7 (voice polish), and Day 8 (SQL panel polish) happen.

**`docs/`** — the planning and documentation trail, including this file. `PROJECT-LOG.md` gets a new entry at the end of every remaining day, so the repo tells the full story of the build for anyone (recruiter, reviewer) who opens it.

**`testing/`** — QA artifacts, primarily the Day 6 test question log, which doubles as the source for the Day 10 demo script. Keeping this separate from `docs/` distinguishes "how we tested it" from "how we designed it."

**Root files** — `.env` never gets committed (holds the API key); `.gitignore` already excludes it via the Python template GitHub provided; `README.md` is the front door and gets finalized on Day 9 once the product is stable enough to describe accurately.

## Why This Structure

It mirrors the architecture diagram's layers exactly — `frontend` = client, `backend` = server + AI + safety, `database` = data — so anyone (including a fresh AI conversation starting a future day) can map any Blueprint day's tasks onto a folder without ambiguity. Nothing needs to be reorganized as the project grows through Day 10; every file introduced in later days has an obvious home already defined here.
