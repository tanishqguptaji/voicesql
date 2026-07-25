# VoiceSQL — System Architecture

Status: Finalized Day 2, **AI provider updated Day 4** (Claude → Groq, see `DAY4-SUMMARY.md` for why). This is the source of truth for how components interact. Do not change without re-approval.

## Component Diagram

```mermaid
graph TB
    U[User: Browser / Chrome] -->|1. Speaks| WSA[Web Speech API]
    WSA -->|2. Transcript text| FE[Frontend: index.html / app.js]
    FE -->|3. POST /query| BE[Flask Backend]
    BE -->|4. question + schema| GROQ[Groq API]
    GROQ -->|5. SQL text| BE
    BE -->|6. validate SELECT-only| GUARD[sql_guard.py]
    GUARD -->|7. safe SQL| DB[(SQLite: sample.db)]
    DB -->|8. rows| BE
    BE -->|9. JSON: sql + results| FE
    FE -->|10. renders table + SQL panel| U
```

## Request Lifecycle (Sequence)

```mermaid
sequenceDiagram
    participant User
    participant Browser as Browser (Web Speech API)
    participant FE as Frontend (app.js)
    participant BE as Flask /query
    participant AI as Groq API
    participant DB as SQLite

    User->>Browser: Click mic, speak question
    Browser->>FE: onresult (transcript)
    FE->>User: Show transcript, "Ask This?" confirm
    User->>FE: Confirms
    FE->>BE: POST /query {question}
    BE->>AI: schema + question
    AI-->>BE: SQL string
    BE->>BE: sql_guard.is_safe_select()
    alt unsafe or invalid
        BE-->>FE: 400 { error: "..." }
        FE-->>User: Friendly error message
    else safe SELECT
        BE->>DB: execute SQL
        DB-->>BE: rows
        BE-->>FE: 200 { sql, results }
        FE-->>User: Results table + SQL panel
    end
```

## User Flow / State Machine

```mermaid
flowchart TD
    A[Idle: Mic button visible] -->|Click mic| B[Listening: pulsing animation]
    B -->|Speech captured| C[Confirm: show transcript]
    C -->|"Try Again"| B
    C -->|"Ask This"| D[Processing: loading state]
    D -->|Success| E[Results: table + SQL panel]
    D -->|Error| F[Error message shown inline]
    E -->|"Ask Another Question"| A
    F -->|"Try Again"| A
```

## Data Flow Summary

- **Client-side only:** voice capture and transcription via the Web Speech API. No audio data ever leaves the browser — only the transcribed text is sent to the backend.
- **Server-side:** the Flask backend receives text (the question), sends text to Groq (question + schema), receives text back (the SQL), validates it, and executes it locally against SQLite.
- **External services:** the Groq API is the only external network call in the entire request lifecycle. There are no other third-party services, no analytics, and no authentication providers in v1.0.

## AI Interaction

- Every `/query` call sends the **full database schema** (from `backend/schema.py`) alongside the user's question, so the AI model always has ground-truth table/column names.
- The system prompt instructs the model to return **only** a single SQL `SELECT` statement, no explanation, no markdown fences.
- The response is passed through `sql_guard.py` before ever touching the database — this is a hard boundary, not a suggestion. Any non-`SELECT` statement, or a `SELECT` containing a stacked statement, is rejected before execution.
- **Provider:** Groq API, model `openai/gpt-oss-20b`. Originally planned as the Claude API (Day 2), changed on Day 4 after hitting a hard paywall on Anthropic's API (no free tier) and persistent account-level permission issues on Google's Gemini API. See `docs/DAY4-SUMMARY.md` for the full troubleshooting history.

## External Services

| Service | Purpose | Data sent | Data received |
|---|---|---|---|
| Groq API | NL → SQL translation | Question text + schema text | SQL text only |
| Render (hosting) | Runs the Flask app publicly | N/A (infrastructure) | N/A |

No other external services are used in v1.0 (no analytics, no auth provider, no external database).
