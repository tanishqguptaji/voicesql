"""
db.py — SQLite connection and query execution helper.

Per docs/ARCHITECTURE.md: this is the only file that talks directly to
sample.db. backend/app.py and future backend/nl_to_sql.py should go
through the functions here rather than opening sqlite3 connections
themselves.
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "database", "sample.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # lets us return rows as dictionaries
    return conn


def run_query(sql: str):
    """Executes a SQL string and returns rows as a list of dicts.
    Safety validation (SELECT-only) happens in sql_guard.py, BEFORE
    this function is called — this function assumes the SQL is already safe.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        return [dict(row) for row in rows]
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
