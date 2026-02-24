# ADR 0025: Stateless HMAC-TTL Routing Tokens

## Status
Accepted

## Context
Features like cross-domain authentication (Nginx mTLS to Cloudflare proxy) and API endpoints (ADIF downloading) require secure, temporary validation. Storing these ephemeral session tokens in a PostgreSQL table generates unnecessary write-heavy database bloat and requires background cron jobs to clean up expired rows.

## Decision
Short-lived authorization grants (Time-To-Live under 15 minutes) MUST utilize stateless, HMAC-signed payload strings, avoiding database storage entirely.

1. The token MUST contain the required payload data (e.g., callsign).
2. The token MUST contain a Unix epoch timestamp.
3. The token MUST contain an HMAC-SHA256 signature generated against the payload, timestamp, and a highly secure secret (like `database.secret` or a user's API key).
4. The consuming route MUST mathematically reconstruct the hash, rejecting the request if it mismatches or if the timestamp exceeds the strict TTL.

## Consequences
* **Positive:** Zero database I/O. Horizontally scalable across multiple application servers without requiring a shared state cache.
* **Negative:** Stateless tokens cannot be actively revoked before they expire. They must be kept extremely short-lived to mitigate theft.
