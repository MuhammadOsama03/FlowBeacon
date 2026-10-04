# FlowBeacon

**Illuminate every step of your AI agents.**

FlowBeacon is an open observability platform for tracing, debugging, and improving AI-agent runs. It will collect structured run events, show tool and model activity as a timeline, and surface latency, token, cost, and failure signals without storing sensitive content by default.

## Product goals

- Ingest framework-neutral agent traces through a documented API.
- Explore runs, spans, model calls, tool calls, errors, and timing.
- Compare successful and failed runs with useful operational metrics.
- Redact secrets and minimize captured prompts and outputs.
- Export interoperable telemetry and support OpenTelemetry conventions.

## Planned stack

- TypeScript shared schemas
- FastAPI ingestion and query service
- PostgreSQL persistence
- Next.js dashboard
- OpenTelemetry-compatible integrations
- Docker and GitHub Actions

## Run the API locally

Requirements: Python 3.12+

```bash
cd services/api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open the interactive API documentation at `http://localhost:8000/docs`.

Store data in a custom location with:

```bash
FLOWBEACON_DATABASE_PATH=./data/flowbeacon.db uvicorn app.main:app
```

## First trace

Submit a bounded event batch:

```bash
curl -X POST http://localhost:8000/v1/events \
  -H "Content-Type: application/json" \
  -d '{"events":[{"event_id":"evt-1","run_id":"run-1","span_id":"span-1","timestamp":"2026-10-03T08:00:00Z","event_type":"tool","status":"ok","duration_ms":12.5,"attributes":{"tool.name":"search"}}]}'
```

Retrieve the ordered trace with `GET /v1/runs/run-1`.

List summarized runs with `GET /v1/runs`; the endpoint accepts `status`,
`search`, `limit`, and `offset`. Aggregate latency, token usage, and reported
costs are available from `GET /v1/runs/{run_id}/metrics`.

In production, set `FLOWBEACON_INGESTION_API_KEY` and send the value as a
Bearer token. Leaving it unset preserves the zero-configuration local workflow.

## Quality checks

```bash
cd services/api
python -m compileall -q app tests
python -m pytest
```

GitHub Actions runs these checks for every API change.

## Delivery plan

Development is organized into five milestones: architecture, backend intelligence, dashboard, integrations, and production readiness. Every milestone must keep tests and CI passing.

## Status

Milestones 1 and 2 are complete: FlowBeacon has secure trace ingestion,
searchable and paginated run summaries, aggregate metrics, operational error
classification, authentication foundations, automated tests, and CI. The next
milestone builds the web dashboard.
