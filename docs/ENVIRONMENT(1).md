# VoiceSQL — Environment & Configuration Reference

## Environment Variables

| Variable | Where set | Required | Purpose |
|---|---|---|---|
| `GROQ_API_KEY` | `.env` (local), Render dashboard (deployed) | Yes | Authenticates calls to the Groq API for NL → SQL translation (used starting Day 4) |

`.env` lives at the project root (`voicesql/.env`), is loaded by `python-dotenv` in `backend/app.py`, and is excluded from Git via `.gitignore`. It is never committed and never shared in screenshots.

When deployed to Render (Day 10), the same variable is set directly in Render's dashboard under Environment rather than in a file — Render injects it into the running process automatically.

## Tools & Runtimes

| Tool | Version used | Why it's needed |
|---|---|---|
| Python | 3.11.9 | Runs the Flask backend and the database build script |
| pip | bundled with Python | Installs backend dependencies |
| Git | (as installed) | Version control, connects local project to GitHub |
| VS Code | latest | Code editor, integrated terminal |
| VS Code Python extension | latest (Microsoft) | Syntax highlighting, linting, run/debug support for `.py` files |

## Python Packages (`backend/requirements.txt`)

| Package | Version | Purpose |
|---|---|---|
| flask | 3.0.3 | Web framework — serves the frontend and the `/health`, `/query` (Day 4), `/run-sql` (optional, Day 8) endpoints |
| python-dotenv | 1.0.1 | Loads `GROQ_API_KEY` from `.env` into the environment |
| groq | 0.11.0 | Official SDK for calling the Groq API (used starting Day 4) |
| httpx | 0.27.2 | Pinned for SDK compatibility (newer httpx versions break groq 0.11.0) |
| gunicorn | 22.0.0 | Production WSGI server, used only when deployed to Render — not used in local development (`python backend/app.py` uses Flask's built-in dev server instead) |

## Configuration Files

| File | Purpose |
|---|---|
| `.env` | Holds `GROQ_API_KEY` locally. Gitignored. |
| `.gitignore` | Excludes `.env`, `venv/`, `__pycache__/`, and other Python build artifacts from Git — created by GitHub's Python template on repo init, verified Day 3 to include `.env` |
| `backend/requirements.txt` | Pinned dependency versions for reproducible installs |
| `backend/schema.py` | Not a config file in the traditional sense, but functions as one: it's the single source of truth for what schema text gets sent to Groq in every AI prompt. Must stay in sync with `database/build_db.py` and `docs/SCHEMA.md`. |

## Local vs. Deployed Differences

| Aspect | Local (Day 3–9) | Deployed (Render, Day 10) |
|---|---|---|
| Server | Flask dev server (`python backend/app.py`) | gunicorn (`gunicorn backend.app:app`) |
| API key source | `.env` file | Render dashboard environment variable |
| URL | `http://127.0.0.1:5000` | Public Render URL |
| Debug mode | On (`debug=True`) | Off (never enable debug mode in production) |
