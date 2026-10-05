import { getRun, getRunMetrics, listRuns } from "./api.js";

const list = document.querySelector("#run-list");
const detail = document.querySelector("#run-detail");
const state = { selected: null, controller: null };

const escapeHtml = (value) => String(value).replace(/[&<>'"]/g, character => ({
  "&":"&amp;", "<":"&lt;", ">":"&gt;", "'":"&#39;", '"':"&quot;"
})[character]);
const time = (value) => new Intl.DateTimeFormat(undefined, { dateStyle:"medium", timeStyle:"short" }).format(new Date(value));
const duration = (value) => value >= 1000 ? `${(value / 1000).toFixed(2)}s` : `${Math.round(value)}ms`;

function runCard(run) {
  const active = run.run_id === state.selected;
  return `<button class="run-card" data-run-id="${escapeHtml(run.run_id)}" aria-pressed="${active}">
    <span class="run-card__top"><strong>${escapeHtml(run.run_id)}</strong><span class="status status--${run.status}">${run.status}</span></span>
    <span class="run-card__meta"><time datetime="${run.started_at}">${time(run.started_at)}</time><span>${run.event_count} events</span><span>${duration(run.duration_ms)}</span></span>
  </button>`;
}

async function loadRuns() {
  list.innerHTML = `<div class="list-state" role="status">Loading recent runs…</div>`;
  try {
    const page = await listRuns();
    list.innerHTML = page.items.length ? page.items.map(runCard).join("") : `<div class="list-state">No traces yet.</div>`;
  } catch (error) {
    list.innerHTML = `<div class="list-state list-state--error">Could not load runs.<button data-retry>Try again</button></div>`;
  }
}

list.addEventListener("click", event => {
  const card = event.target.closest("[data-run-id]");
  if (card) selectRun(card.dataset.runId);
  if (event.target.matches("[data-retry]")) loadRuns();
});

loadRuns();
