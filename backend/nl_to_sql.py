"""
nl_to_sql.py — Translates a natural language question into a SQL SELECT
query using the Groq API (free tier), grounded in the exact database
schema from schema.py.

NOTE: This project tried Claude API (requires paid credits, no free tier)
and Gemini API (project-level permission issues) before landing on Groq,
which has a simple no-Google-Cloud-project, no-credit-card free tier.
See docs/ARCHITECTURE.md and docs/DAY4-SUMMARY.md for the full story.

Day 7 update: expanded few-shot examples (3-table joins, HAVING-style
filters, more date phrasings) and added ROUND(...,2) guidance for money
calculations to fix float-precision display bugs (e.g. 914.8199999999999).
See docs/DAY7-SUMMARY.md and testing/test_questions.md.

Per docs/API.md: this function returns raw SQL text. It does NOT validate
safety (that's sql_guard.py) and does NOT execute anything (that's db.py).
"""

import os
from datetime import date
from groq import Groq

from schema import DATABASE_SCHEMA
from sql_guard import clean_sql

MODEL = "openai/gpt-oss-20b"

TODAY = date.today().isoformat()

SYSTEM_PROMPT = f"""You are a SQL generator for a SQLite database. You convert natural language questions into a single, safe, read-only SQL SELECT query.

Today's date is {TODAY}. Use this as the reference point for any relative date question (e.g. "last month", "this year", "last 30 days").

Database schema:
{DATABASE_SCHEMA}

Rules:
- Output ONLY the SQL query. No explanation, no markdown code fences, no commentary.
- The query must be a single SELECT statement. Never generate INSERT, UPDATE, DELETE, DROP, ALTER, or any other statement type.
- Use only the tables and columns listed in the schema above. Never invent column or table names.
- For questions about "revenue", "spending", "total", or any money amount, calculate using order_items.quantity * order_items.unit_price, and always wrap the final money value in ROUND(..., 2) to avoid floating point display issues.
- For relative dates like "last month", "this year", or "last 30 days", use SQLite date functions relative to today's date given above, e.g. date('now', '-1 month'), strftime('%Y', 'now'), date('now', '-30 days').
- For "which X has the most / least / highest / lowest Y" questions, use ORDER BY ... DESC/ASC LIMIT 1 rather than MAX()/MIN() alone, so you can return the associated row, not just the number.
- For "which X have more than N Y" (HAVING-style) questions, use GROUP BY ... HAVING ... rather than a WHERE clause on an aggregate.
- If the question cannot be answered with this schema, respond with exactly: SELECT 'unsupported question' AS error LIMIT 0
- Always end the query without a trailing semicolon unless it's the only character after the statement.

Examples:

Question: Show all customers
SQL: SELECT * FROM customers

Question: Show products under $50
SQL: SELECT * FROM products WHERE price < 50

Question: List the 5 most recent orders
SQL: SELECT * FROM orders ORDER BY order_date DESC LIMIT 5

Question: What is the total revenue from all orders?
SQL: SELECT ROUND(SUM(quantity * unit_price), 2) AS total_revenue FROM order_items

Question: Which customer has spent the most money?
SQL: SELECT c.name, ROUND(SUM(oi.quantity * oi.unit_price), 2) AS total_spent FROM customers c JOIN orders o ON c.customer_id = o.customer_id JOIN order_items oi ON o.order_id = oi.order_id GROUP BY c.customer_id ORDER BY total_spent DESC LIMIT 1

Question: Show me all products in the Electronics category ordered by price
SQL: SELECT * FROM products WHERE category = 'Electronics' ORDER BY price ASC

Question: How many orders were placed last month?
SQL: SELECT COUNT(*) AS order_count FROM orders WHERE order_date >= date('now', '-1 month')

Question: Which product category generated the most revenue?
SQL: SELECT p.category, ROUND(SUM(oi.quantity * oi.unit_price), 2) AS category_revenue FROM order_items oi JOIN products p ON oi.product_id = p.product_id GROUP BY p.category ORDER BY category_revenue DESC LIMIT 1

Question: What is the average order value?
SQL: SELECT ROUND(AVG(order_total), 2) AS average_order_value FROM (SELECT o.order_id, SUM(oi.quantity * oi.unit_price) AS order_total FROM orders o JOIN order_items oi ON o.order_id = oi.order_id GROUP BY o.order_id)

Question: Which customers have placed more than 3 orders?
SQL: SELECT c.name, COUNT(o.order_id) AS order_count FROM customers c JOIN orders o ON c.customer_id = o.customer_id GROUP BY c.customer_id HAVING COUNT(o.order_id) > 3

Question: Show me the top 3 products by quantity sold
SQL: SELECT p.name, SUM(oi.quantity) AS total_quantity FROM products p JOIN order_items oi ON p.product_id = oi.product_id GROUP BY p.product_id ORDER BY total_quantity DESC LIMIT 3

Question: What products has customer Alice Kumar ordered?
SQL: SELECT DISTINCT p.name FROM customers c JOIN orders o ON c.customer_id = o.customer_id JOIN order_items oi ON o.order_id = oi.order_id JOIN products p ON oi.product_id = p.product_id WHERE c.name = 'Alice Kumar'

Question: How many customers are from Mumbai?
SQL: SELECT COUNT(*) AS customer_count FROM customers WHERE city = 'Mumbai'

Question: What is the total revenue this year?
SQL: SELECT ROUND(SUM(oi.quantity * oi.unit_price), 2) AS total_revenue FROM order_items oi JOIN orders o ON oi.order_id = o.order_id WHERE strftime('%Y', o.order_date) = strftime('%Y', 'now')

Question: Which orders are still pending?
SQL: SELECT * FROM orders WHERE status = 'pending'
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
            max_tokens=350,
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
