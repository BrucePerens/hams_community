# ADR 0001: Hybrid Monolith-Daemon Architecture

## Status
Accepted

## Context
The Hams.com platform handles massive data ingestion (multi-megabyte ADIF files), continuous external polling (QSL syncs, FCC databases), and high-concurrency real-time streaming (DX Cluster WebSockets). Odoo's native WSGI/ASGI web workers are optimized for stateful, low-concurrency ERP transactions. Relying on Odoo web workers or native cron jobs for these tasks results in worker timeouts, high memory consumption, and blocked HTTP requests for standard users.

## Decision
We will adopt a Hybrid Monolith-Daemon Architecture. 
1. Odoo acts strictly as the database authority, ORM layer, and primary web UI.
2. All high-CPU, high-I/O, and high-concurrency tasks MUST be offloaded to standalone Python daemons.
3. Communication between Odoo and daemons will occur via RabbitMQ (event queuing), Redis (ephemeral caching), or direct PostgreSQL connections (e.g., `asyncpg` for LISTEN/NOTIFY), completely bypassing the Odoo web worker layer.

## Consequences
* **Positive:** The main web application remains lightning fast and highly responsive, regardless of background processing loads. WebSocket connections can scale to tens of thousands without exhausting Odoo threads.
* **Negative:** Increased infrastructure complexity. Requires maintaining separate `systemd` or Docker orchestration for the external daemons, as well as distinct virtual environments.
