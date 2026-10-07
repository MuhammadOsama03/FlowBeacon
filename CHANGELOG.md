# Changelog

## 1.0.0 — 2026-10-07

- Added secure native and OTLP trace ingestion with idempotent persistence.
- Added run search, summaries, latency/token/cost metrics, and error analysis.
- Added a responsive accessible trace dashboard and resilient interface states.
- Added evaluation policies, alert previews, and NDJSON/CSV exports.
- Added hardened container deployment, readiness probes, security headers,
  structured request logging, smoke checks, and container CI.

This is the first production-ready baseline. SQLite is intended for single-node
deployments; horizontal scaling and managed database support remain future work.
