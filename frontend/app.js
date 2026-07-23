// Day 3 foundation check: confirms the frontend can reach the Flask backend.
// Full voice UI state machine (idle/listening/confirm/processing/results/error)
// is built Day 4 per docs/UI-WIREFRAMES.md.

fetch("/health")
  .then((res) => res.json())
  .then((data) => {
    const el = document.getElementById("health-status");
    el.textContent = `Backend status: ${data.status} | Database: ${data.database} | API key configured: ${data.anthropic_api_key_configured}`;
  })
  .catch(() => {
    document.getElementById("health-status").textContent =
      "Could not reach backend.";
  });
