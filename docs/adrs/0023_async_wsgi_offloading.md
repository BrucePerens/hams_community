# ADR 0023: Asynchronous WSGI Offloading via Independent Cursors

## Status
Accepted

## Context
Odoo WSGI web workers are synchronous and block easily. If a user triggers a web request that relies on a slow external API (e.g., scraping a third-party website like QRZ.com for a verification token), the worker thread is held hostage. If enough users do this simultaneously, the server runs out of workers and the platform goes offline.

## Decision
When a user-triggered controller or action requires high-latency external HTTP interactions (and the user's UI does not strictly depend on an immediate synchronous response), the system MUST offload the operation to a Python background thread.

To safely interact with the database without conflicting with the main thread's closed transaction:
1. The method must spawn a `threading.Thread`.
2. The target function must accept the `db_name`.
3. The background thread must spin up an entirely independent cursor using `with odoo.registry(db_name).cursor() as cr:`.
4. The thread must instantiate its own environment (`odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})`).

## Consequences
* **Positive:** Protects WSGI workers from exhaustion due to third-party network latency. Keeps the frontend UI snappy.
* **Negative:** Background threads silently fail if they encounter exceptions, making debugging more difficult. Requires explicit error logging inside the thread.
