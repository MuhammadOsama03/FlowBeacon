# FlowBeacon operator guide

## Connect telemetry

FlowBeacon accepts OTLP JSON at `POST /v1/otlp/v1/traces`. Point an OTLP/HTTP
exporter at the service URL plus `/v1/otlp`, or adapt the dependency-free
example in `examples/python/agent_trace.py`. When ingestion authentication is
enabled, send `Authorization: Bearer <FLOWBEACON_INGESTION_API_KEY>`.

The adapter recognizes standard span IDs, nanosecond timestamps, status codes,
and scalar attributes. `gen_ai.operation.name` values for chat, completion, and
embeddings are classified as model events. All attributes pass through the
same recursive secret-redaction boundary as native events.

## Evaluate runs

Send a policy to `POST /v1/runs/{run_id}/evaluate`:

```json
{"max_latency_ms": 5000, "max_errors": 0}
```

The response contains a stable pass/fail verdict, normalized score, and
per-check results suitable for CI gates. Use the same body with the `/alerts`
endpoint to preview warning and critical signals before connecting an external
notification system.

## Export data

Download redacted stored events from `/v1/runs/{run_id}/export?format=ndjson`
or `format=csv`. NDJSON retains complete structured attributes; CSV provides a
flat operational event index and intentionally excludes attribute payloads.

## Operational safeguards

- Keep the ingestion API key in a secret manager and rotate it regularly.
- Terminate TLS before FlowBeacon and restrict ingestion at the network edge.
- Treat exports as operational data even though known credentials are redacted.
- Monitor rejected payloads (`422`) and authentication failures (`401`).

## Retention and metrics

Administrative operations use a separate `FLOWBEACON_ADMIN_API_KEY`. Delete
only complete runs older than an explicit timezone-aware cutoff:

```bash
curl -X DELETE 'https://traces.example.com/v1/admin/runs?before=2026-09-01T00:00:00Z' \
  -H "Authorization: Bearer $FLOWBEACON_ADMIN_API_KEY"
```

Scrape `/metrics` with the same administrative Bearer credential. Metrics use
route templates instead of raw run IDs, preventing unbounded label cardinality.
