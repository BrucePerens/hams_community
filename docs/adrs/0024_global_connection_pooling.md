# ADR 0024: Global Connection Pooling for Non-ORM Datastores

## Status
Accepted

## Context
The platform relies heavily on external caching and message brokers (Redis, RabbitMQ) to support high-velocity REST APIs (like Live QSO logging and DX spotting). Establishing a new TCP connection to these services on every single HTTP request adds significant latency overhead and can exhaust ephemeral ports on the host machine.

## Decision
Direct integrations with external caching or queue services within Odoo controllers MUST utilize module-level connection pooling.

1. The connection pool (e.g., `redis.ConnectionPool`) MUST be declared globally at the top of the Python file.
2. Controllers and methods must draw from this persistent pool (`redis.Redis(connection_pool=redis_pool)`) rather than instantiating a new, un-pooled connection.

## Consequences
* **Positive:** Drastically reduces TCP handshake latency for high-throughput APIs. Lowers resource utilization on both the application and the datastore.
* **Negative:** State management issues can occur if a connection in the pool goes stale or the external service restarts, requiring robust `try/except` fallback logic when utilizing the pooled connection.
