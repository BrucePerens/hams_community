# Runbook: APIs & Webhooks

## 1. REST API Security (HMAC-SHA256)
*(Reference: ham_logbook/controllers/api.py)*
To bypass Odoo's native CSRF protection safely for headless clients, the platform utilizes HMAC-SHA256 signatures.
* **POST Endpoints (e.g., ADIF Upload):** The client must hash the raw HTTP request body using their `adif_api_secret` and provide it in the `X-Odoo-Signature` header.
* **GET Endpoints (e.g., ADIF Download):** The client provides a Unix epoch timestamp in `X-Odoo-Timestamp` and hashes that timestamp using their secret. The server enforces a strict 5-minute TTL to block replay attacks.

## 2. Idempotency
*(Reference: ham_logbook/controllers/api.py -> live_qso -> [%ANCHOR: api_idempotency_check])*
High-velocity ingestion endpoints require the client to supply an `X-Idempotency-Key` header.
The backend caches the successful JSON response against this key in Redis for 24 hours.
If a client drops connection and retries the exact same payload, the system returns the cached response instead of creating a duplicate `ham.qso` record.

## 3. The WebSocket Firehose
*(Reference: daemons/dx_firehose/dx_firehose.py -> postgres_notify_handler -> [%ANCHOR: firehose_notify_handler])*
The real-time streaming engine operates completely outside the main web application.
* **Listen Channel:** It uses `asyncpg` to listen to the PostgreSQL `ham_qso_firehose` channel.
* **Trigger:** When Odoo commits a batch of QSOs, it fires a `NOTIFY` containing only the comma-separated integer IDs of the new records.
* **Broadcast:** The daemon wakes up, queries PostgreSQL for the specific JSON payloads, and instantly broadcasts them to all authenticated WebSocket clients.
