# Day 6 Summary — VoiceSQL

**Date:** July 28, 2026
**Blueprint mapping:** Day 5 — Integration & Deployment

## Goals for Today
1. Wire the real Flask backend (Groq) into the frontend, replacing Day 5's mock data
2. Add the required challenge footer
3. Deploy the app publicly on Render

## What Got Done

### 1. Real Backend Integration
- `frontend/app.js` updated to call `fetch('/query')` instead of returning mock data
- Verified in real Chrome: two different spoken questions returned two genuinely different, correct results
- Confirmed the full 6-state UI flow (idle → listening → confirm → processing → results) works against the live backend, not just mocked transitions

### 2. Footer Requirement
- Added to `frontend/index.html`: *"Built with Claude as part of the AB Talks 60-Day Claude AI Challenge."*
- Verified present both locally (Flask test client) and on the deployed Render URL

### 3. Deployment to Render
- Created Render account (GitHub OAuth), new Web Service `voicesql` connected to the GitHub repo, `main` branch, free instance tier
- Added `Procfile` (`web: gunicorn --chdir backend app:app`), tested locally with gunicorn before pushing
- **Hit a deploy failure:** Render defaulted to `pip install -r requirements.txt` instead of the custom build command, causing `Could not open requirements file: No such file or directory: 'requirements.txt'` (the file actually lives at `backend/requirements.txt`)
- **Fix:** manually set in Settings:
  - Build Command: `pip install -r backend/requirements.txt`
  - Start Command: `gunicorn --chdir backend app:app`
- Triggered a Manual Deploy → succeeded, service went **Live**
- Confirmed `GROQ_API_KEY` environment variable persisted correctly from initial setup

### 4. Live Verification
- **Live URL:** https://voicesql-pvh8.onrender.com
- `/health` returns: `{"status": "ok", "database": "connected", "groq_api_key_configured": true}`
- Full voice → SQL → results flow tested live: "show me the first 10 customers" returned correct data, correct generated SQL (`SELECT * FROM customers LIMIT 10`) shown in the "Show SQL" panel with syntax highlighting
- Footer confirmed visible on the deployed version

## Issues Encountered & Resolved
| Issue | Cause | Fix |
|---|---|---|
| Render build failed: `requirements.txt` not found | Render used default build command, ignoring the custom one set during initial Configure step | Manually re-set Build Command in Settings, redeployed |

## Known Minor Issues (not blocking, tracked for later)
- Currency values sometimes display float precision artifacts (e.g. `914.8199999999999` instead of `914.82`) — cosmetic only, fix planned during Day 7 prompt-hardening pass (round in SQL or format client-side)
- Free Render instance spins down when idle; first request after inactivity takes ~30-50s to wake — acceptable for a portfolio demo, worth a one-line note in the README/demo script

## Status at End of Day
✅ Backend fully integrated with frontend
✅ Footer added and verified
✅ Deployed live on Render, publicly accessible
✅ End-to-end flow verified on the live URL with real voice input

## Tomorrow's Focus (Conversational Day 7 → Blueprint Day 6: Complex Query Handling & Prompt Hardening)
- Expand `nl_to_sql.py` few-shot examples to cover more query patterns
- Build `testing/test_questions.md` with 12-15 test questions spanning simple lookups, aggregations, joins, relative dates, and edge cases
- Curate the final 8-10 question list for live demo/recording
- Fix the float-rounding display issue for currency values
