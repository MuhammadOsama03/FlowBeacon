const JSON_HEADERS = { Accept: "application/json" };

export class ApiError extends Error {
  constructor(message, status) { super(message); this.name = "ApiError"; this.status = status; }
}

async function request(path, signal) {
  const response = await fetch(path, { headers: JSON_HEADERS, signal });
  if (!response.ok) {
    let detail = `Request failed (${response.status})`;
    try { detail = (await response.json()).detail || detail; } catch { /* non-JSON response */ }
    throw new ApiError(detail, response.status);
  }
  return response.json();
}

async function post(path, body, signal) {
  const response = await fetch(path, { method: "POST", signal,
    headers: { ...JSON_HEADERS, "Content-Type": "application/json" }, body: JSON.stringify(body) });
  if (!response.ok) throw new ApiError(`Request failed (${response.status})`, response.status);
  return response.json();
}

export function listRuns({ search = "", status = "", limit = 20, offset = 0, signal } = {}) {
  const query = new URLSearchParams({ limit, offset });
  if (search) query.set("search", search);
  if (status) query.set("status", status);
  return request(`/v1/runs?${query}`, signal);
}

export function getRun(runId, signal) {
  return request(`/v1/runs/${encodeURIComponent(runId)}`, signal);
}

export function getRunMetrics(runId, signal) {
  return request(`/v1/runs/${encodeURIComponent(runId)}/metrics`, signal);
}

export function evaluateRun(runId, policy, signal) {
  return post(`/v1/runs/${encodeURIComponent(runId)}/evaluate`, policy, signal);
}

export function previewAlerts(runId, policy, signal) {
  return post(`/v1/runs/${encodeURIComponent(runId)}/alerts`, policy, signal);
}
