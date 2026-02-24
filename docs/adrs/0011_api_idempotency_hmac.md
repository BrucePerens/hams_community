# ADR 0011: API Idempotency & HMAC Security

## Status
Accepted

## Context
The platform provides headless REST APIs for external logging software (e.g., WSJT-X, N1MM) to ingest data. These clients cannot manage standard Odoo browser cookies or CSRF tokens. Additionally, unreliable network connections frequently cause external clients to retry POST requests, which would normally result in duplicate `ham.qso` database rows.

## Decision
We bypass Odoo's native `csrf=True` protection on automated routes by implementing a dual-layer security protocol:
1. **HMAC-SHA256 Signatures:** Clients must cryptographically sign their payloads using their private `adif_api_secret`. The server rebuilds the hash; if it mismatches, the request is dropped. For GET requests, the signature encompasses an `X-Odoo-Timestamp` with a strict 5-minute TTL to prevent replay attacks.
2. **Redis Idempotency:** Clients must provide a unique `X-Idempotency-Key` header on POST requests. The API controller checks this key against Redis. If found, it instantly returns the cached successful JSON response without executing WSGI logic or querying PostgreSQL.

3. **Database-Level Fallback:** Because Redis is a volatile, ephemeral cache, it cannot be relied upon as the absolute guarantor of idempotency. If the Redis container restarts, all idempotency memory is lost. Therefore, critical ingestion tables MUST implement composite SQL `UNIQUE` constraints (e.g., `UNIQUE(owner_user_id, callsign, qso_date)`) to mathematically reject duplicate data at the disk level if the cache is bypassed.

## Consequences
* **Positive:** Bulletproof protection against duplicate data ingestion and CSRF attacks without requiring stateful browser cookies, maintaining integrity even during cache loss.
* **Negative:** Increases integration friction for third-party developers, as they must implement HMAC hashing and idempotency key generation in their respective languages.
