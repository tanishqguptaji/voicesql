// app.js — VoiceSQL frontend state machine.
//
// Day 6 scope (per Blueprint "Day 5 — Integration"):
//   - Real fetch('/query') call replaces yesterday's mock data
//   - Full end-to-end loop: voice -> transcript -> real AI-generated SQL -> real results

const STATES = ["idle", "listening", "confirm", "processing", "results", "error"];

const panels = {};
STATES.forEach((s) => {
  panels[s] = document.getElementById(`state-${s}`);
});

function showState(name) {
  STATES.forEach((s) => {
    panels[s].classList.toggle("active", s === name);
  });
}

// ---- Web Speech API setup ----
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
let recognition = null;
let lastTranscript = "";

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

  rec.onerror = () => {
    showError("Didn't catch that. Try again.");
  };

  rec.onend = () => {
    if (panels.listening.classList.contains("active")) {
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
  recognition = initRecognition();
  showState("listening");
  try {
    recognition.start();
  } catch (e) {
    showError("Could not start the microphone. Try again.");
  }
}

// ---- Button wiring ----
document.getElementById("mic-button").addEventListener("click", startListening);
document.getElementById("try-again-btn").addEventListener("click", startListening);
document.getElementById("error-try-again-btn").addEventListener("click", () => showState("idle"));
document.getElementById("ask-another-btn").addEventListener("click", () => showState("idle"));
document.getElementById("ask-this-btn").addEventListener("click", () => {
  runQuery(lastTranscript);
});

// ---- Real backend query (replaces Day 5's mock setTimeout logic) ----
async function runQuery(question) {
  showState("processing");

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
        td.textContent = row[col];
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
    "SELECT", "FROM", "WHERE", "JOIN", "GROUP BY", "ORDER BY",
    "LIMIT", "AS", "ON", "AND", "OR", "SUM", "COUNT", "AVG",
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
