# Security policy

AI telemetry can contain credentials, personal data, proprietary prompts, and tool output. FlowBeacon therefore treats every submitted field as sensitive and untrusted.

## Collection principles

- Collect metadata by default; capture prompt and output bodies only through explicit configuration.
- Redact authorization headers, cookies, API keys, access tokens, passwords, and common provider credentials before persistence.
- Enforce payload, batch, attribute, and string-size limits at ingestion.
- Never execute instructions or code found inside telemetry.
- Keep tenant authorization checks on the server for every write, query, export, and live stream.

## Operational controls

Production deployments must use TLS, rotated secrets, least-privilege database credentials, retention limits, audit logs, rate limits, encrypted backups, and tested deletion procedures. Logs must not reproduce rejected payloads or credentials.

## Reporting vulnerabilities

Report vulnerabilities through a private GitHub security advisory. Include the affected component, impact, and a minimal reproduction using synthetic data. Do not open a public issue containing secrets or real trace data.

## Supported versions

Until the first release, security fixes apply only to the latest commit on `main`.
