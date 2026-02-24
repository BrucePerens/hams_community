# Hams.com System API Directory

This document is the comprehensive directory of all Application Programming Interfaces (APIs) exposed by the Hams.com platform. 

*Note: For a functional overview of the human-facing web interface, see the **[System User Guide](SYSTEM_USER_GUIDE.md)**.*

---

## 1. REST APIs (HTTP/HTTPS)

The system exposes several REST endpoints for data ingestion and frontend rendering. Secured endpoints utilize HMAC-SHA256 signatures to bypass standard CSRF protections safely.

*Architectural Security Note:* All automated REST API endpoints and webhooks on the Hams.com platform are protected against RPC Mass Assignment vulnerabilities. They execute their internal logic using the **Service Account Pattern** (e.g., `user_logbook_api_service`), ensuring operations are strictly bound by least-privilege Record Rules.

### A. Logbook & Ingestion (`ham_logbook`)
**Reference:** [Ham Logbook & ADIF Manual](ham_logbook/data/documentation.html)

* **Batch ADIF Upload:** `POST /api/v1/ham_logbook/adif/upload`
  * **Auth:** Required (`X-Odoo-User`, `X-Odoo-Signature`).
  * **Purpose:** Queues multi-megabyte ADIF files for background processing by the `adif_processor` daemon.
* **Batch ADIF Download:** `GET /api/v1/ham_logbook/adif/download`
  * **Auth:** Required (`X-Odoo-User`, `X-Odoo-Timestamp`, `X-Odoo-Signature`).
  * **Purpose:** Allows external services to download a user's logbook. Supports `limit`, `offset`, `start_date`, and `end_date` query parameters. Protected by a strict Nginx rate limit.
* **Real-Time QSO Logging:** `POST /api/v1/ham_logbook/qso/live`
  * **Auth:** Required (`X-Odoo-User`, `X-Odoo-Signature`).
  * **Purpose:** Instantly commits a single JSON-formatted QSO to the database. Designed for use with local desktop relays listening to WSJT-X / N1MM broadcasts.

### B. Frontend Data Widgets (`ham_callbook` & `ham_logbook`)
* **Community Map Data:** `GET /api/v1/ham_callbook/map_data`
  * **Auth:** Public.
  * **Purpose:** Returns a JSON array of operator coordinates for the Leaflet maps. Enforces strict GDPR Geographic Fuzzing.
* **Last QSO Widget:** `GET /api/v1/ham_logbook/last_qso/{slug}`
  * **Auth:** Public.
  * **Purpose:** Returns the most recent contact logged by a specific user for display on their personal Website Builder digital display widget.

### C. Web Shack (`ham_shack`)
**Reference:** [Ham Radio Web Shack Manual](ham_shack/data/documentation.html)

* **Callsign Lookup:** `GET /api/v1/ham_shack/lookup/{callsign}`
  * **Auth:** Required (`user`).
  * **Purpose:** Queries `ham_callbook` and `ham_logbook` for regulatory data and 4-hour historical context. Returns a JSON payload for Fast Entry auto-fill.
* **Missing Multipliers:** `GET /api/v1/ham_shack/multipliers`
  * **Auth:** Required (`user`).
  * **Purpose:** Returns a JSON dictionary of the active user's unworked multipliers based on the `ham.award.progress` model to highlight needed DX spots.

### D. Satellite Tracking (`ham_satellite`)
**Reference:** [Amateur Satellite Tracking Manual](ham_satellite/data/documentation.html)

* **Pass Predictions:** `GET /api/v1/ham_satellite/passes`
  * **Auth:** Public.
  * **Parameters:** `location` (Grid Square, Decimal, or DMS), `time` (optional UTC ISO string).
  * **Purpose:** Calculates orbital mechanics via the `ephem` library and returns a JSON array of active and upcoming satellite passes with AOS, TCA, and LOS metrics.

### E. Propagation Forecasting (`ham_propagation`)
**Reference:** [Live Propagation Forecasting Manual](../ham_propagation/data/documentation.html)

* **MUF Paths:** `GET /api/v1/ham_propagation/muf`
  * **Auth:** Required (`user`).
  * **Parameters:** `grid_square` (optional, falls back to user profile).
  * **Purpose:** Returns a JSON array of geographic polygons representing reachable propagation paths using an empirical ionospheric model based on the latest `ham.space.weather` telemetry.

---

## 2. WebSockets & Real-Time Streams

### A. The Ultimate DX Cluster Firehose (`ham_dx_cluster` / `dx_firehose`)
**Reference:** [Ham DX Cluster Manual](ham_dx_cluster/data/documentation.html)

* **Endpoint:** `wss://hams.com/ws/firehose?user=CALLSIGN&token=SECRET`
* **Auth:** Required (Verified natively against the Postgres `res_users` table upon connection).
* **Purpose:** A high-throughput, async Python daemon bypassing Odoo web workers entirely. It broadcasts a JSON feed of every QSO, POTA/SOTA activation, and contest exchange logged globally on the platform the millisecond it occurs.

### B. UI State Sync (Odoo Native Bus)
* **Endpoint:** `/websocket`
* **Auth:** Managed by Odoo session cookies.
* **Purpose:** Used internally by the web interface to scroll DX telnet spots dynamically on the user's dashboard.

---

## 3. XML-RPC Batch Processing Interfaces

Background daemons communicate with the central Odoo database using standard XML-RPC over port 8069. These interfaces are designed to minimize database locking during massive data syncs.

### A. Callbook Synchronization (`ham_callbook`)
* **Method:** `execute_kw('ham.callbook', 'sync_fcc_batch', ...)`
* **Purpose:** Processes batched arrays of FCC/ISED regulatory data.

### B. QSL Synchronization (`ham_logbook`)
* **Method:** `execute_kw('ham.qso', 'sync_qsl_batch', ...)`
* **Purpose:** Processes batched arrays of LoTW/eQSL confirmations, automatically matching them to existing QSOs in RAM to prevent N+1 queries.

---

## 4. Authentication Protocols Summary

Integrators building against Hams.com must utilize the correct auth paradigm for their use case:

1.  **API Secret (HMAC-SHA256 for POST):** Used for REST data ingestion. The client computes an HMAC hash of the raw payload bytes using their `adif_api_secret`.
2.  **API Secret (HMAC-SHA256 for GET):** Used for REST data retrieval. The client computes an HMAC hash of an injected `X-Odoo-Timestamp` header. The server enforces a strict 5-minute TTL on the timestamp to prevent replay attacks.
3.  **API Secret (Query String):** Used exclusively for the `dx_firehose` WebSocket handshake to authenticate the initial connection.
4.  **Client mTLS (ARRL LoTW):** Used strictly during the `ham_onboarding` flow. Nginx intercepts the `.p12` cryptographic certificate and passes the DN headers to Odoo to verify identity.

---

## 5. Local Hardware APIs

To bypass browser CORS and Mixed Content constraints, the Web Shack communicates with physical radio hardware via a local daemon (`hams_local_relay.py`) running on the operator's PC.

### A. Rig Control Relay
* **Endpoint:** `GET http://127.0.0.1:8089/qsy`
* **Parameters:** `freq` (in MHz), `mode` (optional string).
* **Auth:** None (Bound to localhost).
