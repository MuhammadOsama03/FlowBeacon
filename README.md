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

## Delivery plan

Development is organized into five milestones: architecture, backend intelligence, dashboard, integrations, and production readiness. Every milestone must keep tests and CI passing.

## Status

Product foundation in progress.
