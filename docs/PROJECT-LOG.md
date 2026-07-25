# VoiceSQL — Project Log

## Day 1 — Product Discovery & Sprint Planning
- Interviewed to select the project: VoiceSQL, a browser-based voice-to-SQL assistant.
- Defined v1.0 scope, what's explicitly out of scope, and the Day 10 definition of success.
- Generated PRD, 9-day Implementation Blueprint, and Pitch Deck.

## Day 2 — System Design
- Created the GitHub repository (`tanishqguptaji/voicesql`), cloned it locally, and set up the initial folder structure: `backend/`, `database/`, `frontend/`, `docs/`, `testing/`.
- Finalized the tech stack: Flask backend, SQLite database, Web Speech API for voice, Claude API for NL→SQL translation, Render for hosting, no authentication in v1.0.
- Designed the full system architecture (component diagram, request lifecycle, AI interaction flow) — documented in `docs/ARCHITECTURE.md`.
- Designed the database schema (4 tables: customers, products, orders, order_items) and validated it against every user story in the PRD — documented in `docs/SCHEMA.md`.
- Specified every v1.0 API endpoint (`/health`, `/`, `/query`, and the optional `/run-sql` stretch endpoint) including request/response shapes, validation rules, and error cases — documented in `docs/API.md`.
- Designed the complete UI state machine (idle → listening → confirm → processing → results/error) with low-fidelity wireframes — documented in `docs/UI-WIREFRAMES.md`.
- Documented the full project folder structure and the reasoning behind it — `docs/PROJECT-STRUCTURE.md`.
- Confirmed Day 3 readiness: no scope creep, no open design decisions, implementation can begin immediately tomorrow.
- Committed and pushed all Day 2 deliverables to GitHub.

**Status:** On track. No blockers. Tech stack and full technical design locked — Day 3 begins implementation with zero remaining ambiguity.

## Day 3 — Project Setup & Foundation
- Set up Python virtual environment, installed all backend dependencies (Flask, Anthropic SDK, python-dotenv, gunicorn).
- Obtained Anthropic API key, configured .env, verified .gitignore protects it.
- Built database/build_db.py implementing the Day 2 schema exactly — seeded 15 customers, 15 products, 40 orders, 80 order_items.
- Built backend/db.py (connection + query helper) and backend/schema.py (AI prompt schema text).
- Built backend/app.py with / (static frontend serving) and /health (server + DB + API key check) routes.
- Built placeholder frontend (index.html, style.css, app.js) that verifies live backend connectivity.
- Verified full stack running locally with zero errors — foundation confirmed ready for feature development.
- Noted a one-day offset in the Blueprint's day numbering (Day 2 became a design day; today completed the original "Day 2 — Setup" content) — no scope or time lost.

**Status:** On track. Foundation complete. Tomorrow begins the first real feature: the /query NL-to-SQL endpoint.
