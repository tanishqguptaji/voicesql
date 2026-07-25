"""
sql_guard.py — Safety validator. Every AI-generated SQL string must pass
through is_safe_select() BEFORE it is ever executed against the database.

Per docs/API.md and docs/ARCHITECTURE.md: only single, read-only SELECT
statements are allowed. Anything else is rejected.
"""

import re

FORBIDDEN_KEYWORDS = [
    "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE",
    "TRUNCATE", "REPLACE", "ATTACH", "DETACH", "PRAGMA",
    "VACUUM", "REINDEX", "EXEC", "EXECUTE",
]


def is_safe_select(sql: str) -> bool:
    """Returns True only if sql is a single, read-only SELECT statement."""
    if not sql or not isinstance(sql, str):
        return False

    cleaned = sql.strip()

    # Strip a single trailing semicolon (allowed), but reject if anything
    # follows it (stacked statements like "SELECT ...; DROP TABLE ...").
    if ";" in cleaned:
        parts = [p.strip() for p in cleaned.split(";") if p.strip()]
        if len(parts) > 1:
            return False
        cleaned = parts[0] if parts else ""

    if not cleaned:
        return False

    # Must start with SELECT (case-insensitive).
    if not re.match(r"^\s*SELECT\b", cleaned, re.IGNORECASE):
        return False

    # Must not contain any forbidden keyword as a whole word, anywhere.
    upper = cleaned.upper()
    for keyword in FORBIDDEN_KEYWORDS:
        if re.search(rf"\b{keyword}\b", upper):
            return False

    return True


def clean_sql(raw: str) -> str:
    """Strips markdown code fences and extra whitespace from an AI response
    before it's checked by is_safe_select() or executed.
    """
    if not raw:
        return ""
    text = raw.strip()
    # Remove ```sql ... ``` or ``` ... ``` fences if present.
    text = re.sub(r"^```(?:sql)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()
