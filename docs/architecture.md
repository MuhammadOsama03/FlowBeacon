# Architecture

FlowBeacon separates telemetry ingestion from read-heavy exploration so either side can scale independently.

## Components

1. **Collector API** validates batches, assigns ingestion metadata, redacts protected values, and writes accepted events.
2. **Trace store** persists runs and spans with tenant, project, time, status, and parent-child indexes.
3. **Query API** provides bounded filtering, pagination, summaries, timelines, and exports.
4. **Web dashboard** visualizes runs, nested spans, errors, latency, token usage, and estimated cost.
5. **Integration SDKs** translate framework events into the stable FlowBeacon envelope.

## Initial event envelope

Every event should include a schema version, event identifier, run identifier, timestamp, event type, status, and attributes. Spans may additionally include parent span, start/end time, model/provider, tool name, token counts, and error classification.

## Design rules

- Accept client-generated identifiers but validate their format and size.
- Store timestamps in UTC and preserve deterministic event ordering.
- Make ingestion idempotent by event identifier.
- Treat prompts, outputs, tool results, and attributes as untrusted sensitive data.
- Keep provider-specific fields inside namespaced attributes.
- Version schemas before making incompatible changes.

## First vertical slice

The first runnable slice will accept one trace batch, persist it locally, retrieve the run, and render its ordered timeline. Tests will cover validation, idempotency, redaction, and parent-child ordering.
