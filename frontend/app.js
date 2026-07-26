// app.js — VoiceSQL frontend state machine.
//
// Day 4/5 scope (per Blueprint "Day 4 — Frontend UI"):
//   - Real browser voice capture via the Web Speech API (free, built into Chrome)
//   - All 6 UI states wired and working
//   - Results table + SQL panel populated with MOCK data to validate layout
//
// Wiring to the real /query backend (built and tested yesterday) happens
// in the next milestone/day per the Blueprint's "Day 5 — Integration" section.

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
    // If we're still on the listening panel with no transcript captured,
    // the mic closed without hearing anything usable.
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

document.getElementById("error-try-again-btn").addEventListener("click", () => {
  showState("idle");
});

document.getElementById("ask-another-btn").addEventListener("click", () => {
  showState("idle");
});

document.getElementById("ask-this-btn").addEventListener("click", () => {
  runQuery(lastTranscript);
});

// ---- Mock query execution (Day 4: layout validation only) ----
// This is intentionally NOT calling the real /query endpoint yet.
// Tomorrow this function is replaced with a real fetch('/query', ...) call.
function runQuery(question) {
  showState("processing");

  setTimeout(() => {
    // Simulate an occasional "no results" or error case so every UI
    // branch can be visually verified today, alongside the success path.
    const lower = question.toLowerCase();

    if (lower.includes("error") || lower.includes("fail")) {
      showError("Couldn't safely process that question.");
      return;
    }

    if (lower.includes("empty") || lower.includes("nothing")) {
      renderResults([], "SELECT * FROM customers WHERE 1 = 0");
      return;
    }

    const mockSql =
      "SELECT c.name, SUM(oi.quantity * oi.unit_price) AS total_spent " +
      "FROM customers c JOIN orders o ON c.customer_id = o.customer_id " +
      "JOIN order_items oi ON o.order_id = oi.order_id " +
      "GROUP BY c.customer_id ORDER BY total_spent DESC LIMIT 3";

    const mockResults = [
      { name: "Chetan Mehta", total_spent: 914.82 },
      { name: "Alice Kumar", total_spent: 780.15 },
      { name: "Priya Reddy", total_spent: 664.40 },
    ];

    renderResults(mockResults, mockSql);
  }, 900);
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

  document.getElementById("sql-text").innerHTML = highlightSql(sql);
  showState("results");
}

// ---- Simple SQL keyword highlighting (Day 8 preview, harmless to include now) ----
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
