"""
app.py — VoiceSQL Flask backend.

Day 3 scope (foundation only, per the Blueprint):
  - Serve the frontend as static files
  - /health route, confirming both the server AND the database are reachable
  - Load environment variables (ANTHROPIC_API_KEY) so tomorrow's
    nl_to_sql.py can use them without any extra setup

The /query route (NL -> SQL translation) is built Day 4, not today.
"""

import os
from flask import Flask, jsonify, send_from_directory
from dotenv import load_dotenv

import db

# Load variables from .env into the environment (e.g. ANTHROPIC_API_KEY)
load_dotenv()

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")


@app.route("/")
def index():
    """Serves the frontend's index.html."""
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/health")
def health():
    """Liveness check. Confirms the server is up AND the database is reachable."""
    db_ok = db.check_connection()
    api_key_present = bool(os.getenv("ANTHROPIC_API_KEY"))
    return jsonify({
        "status": "ok" if db_ok else "degraded",
        "database": "connected" if db_ok else "unreachable",
        "anthropic_api_key_configured": api_key_present,
    })


if __name__ == "__main__":
    # Local development only. Render will use gunicorn in production (Day 2 architecture).
    app.run(debug=True, port=5000)
