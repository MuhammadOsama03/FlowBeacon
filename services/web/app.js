import { getRun, getRunMetrics, listRuns } from "./api.js";

const list = document.querySelector("#run-list");
const detail = document.querySelector("#run-detail");
const filters = document.querySelector("#filters");
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

function eventRow(event) {
  const parent = event.parent_span_id ? `<span>parent ${escapeHtml(event.parent_span_id)}</span>` : "";
  return `<li class="event event--${event.status}">
    <span class="event__mark" aria-hidden="true"></span><div><div class="event__title"><strong>${escapeHtml(event.event_type)}</strong><span class="status status--${event.status}">${event.status}</span></div>
    <div class="event__meta"><code>${escapeHtml(event.span_id)}</code>${parent}<time datetime="${event.timestamp}">${time(event.timestamp)}</time>${event.duration_ms == null ? "" : `<span>${duration(event.duration_ms)}</span>`}</div></div>
  </li>`;
}

async function selectRun(runId) {
  state.controller?.abort();
  state.controller = new AbortController();
  state.selected = runId;
  document.querySelectorAll("[data-run-id]").forEach(card => card.setAttribute("aria-pressed", card.dataset.runId === runId));
  detail.innerHTML = `<div class="empty-state" role="status">Loading trace…</div>`;
  try {
    const run = await getRun(runId, state.controller.signal);
    detail.innerHTML = `<header class="detail-heading"><div><p class="eyebrow">Run detail</p><h2>${escapeHtml(run.run_id)}</h2></div><span>${run.events.length} events</span></header>
      <section aria-labelledby="timeline-title"><h3 id="timeline-title" class="panel-heading">Trace timeline</h3><ol class="timeline">${run.events.map(eventRow).join("")}</ol></section>`;
  } catch (error) {
    if (error.name !== "AbortError") detail.innerHTML = `<div class="empty-state"><h2>Trace unavailable</h2><p>${escapeHtml(error.message)}</p><button data-detail-retry>Try again</button></div>`;
  }
}

async function loadRuns() {
  list.innerHTML = `<div class="list-state" role="status">Loading recent runs…</div>`;
  try {
    const form = new FormData(filters);
    const page = await listRuns({ search: form.get("search").trim(), status: form.get("status") });
    list.innerHTML = page.items.length ? page.items.map(runCard).join("") : `<div class="list-state">No traces yet.</div>`;
  } catch (error) {
    list.innerHTML = `<div class="list-state list-state--error">Could not load runs.<button data-retry>Try again</button></div>`;
  }
}

let filterTimer;
filters.addEventListener("input", () => { clearTimeout(filterTimer); filterTimer = setTimeout(loadRuns, 250); });

list.addEventListener("click", event => {
  const card = event.target.closest("[data-run-id]");
  if (card) selectRun(card.dataset.runId);
  if (event.target.matches("[data-retry]")) loadRuns();
});

detail.addEventListener("click", event => { if (event.target.matches("[data-detail-retry]")) selectRun(state.selected); });

loadRuns();
