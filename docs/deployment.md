# Production deployment

## Start the service

Generate a secret of at least 24 characters, configure the public host, and
start the hardened Compose service:

```bash
export FLOWBEACON_INGESTION_API_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"
export FLOWBEACON_ALLOWED_HOSTS="traces.example.com"
docker compose up --build -d
docker compose ps
```

Terminate TLS at a trusted reverse proxy and forward only the required public
port. `/health` is a process liveness probe; `/ready` also verifies that the
SQLite persistence layer is reachable. Do not expose the data volume or mount
the Docker socket into the container.

## Verify a release

```bash
FLOWBEACON_URL=https://traces.example.com \
FLOWBEACON_API_KEY="$FLOWBEACON_INGESTION_API_KEY" \
python scripts/smoke_test.py
```

The smoke check creates one uniquely named trace and verifies it can be read
back. Its data can be removed during routine retention cleanup.

## Backup and restore

Quiesce writes before copying the SQLite database. With Compose, stop the
service and copy the volume through a temporary container. Keep encrypted,
access-controlled backups and regularly test restoration in a non-production
environment. Never edit the live database file in place.

## Upgrade and rollback

1. Back up the database and record the running image digest.
2. Build and test the new image, then run the smoke check.
3. Watch structured request logs, readiness, HTTP 5xx responses, and disk use.
4. If validation fails, restore the prior image. Restore data only when a
   documented schema migration requires it; current releases are additive.

## Operational security

- Store the ingestion key in the deployment platform's secret manager.
- Rotate the key after suspected disclosure and during scheduled maintenance.
- Restrict `/docs` at the proxy if public API documentation is unnecessary.
- Apply retention limits to traces and exports according to local policy.
- Alert on readiness failures, repeated `401`/`422` responses, and storage use.
