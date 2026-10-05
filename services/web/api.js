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
