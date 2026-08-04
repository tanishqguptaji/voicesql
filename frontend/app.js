// app.js — VoiceSQL frontend state machine.
//
// Day 7 polish pass (per Sprint Workbook "Product Refinement & UX"):
//   - aria-live announcements for screen readers on every state change
//   - Cancel button while listening (stops recognition cleanly)
//   - Safety timeout so "Thinking..." never gets stuck indefinitely
//   - Consistent 2-decimal number formatting in results (fixes 2490.2 vs 2490.20)
//
// Core logic (fetch('/query'), state machine) unchanged from Day 6.

const STATES = ["idle", "listening", "confirm", "processing", "results", "error"];

const STATE_ANNOUNCEMENTS = {
  idle: "Ready. Tap the mic to ask a question.",
  listening: "Listening for your question.",
  confirm: "Please confirm your question.",
  processing: "Processing your question.",
  results: "Results are ready.",
  error: "Something went wrong.",
};

const panels = {};
STATES.forEach((s) => {
  panels[s] = document.getElementById(`state-${s}`);
});

const liveStatus = document.getElementById("live-status");

// Safety timeout: if processing hangs longer than this, fail gracefully
// instead of leaving the user staring at a spinner forever.
const PROCESSING_TIMEOUT_MS = 15000;
let processingTimeoutId = null;

function showState(name) {
  STATES.forEach((s) => {
    panels[s].classList.toggle("active", s === name);
  });
  if (liveStatus && STATE_ANNOUNCEMENTS[name]) {
    liveStatus.textContent = STATE_ANNOUNCEMENTS[name];
  }
  if (name !== "processing" && processingTimeoutId) {
    clearTimeout(processingTimeoutId);
    processingTimeoutId = null;
  }
}

// ---- Web Speech API setup ----
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
let recognition = null;
let lastTranscript = "";
let userCancelledListening = false;

function initRecognition() {
  if (!SpeechRecognition) {
    return null;
  }
  const rec = new SpeechRecognition();
  rec.lang = "en-US";
  rec.continuous = false;
  rec.interimResults = false;
  rec.maxAlternatives = 1;

  rec.onresult = (event) => {
    const transcript = event.results[0][0].transcript.trim();
    lastTranscript = transcript;
    document.getElementById("transcript-text").textContent = transcript;
    showState("confirm");
  };

  rec.onerror = (event) => {
    if (event.error === "aborted" || userCancelledListening) {
      showState("idle");
      return;
    }
    showError("Didn't catch that. Try again.");
  };

  rec.onend = () => {
    if (panels.listening.classList.contains("active") && !userCancelledListening) {
      showError("Didn't catch that. Try again.");
    }
  };

  return rec;
}

function startListening() {
  if (!SpeechRecognition) {
    showError("Voice input isn't supported in this browser. Please use Chrome.");
    return;
  }
  userCancelledListening = false;
  recognition = initRecognition();
  showState("listening");
  try {
    recognition.start();
  } catch (e) {
    showError("Could not start the microphone. Try again.");
  }
}

function cancelListening() {
  userCancelledListening = true;
  if (recognition) {
    recognition.abort();
  }
  showState("idle");
}

// ---- Button wiring ----
document.getElementById("mic-button").addEventListener("click", startListening);
document.getElementById("cancel-listening-btn").addEventListener("click", cancelListening);
document.getElementById("try-again-btn").addEventListener("click", startListening);
document.getElementById("error-try-again-btn").addEventListener("click", () => showState("idle"));
document.getElementById("ask-another-btn").addEventListener("click", () => showState("idle"));
document.getElementById("ask-this-btn").addEventListener("click", () => {
  runQuery(lastTranscript);
});

// ---- Real backend query ----
const MAX_QUESTION_LENGTH = 500; // must match backend/app.py's MAX_QUESTION_LENGTH

async function runQuery(question) {
  // Client-side mirror of the server's length check — catches the
  // (rare, since this is spoken input) case instantly instead of
  // making a network round trip just to get rejected.
  if (question.length > MAX_QUESTION_LENGTH) {
    showError("That question is too long, try rephrasing more briefly.");
    return;
  }

  showState("processing");

  processingTimeoutId = setTimeout(() => {
    showError("That took longer than expected. Try again.");
  }, PROCESSING_TIMEOUT_MS);

  let response;
  try {
    response = await fetch("/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });
  } catch (networkErr) {
    showError("Couldn't reach the server. Check your connection and try again.");
    return;
  }

  let data;
  try {
    data = await response.json();
  } catch (parseErr) {
    showError("Something went wrong reading the response. Try again.");
    return;
  }

  if (!response.ok) {
    showError(data.error || "Something went wrong. Try again.");
    return;
  }

  renderResults(data.results, data.sql);
}

function showError(message) {
  document.getElementById("error-message").textContent = message;
  showState("error");
}

// Formats a cell value for display. Non-integer numbers are shown with
// exactly 2 decimal places so "2490.2" and "2490.20" never look
// inconsistent side by side (the underlying value is already correct —
// this is purely a display-layer fix from Day 7's UI review).
function formatCell(value) {
  if (typeof value === "number" && !Number.isInteger(value)) {
    return value.toFixed(2);
  }
  return value;
}

function renderResults(results, sql) {
  const thead = document.getElementById("results-thead");
  const tbody = document.getElementById("results-tbody");
  const table = document.getElementById("results-table");
  const noResultsMsg = document.getElementById("no-results-msg");

  thead.innerHTML = "";
  tbody.innerHTML = "";

  if (!results || results.length === 0) {
    table.hidden = true;
    noResultsMsg.hidden = false;
  } else {
    table.hidden = false;
    noResultsMsg.hidden = true;

    const columns = Object.keys(results[0]);
    const headerRow = document.createElement("tr");
    columns.forEach((col) => {
      const th = document.createElement("th");
      th.textContent = col;
      headerRow.appendChild(th);
    });
    thead.appendChild(headerRow);

    results.forEach((row) => {
      const tr = document.createElement("tr");
      columns.forEach((col) => {
        const td = document.createElement("td");
        td.textContent = formatCell(row[col]);
        tr.appendChild(td);
      });
      tbody.appendChild(tr);
    });
  }

  document.getElementById("sql-text").innerHTML = highlightSql(sql || "");
  showState("results");
}

// ---- SQL keyword highlighting ----
function highlightSql(sql) {
  const keywords = [
    "SELECT", "FROM", "WHERE", "JOIN", "GROUP BY", "ORDER BY", "HAVING",
    "LIMIT", "AS", "ON", "AND", "OR", "SUM", "COUNT", "AVG", "ROUND",
    "DISTINCT", "DESC", "ASC",
  ];
  let escaped = sql
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
  keywords.forEach((kw) => {
    const re = new RegExp(`\\b${kw}\\b`, "gi");
    escaped = escaped.replace(re, (match) => `<span class="sql-keyword">${match}</span>`);
  });
  return escaped;
}

// Start on the idle state.
showState("idle");
