# Day 7 Summary — VoiceSQL

**Date:** July 29-30, 2026
**Blueprint mapping:** Day 6 — Complex Query Handling & Prompt Hardening, plus an added Product/UX refinement pass

## Goals for Today
1. Expand `nl_to_sql.py`'s few-shot examples to handle more complex query patterns
2. Build `testing/test_questions.md` with a full test log
3. Curate the final demo question list
4. Fix the known float-rounding display bug
5. Senior-designer UI/UX polish pass across the whole app

## What Got Done

### 1. Prompt Hardening (`backend/nl_to_sql.py`)
- Expanded from 5 to 14 few-shot examples, adding coverage for:
  - 3-table joins with aggregation (category revenue)
  - Nested subqueries (average order value)
  - `HAVING`-style filters ("customers who placed more than N orders")
  - Named-entity joins ("what has customer X ordered")
  - Additional relative-date phrasings ("this year")
  - Simple count/filter combinations
- Added explicit rules to the system prompt: use `ORDER BY ... LIMIT 1` instead of bare `MAX()`/`MIN()`, use `GROUP BY ... HAVING` instead of `WHERE` on aggregates, and always wrap money calculations in `ROUND(..., 2)`
- Injected today's real date into the prompt so relative-date questions resolve correctly regardless of when the app is used

### 2. Float Rounding Fix
- Two-layer fix: `ROUND(..., 2)` added at the SQL generation level (primary fix) + a Python-side safety net in `backend/db.py` that rounds any float in query results before they're returned (backup, in case AI-generated SQL ever misses it)
- Verified: `₹914.8199999999999` → `₹914.82`

### 3. Test Questions Log (`testing/test_questions.md`)
- 15 test questions spanning simple lookups, filters, sorting, joins, aggregations, HAVING-filters, relative dates, named-entity joins, and an adversarial safety test
- **Result: 15 of 15 passing**, confirmed live against the running app
- Locked in an 8-question demo script for Day 10, covering a spread of difficulty without repeating patterns

### 4. UI/UX Polish Pass
Reviewed the app as a senior product/UX designer would, keeping the core teal identity and 6-state flow intact. Changes made:

- **Typography** — added a real type pairing (Space Grotesk for headline/display, Inter for body, IBM Plex Mono for the SQL panel) via Google Fonts, replacing plain system fonts
- **Signature micro-interaction** — replaced the generic pulsing-ring animation with small waveform bars around the mic button (breathing gently in idle, bouncing actively while listening) — a motif tied directly to the voice-input concept
- **New: Cancel while listening** — tapping the mic again during listening now stops recognition cleanly and returns to idle, instead of forcing the user to wait or get an error
- **New: stuck-state safety timeout** — if a query takes longer than 15 seconds, the app now fails gracefully with a clear message instead of leaving the spinner running indefinitely
- **Accessibility** — added `aria-live` region announcing every state change for screen readers, visible keyboard focus rings on all interactive elements, `prefers-reduced-motion` support, and real SVG icons (replacing emoji-style characters) for the empty and error states
- **Consistent number formatting** — all non-integer numeric results now display with exactly 2 decimal places, fixing an inconsistency where `2490.20` was rendering as `2490.2`
- **Empty/error state clarity** — empty state now explains that the SQL ran successfully but matched nothing (rather than implying something failed); error state uses a calmer icon and warmer, more legible red
- **Responsive tightening** — refined spacing rhythm and button wrapping on narrow screens

## Issues Encountered & Resolved
| Issue | Cause | Fix |
|---|---|---|
| "No results found" message displayed simultaneously with a valid results table | `.no-results-msg { display: flex }` in CSS silently overrode the browser's default `[hidden] { display: none }` behavior, since author styles beat user-agent styles regardless of source order | Added a higher-specificity `.no-results-msg[hidden] { display: none }` rule |

## Status at End of Day
✅ Prompt hardened — 15/15 test questions passing live
✅ Float rounding fixed at both the SQL and application layers
✅ Test log and locked demo question list documented
✅ Full UI/UX polish pass complete — typography, signature interaction, accessibility, empty/error states, responsive tightening
✅ CSS bug found during testing and fixed before deploy
✅ Deployed to Render and verified live at https://voicesql-pvh8.onrender.com

## Tomorrow's Focus (Conversational Day 8 → Blueprint Day 7)
Per the Blueprint offset, tomorrow moves into the next scheduled phase of the sprint — check the Blueprint's Day 7 section for the exact scope (expected to cover further feature/testing work ahead of the final documentation and submission days).
