"""
nl_to_sql.py — Translates a natural language question into a SQL SELECT
query using the Groq API (free tier), grounded in the exact database
schema from schema.py.

NOTE: This project tried Claude API (requires paid credits, no free tier)
and Gemini API (project-level permission issues) before landing on Groq,
which has a simple no-Google-Cloud-project, no-credit-card free tier.
See docs/ARCHITECTURE.md and docs/DAY4-SUMMARY.md for the full story.

Per docs/API.md: this function returns raw SQL text. It does NOT validate
safety (that's sql_guard.py) and does NOT execute anything (that's db.py).
"""

import os
from groq import Groq

from schema import DATABASE_SCHEMA
from sql_guard import clean_sql

MODEL = "openai/gpt-oss-20b"

SYSTEM_PROMPT = f"""You are a SQL generator for a SQLite database. You convert natural language questions into a single, safe, read-only SQL SELECT query.

Database schema:
{DATABASE_SCHEMA}

Rules:
- Output ONLY the SQL query. No explanation, no markdown code fences, no commentary.
- The query must be a single SELECT statement. Never generate INSERT, UPDATE, DELETE, DROP, ALTER, or any other statement type.
- Use only the tables and columns listed in the schema above. Never invent column or table names.
- For questions about "revenue", "spending", or "total", calculate using order_items.quantity * order_items.unit_price.
- For relative dates like "last month" or "this year", use SQLite date functions such as date('now', '-1 month') or strftime('%Y', 'now').
- If the question cannot be answered with this schema, respond with exactly: SELECT 'unsupported question' AS error LIMIT 0
- Always end the query without a trailing semicolon unless it's the only character after the statement.

Examples:

Question: Show all customers
SQL: SELECT * FROM customers

Question: What is the total revenue from all orders?
SQL: SELECT SUM(quantity * unit_price) AS total_revenue FROM order_items

Question: Which customer has spent the most money?
SQL: SELECT c.name, SUM(oi.quantity * oi.unit_price) AS total_spent FROM customers c JOIN orders o ON c.customer_id = o.customer_id JOIN order_items oi ON o.order_id = oi.order_id GROUP BY c.customer_id ORDER BY total_spent DESC LIMIT 1

Question: How many orders were placed last month?
SQL: SELECT COUNT(*) AS order_count FROM orders WHERE order_date >= date('now', '-1 month')

Question: Which product category generated the most revenue?
SQL: SELECT p.category, SUM(oi.quantity * oi.unit_price) AS category_revenue FROM order_items oi JOIN products p ON oi.product_id = p.product_id GROUP BY p.category ORDER BY category_revenue DESC LIMIT 1
"""

_client_cache = None


class NLToSQLError(Exception):
    """Raised when the Groq API call itself fails (network, auth, quota, timeout)."""
    pass


def _get_client():
    global _client_cache
    if _client_cache is not None:
        return _client_cache

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise NLToSQLError("GROQ_API_KEY is not configured.")

    _client_cache = Groq(api_key=api_key)
    return _client_cache


def translate(question: str) -> str:
    """Sends the question to Groq and returns a cleaned SQL string.
    Raises NLToSQLError if the API call fails.
    """
    client = _get_client()

    try:
        response = client.chat.completions.create(
            model=MODEL,
            max_tokens=300,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": question},
            ],
        )
    except Exception as e:
        print(f"[DEBUG] Groq API call failed: {e}")
        raise NLToSQLError(f"Groq API call failed: {e}")

    raw_text = response.choices[0].message.content or ""
    return clean_sql(raw_text)
