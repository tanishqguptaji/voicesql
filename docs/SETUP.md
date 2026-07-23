# VoiceSQL — Setup Guide

Follow this guide to get the project running locally from a clean clone.

## Prerequisites

- **Python 3.9+** (tested with 3.11.9)
- **Git**
- **VS Code** (recommended, with the Microsoft Python extension)
- An **Anthropic API key** (from https://console.anthropic.com — free to sign up)

## 1. Clone the repository

```
git clone https://github.com/tanishqguptaji/voicesql.git
cd voicesql
```

## 2. Create and activate a virtual environment

**Windows (PowerShell):**
```
python -m venv venv
.\venv\Scripts\Activate.ps1
```
If activation is blocked by a script execution policy error, run once:
```
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

**Mac/Linux:**
```
python3 -m venv venv
source venv/bin/activate
```

You'll know it worked when your terminal prompt starts with `(venv)`.

## 3. Install dependencies

```
pip install -r backend/requirements.txt
```

This installs Flask, the Anthropic SDK, python-dotenv, and gunicorn.

## 4. Configure your API key

1. Create a file named `.env` in the project root (`voicesql/.env`).
2. Add this line, replacing with your real key:
   ```
   ANTHROPIC_API_KEY=sk-ant-your-real-key-here
   ```
3. This file is already excluded by `.gitignore` — never commit it.

## 5. Build the sample database

```
python database/build_db.py
```
This creates `database/sample.db` with 15 customers, 15 products, 40 orders, and 80 order items, per `docs/SCHEMA.md`.

## 6. Run the app

```
python backend/app.py
```
The server starts on `http://127.0.0.1:5000`.

## 7. Verify it's working

- Visit `http://127.0.0.1:5000` — you should see the VoiceSQL page with a live backend health message.
- Visit `http://127.0.0.1:5000/health` — you should see:
  ```json
  { "status": "ok", "database": "connected", "anthropic_api_key_configured": true }
  ```

If `database` shows `"unreachable"`, re-run step 5. If `anthropic_api_key_configured` shows `false`, check your `.env` file is saved in the project root with the exact variable name `ANTHROPIC_API_KEY`.

## Troubleshooting

| Problem | Fix |
|---|---|
| `python` not recognized | Try `py` instead, or reinstall Python with "Add to PATH" checked |
| `venv` creation fails with a permission error | Delete the partial `venv` folder (`Remove-Item -Recurse -Force venv`) and retry — don't interrupt the command mid-run |
| PowerShell blocks `Activate.ps1` | Run `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned` once |
| `ModuleNotFoundError` for flask/anthropic/etc. | Confirm `(venv)` is active, then re-run `pip install -r backend/requirements.txt` |
| Port 5000 already in use | Stop any other running Flask process, or change the port in `backend/app.py`'s `app.run()` call |
