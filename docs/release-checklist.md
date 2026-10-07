# Release-readiness review

## Verified in automation

- [x] Domain, ingestion, query, dashboard, integration, and operations tests
- [x] Python compilation and JavaScript syntax validation
- [x] Non-root production image build
- [x] Read-only container execution with dropped Linux capabilities
- [x] Readiness-gated end-to-end ingest and retrieval smoke test
- [x] Secret redaction and authenticated native/OTLP ingestion
- [x] Host allowlisting, CSP, HSTS in production, and request correlation

## Deployment owner checks

- [ ] Set a unique 24+ character ingestion key in a secret manager
- [ ] Configure the exact public hostname and TLS reverse proxy
- [ ] Define backup, retention, disk-capacity, and key-rotation policies
- [ ] Run `scripts/smoke_test.py` against the deployed URL
- [ ] Configure alerts for readiness, 5xx/401/422 rates, and disk utilization

## Known boundaries

- SQLite supports a durable single-node deployment, not horizontal writers.
- Alert endpoints preview signals; delivery to paging systems is not included.
- Authentication protects ingestion; dashboard access belongs at the proxy or
  a future multi-user identity layer.
