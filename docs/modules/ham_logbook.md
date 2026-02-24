# 📻 Ham Logbook (`ham_logbook`)

*Copyright © Bruce Perens K6BP. AGPL-3.0.*

**Context:** Technical documentation strictly for LLMs and Integrators.

---

## 1. Overview
Provides the core `ham.qso` model for tracking over-the-air contacts. Enforces strict GDPR exemptions for public RF records. Features a robust confirmation engine with automatic cross-indexing, Space Weather mapping, asynchronous ADIF processing queues, and real-time ingestion endpoints.

---

## 2. Data Model Reference

### Core Model: `ham.qso`
* **`owner_user_id`** (`Many2one` to `res.users`): **CRITICAL:** `ondelete='set null'` is enforced to anonymize rather than destroy public records.
* **`is_fully_confirmed`** (`Boolean`): Evaluates to True if cross-indexed or externally QSL'd.
* **`inverse_qso_id`** (`Many2one` to `ham.qso`): Links to the other station's log entry.
* **Space Weather:** `sfi`, `a_index`, `k_index` (Appended dynamically during `create()`).

### Background Support Models
* **`ham.adif.queue`**: Asynchronous staging queue for large ADIF files. Processed by external RabbitMQ daemons.
* **`ham.space.weather`**: Stores hourly solar telemetry from NOAA SWPC.

### Extended `res.users`
* **`adif_api_secret`**: Cryptographic HMAC token.
* **`lotw_password` / `eqsl_password`**: Secured via Fernet encryption for background QSL polling.

---

## 3. Public Python API & Methods
* **`model.sync_qsl_batch(user_id, provider, qsl_list)`**: High-performance XML-RPC endpoint for batch updates in RAM without N+1 database locks.
* **`record.action_nudge_station()`**: Sends a polite confirmation request email to the target station.
* **`record._link_inverse_qsos()`**: Fuzzy matches frequency (+/- 50kHz) and time (+/- 15min) to establish `platform_confirmed` relationships.

---

## 4. REST APIs
* **ADIF Upload:** `POST /api/v1/ham_logbook/adif/upload` (HMAC payload signature, Async Queueing).
* **ADIF Download:** `GET /api/v1/ham_logbook/adif/download` (HMAC timestamp signature, 5-minute TTL).
* **Live Logging:** `POST /api/v1/ham_logbook/qso/live` (Commits instantly, triggers DX Firehose Postgres `NOTIFY`).
* **POTA Statistics:** `GET /api/v1/ham_logbook/pota_stats/<slug>` (Returns unique hunted and activated parks).
* **Idempotency:** All ingestion endpoints require `X-Idempotency-Key` validated against Redis to prevent duplicate logs on network retry.
