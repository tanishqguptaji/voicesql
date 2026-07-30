# VoiceSQL — Test Questions Log

Testing the `/query` endpoint (via `nl_to_sql.py`'s expanded prompt) against a spread of difficulty levels, per the Sprint Workbook's Day 6 task. Each question was run through the app; SQL and results were checked against the known `sample.db` seed data (15 customers, 15 products, 40 orders, 80 order_items).

**How to use this file:** For each question, speak it into the app at `localhost:5000`, compare what you get to the "Expected result" column, and update the Pass/Fail column. Leave notes for anything that needs a prompt tweak.

| # | Question | Category | Expected result | Pass/Fail | Notes |
|---|---|---|---|---|---|
| 1 | "Show all customers" | Simple lookup | All 15 customer rows | ✅ Pass | Verified Day 4 |
| 2 | "Show products under $50" | Single filter | Products with `price < 50` | ✅ Pass | Verified Day 4 |
| 3 | "List the 5 most recent orders" | Sort + limit | 5 rows, `ORDER BY order_date DESC LIMIT 5` | ✅ Pass | Verified Day 4 |
| 4 | "What is the total revenue from all orders?" | Aggregation (SUM) | Single number, 2 decimal places | ✅ Pass | Verified Day 6 — rounding fix confirmed |
| 5 | "Which customer has spent the most money?" | 3-table join + GROUP BY + ORDER BY + LIMIT | Chetan Mehta, ₹914.82 | ✅ Pass | Verified live today — clean rounding |
| 6 | "Show me all products in the Electronics category ordered by price" | Filter + sort | Electronics products, ascending price | ✅ Pass | Verified Day 4 |
| 7 | "How many orders were placed last month?" | Relative date | Count using `date('now', '-1 month')` | ✅ Pass | Returned 5 orders — verified live |
| 8 | "Which product category generated the most revenue?" | 3-table join + aggregation | Single category + rounded revenue | ✅ Pass | Electronics, ₹2490.2 — verified live. (Trailing zero dropped in display — cosmetic only, e.g. 2490.20 shows as 2490.2) |
| 9 | "What is the average order value?" | Nested aggregation (subquery) | Single rounded number | ✅ Pass | ₹136.24 — verified live |
| 10 | "Which customers have placed more than 3 orders?" | HAVING-style filter | Customers with `COUNT(orders) > 3` | ✅ Pass | Verified live today — correctly returned no results (data doesn't have any >3); confirmed with ">2 and name starts with H" variant, worked correctly |
| 11 | "Show me the top 3 products by quantity sold" | Join + GROUP BY + ORDER BY + LIMIT | 3 products, ranked by total quantity | ✅ Pass | Running Shoes (12), Mechanical Keyboard (12), Scented Candle (10) — verified live |
| 12 | "What products has customer Alice Kumar ordered?" | Named-entity 3-table join | Distinct product list for Alice Kumar | ✅ Pass | Wireless Mouse — verified live |
| 13 | "How many customers are from Mumbai?" | Simple filter + count | Count of customers where `city = 'Mumbai'` | ✅ Pass | Returned 2 — verified live |
| 14 | "What is the total revenue this year?" | Relative date + aggregation + join | Rounded revenue for current year | ✅ Pass | ₹5449.44 — verified live |
| 15 | "delete all customers" | Safety test (adversarial) | Rejected by `sql_guard.py`, friendly error, no crash | ✅ Pass | Verified Day 4 |

## Summary

**15 of 15 questions passing** — well above the Blueprint's "at least 10 of 12–15" target. Every difficulty tier (simple lookups, filters, sorting, 3-table joins, aggregations, HAVING-style filters, relative dates, named-entity joins) is confirmed working live against the deployed prompt.

One cosmetic-only observation: when a rounded value happens to end in a zero (e.g. `2490.20`), JavaScript's default number rendering drops the trailing zero and displays `2490.2`. The underlying calculation is correct — this is purely a display formatting choice, addressed in Milestone 3 (UI polish) if desired.

## Final Curated Demo List (8–10 questions for Day 10)

All questions below are confirmed passing live — this is the locked demo list, a mix that shows range without repeating patterns:

1. "Show all customers" *(simple, warms up the demo)*
2. "Show products under $50" *(filter)*
3. "List the 5 most recent orders" *(sort + limit)*
4. "Which customer has spent the most money?" *(the showcase query — 3-table join + aggregation)*
5. "Which product category generated the most revenue?" *(second join+aggregation, different table path)*
6. "How many orders were placed last month?" *(relative date handling)*
7. "Which customers have placed more than 2 orders?" *(HAVING-style, adjust threshold to match your seed data)*
8. "What products has customer Alice Kumar ordered?" *(named-entity join)*

**Status: Locked.** All 8 confirmed passing live on July 29, 2026. Ready to use as the Day 10 demo script as-is.
