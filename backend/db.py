"""
db.py — SQLite connection and query execution helper.

Day 8 hardening pass: added a hard cap on rows returned (MAX_ROWS), so
even if the AI ever generates a query without a LIMIT clause on a much
larger dataset than today's sample data, the app can't return an
unbounded result set.
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "database", "sample.db")

MAX_ROWS = 500


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
    Results are capped at MAX_ROWS as a defensive safety net.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchmany(MAX_ROWS)
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