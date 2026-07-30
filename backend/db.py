"""
db.py — SQLite connection and query execution helper.

Per docs/ARCHITECTURE.md: this is the only file that talks directly to
sample.db. backend/app.py and backend/nl_to_sql.py should go through the
functions here rather than opening sqlite3 connections themselves.

Day 7 update: run_query() now rounds any float value in the result set to
2 decimal places as a safety net, in case the AI-generated SQL ever
forgets to wrap a money calculation in ROUND(...). The primary fix lives
in nl_to_sql.py's prompt; this is a backup so the UI never shows something
like 914.8199999999999 even if the prompt-level fix is bypassed.
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "database", "sample.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # lets us return rows as dictionaries
    return conn


def _round_floats(row: dict) -> dict:
    """Rounds any float value in a result row to 2 decimal places."""
    return {
        key: (round(value, 2) if isinstance(value, float) else value)
        for key, value in row.items()
    }


def run_query(sql: str):
    """Executes a SQL string and returns rows as a list of dicts.
    Safety validation (SELECT-only) happens in sql_guard.py, BEFORE
    this function is called — this function assumes the SQL is already safe.
    Any float values in the results are rounded to 2 decimal places.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        return [_round_floats(dict(row)) for row in rows]
    finally:
        conn.close()


def check_connection():
    """Used by /health to confirm the database file exists and is reachable."""
    try:
        conn = get_connection()
        conn.execute("SELECT 1")
        conn.close()
        return True
    except Exception:
        return False
