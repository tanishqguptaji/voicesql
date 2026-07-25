"""
app.py — VoiceSQL Flask backend.

Day 4 scope (per Blueprint "Day 3 — Core Backend"):
  - / and /health (built Day 3, unchanged)
  - /query: the core NL -> SQL -> results endpoint, tested today via
    curl/Postman. UI wiring happens tomorrow.

Error handling follows docs/API.md exactly: every failure returns
JSON with a single "error" field and the status codes specified there.
"""

import os
from flask import Flask, jsonify, request, send_from_directory
from dotenv import load_dotenv

import db
from nl_to_sql import translate, NLToSQLError
from sql_guard import is_safe_select

load_dotenv()

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")

MAX_QUESTION_LENGTH = 500


@app.route("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/health")
def health():
    db_ok = db.check_connection()
    api_key_present = bool(os.getenv("GROQ_API_KEY"))
    return jsonify({
        "status": "ok" if db_ok else "degraded",
        "database": "connected" if db_ok else "unreachable",
        "groq_api_key_configured": api_key_present,
    })


@app.route("/query", methods=["POST"])
def query():
    body = request.get_json(silent=True) or {}
    question = (body.get("question") or "").strip()

    # Validation — per docs/API.md
    if not question:
        return jsonify({"error": "Please ask a question."}), 400
    if len(question) > MAX_QUESTION_LENGTH:
        return jsonify({"error": "That question is too long, try rephrasing more briefly."}), 400

    # AI translation
    try:
        sql = translate(question)
    except NLToSQLError:
        return jsonify({"error": "AI service temporarily unavailable, try again."}), 503

    # Safety validation
    if not is_safe_select(sql):
        return jsonify({"error": "Couldn't safely process that question."}), 400

    # Execution
    try:
        results = db.run_query(sql)
    except Exception:
        return jsonify({"error": "Couldn't understand that question, try rephrasing."}), 422

    return jsonify({"sql": sql, "results": results}), 200


if __name__ == "__main__":
    app.run(debug=True, port=5000)
