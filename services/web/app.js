import { evaluateRun, getRun, getRunMetrics, listRuns } from "./api.js";

const list = document.querySelector("#run-list");
const detail = document.querySelector("#run-detail");
const filters = document.querySelector("#filters");
const resultsCount = document.querySelector("#results-count");
const previousPage = document.querySelector("#previous-page");
const nextPage = document.querySelector("#next-page");
const pageLabel = document.querySelector("#page-label");
const state = { selected: null, controller: null, offset: 0, limit: 20, total: 0 };

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
    const [run, metrics] = await Promise.all([getRun(runId, state.controller.signal), getRunMetrics(runId, state.controller.signal)]);
    const errors = run.events.filter(event => event.status === "error").length;
    const encodedRunId = encodeURIComponent(run.run_id);
    detail.innerHTML = `<header class="detail-heading"><div><p class="eyebrow">Run detail</p><h2 tabindex="-1">${escapeHtml(run.run_id)}</h2></div><div class="detail-actions"><span>${run.events.length} events</span><a href="/v1/runs/${encodedRunId}/export?format=ndjson" download>NDJSON</a><a href="/v1/runs/${encodedRunId}/export?format=csv" download>CSV</a></div></header>
      <dl class="metrics" aria-label="Run metrics">
        <div><dt>Total latency</dt><dd>${duration(metrics.latency_ms)}</dd></div>
        <div><dt>Model latency</dt><dd>${duration(metrics.model_latency_ms)}</dd></div>
        <div><dt>Tokens</dt><dd>${(metrics.input_tokens + metrics.output_tokens).toLocaleString()}</dd></div>
        <div><dt>Reported cost</dt><dd>$${metrics.estimated_cost_usd.toFixed(4)}</dd></div>
        <div class="${errors ? "metric--danger" : ""}"><dt>Errors</dt><dd>${errors}</dd></div>
      </dl>
      <section class="signals" aria-labelledby="signals-title"><div><h3 id="signals-title">Quality gate</h3><p>Check this run against the default 30-second, zero-error policy.</p></div><button data-evaluate>Evaluate</button><output id="evaluation-result"></output></section>
      <section aria-labelledby="timeline-title"><h3 id="timeline-title" class="panel-heading">Trace timeline</h3><ol class="timeline">${run.events.map(eventRow).join("")}</ol></section>`;
  } catch (error) {
    if (error.name !== "AbortError") detail.innerHTML = `<div class="empty-state"><h2>Trace unavailable</h2><p>${escapeHtml(error.message)}</p><button data-detail-retry>Try again</button></div>`;
  }
}

async function loadRuns() {
  list.setAttribute("aria-busy", "true");
  list.innerHTML = `<div class="list-state" role="status">Loading recent runs…</div>`;
  try {
    const form = new FormData(filters);
    const page = await listRuns({ search: form.get("search").trim(), status: form.get("status"), limit: state.limit, offset: state.offset });
    state.total = page.total;
    list.innerHTML = page.items.length ? page.items.map(runCard).join("") : `<div class="list-state"><strong>No matching traces</strong><p>Adjust the search or status filter.</p></div>`;
    resultsCount.textContent = `${page.total} run${page.total === 1 ? "" : "s"} found`;
    previousPage.disabled = state.offset === 0;
    nextPage.disabled = state.offset + state.limit >= page.total;
    pageLabel.textContent = `Page ${Math.floor(state.offset / state.limit) + 1}`;
  } catch (error) {
    list.innerHTML = `<div class="list-state list-state--error" role="alert"><strong>Could not load runs</strong><p>Check the API connection and try again.</p><button data-retry>Try again</button></div>`;
  } finally {
    list.setAttribute("aria-busy", "false");
  }
}

let filterTimer;
filters.addEventListener("input", () => { state.offset = 0; clearTimeout(filterTimer); filterTimer = setTimeout(loadRuns, 250); });
previousPage.addEventListener("click", () => { state.offset = Math.max(0, state.offset - state.limit); loadRuns(); });
nextPage.addEventListener("click", () => { if (state.offset + state.limit < state.total) { state.offset += state.limit; loadRuns(); } });

list.addEventListener("click", event => {
  const card = event.target.closest("[data-run-id]");
  if (card) selectRun(card.dataset.runId).then(() => detail.querySelector("h2")?.focus());
  if (event.target.matches("[data-retry]")) loadRuns();
});

detail.addEventListener("click", async event => {
  if (event.target.matches("[data-detail-retry]")) selectRun(state.selected);
  if (event.target.matches("[data-evaluate]")) {
    const output = detail.querySelector("#evaluation-result");
    output.textContent = "Evaluating…";
    try {
      const result = await evaluateRun(state.selected, { max_latency_ms: 30000, max_errors: 0 });
      output.innerHTML = `<strong class="verdict verdict--${result.verdict}">${result.verdict}</strong> ${Math.round(result.score * 100)}%`;
    } catch { output.textContent = "Evaluation unavailable"; }
  }
});

loadRuns();
