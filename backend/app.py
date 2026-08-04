"""
app.py — VoiceSQL Flask backend.

Day 8 hardening pass (per Sprint Workbook "Testing, Debugging &
Production Optimization"): added a top-level exception handler so /query
always returns JSON even on unexpected failures, request body size cap,
input type validation, and debug mode gated behind an environment
variable so it can never accidentally run in production.

Error handling follows docs/API.md: every failure returns JSON with a
single "error" field and the status codes specified there.
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

# Reject request bodies over 10KB — a spoken question will never be
# remotely close to this size, so this only exists to block abuse.
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024

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
    try:
        body = request.get_json(silent=True) or {}
        question = body.get("question")

        # Validation — per docs/API.md
        if not isinstance(question, str) or not question.strip():
            return jsonify({"error": "Please ask a question."}), 400

        question = question.strip()
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

    except Exception as e:
        # Last-resort catch-all so the frontend always gets JSON back,
        # never an HTML error page it can't parse.
        app.logger.error(f"Unexpected error in /query: {type(e).__name__}")
        return jsonify({"error": "Something went wrong on our end. Please try again."}), 500


@app.errorhandler(413)
def request_too_large(e):
    return jsonify({"error": "Request too large."}), 413


@app.errorhandler(404)
def not_found(e):
    # Only affects unmatched API-style routes; static files are served
    # by Flask's static handler before this ever fires.
    return jsonify({"error": "Not found."}), 404


if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(debug=debug_mode, port=5000)