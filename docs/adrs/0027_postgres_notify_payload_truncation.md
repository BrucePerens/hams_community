# ADR 0027: Postgres Native Signaling Payload Truncation

## Status
Accepted

## Context
The Ultimate DX Firehose relies on the PostgreSQL `NOTIFY` command to trigger an external async WebSocket daemon the millisecond a contact is logged. However, PostgreSQL imposes a strict 8000-byte hard limit on `NOTIFY` payloads. If a user uploads a large ADIF file, attempting to serialize and broadcast the entire JSON array of contacts through the `NOTIFY` channel will crash the database transaction.

## Decision
Event-driven architecture relying on `pg_notify` MUST strictly transmit comma-separated arrays of integer database IDs rather than serialized JSON data payloads.

1. The Odoo model will format the trigger as: `SELECT pg_notify('channel_name', '1,2,3,4')`.
2. The receiving async daemon will parse the IDs and execute an ultra-fast `SELECT row_to_json(t)` query to pull the heavy payload directly from the database.

## Consequences
* **Positive:** Guarantees absolute immunity from Postgres byte-limit crashes, regardless of how large the bulk import is.
* **Negative:** Requires the listening daemon to perform a subsequent `SELECT` query, introducing a microscopic read latency before broadcasting.
