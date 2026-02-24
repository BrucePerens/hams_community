# ADR 0048: Platform Scalability & Horizontal Distribution

## Status
Accepted

## Context
As the platform grows to support global contest logging and massive concurrent WebSocket connections, running all components on a single monolithic server creates unacceptable single points of failure and resource contention. The architecture must support seamless horizontal scaling.

## Decision
The platform MUST adhere to the following decoupled scaling topology:

1. **Stateless Web Tier (Odoo WSGI/ASGI):**
   * Odoo application servers MUST remain entirely stateless.
   * HTTP Sessions MUST be centralized in Redis (`session_store = redis`).
   * This allows the edge router (Nginx / Cloudflare) to round-robin load balance traffic across $N$ horizontally scaled Odoo containers seamlessly.
2. **Database Tier (PostgreSQL):**
   * PostgreSQL will scale vertically (CPU/RAM) as the primary source of truth.
   * If connection limits are reached, `PgBouncer` MUST be introduced as a connection pooler between the Odoo workers and the database. The `asyncpg` daemons will connect directly to the database to bypass transaction pooling limitations for `LISTEN/NOTIFY` commands.
3. **Event & Message Bus (Redis & RabbitMQ):**
   * Redis acts as the centralized ephemeral cache (DX Spots), idempotency lock manager, and session store.
   * RabbitMQ handles all durable, asynchronous job queuing (ADIF processing, DNS syncing).
4. **Isolated Daemons:**
   * Long-running, high-I/O daemons (like `dx_firehose` and `ham_dx_daemon`) MUST run as independent containers or systemd services. They scale independently based on throughput requirements and MUST NEVER execute inside Odoo WSGI web worker threads.

## Consequences
* **Positive:** The system can handle virtually infinite concurrent web traffic and contest logging spikes by dynamically provisioning more Odoo worker nodes without data desynchronization.
* **Negative:** Requires rigorous infrastructure orchestration (e.g., Docker Swarm or Kubernetes) and strict adherence to the Zero-Sudo Service Account pattern to ensure daemons securely communicate with the clustered backend.
