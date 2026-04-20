# Distributed Redis Cache

Fine-grained distributed caching and phase coherence for horizontally scaled Odoo clusters.

## Features
- Distributed Redis-backed cache to replace/augment Odoo's local cache.
- Prevents cache drift across multiple Odoo nodes.
- Fail-open design: falls back to local memory if Redis is unavailable.
- Fine-grained invalidation: only flushes specific models, not the entire cache.
- Management UI for status checks and manual invalidation.

## Installation
This module requires a Redis server.
Ensure the `redis` and `asyncpg` Python packages are installed.

## Configuration
The following environment variables can be used to configure the Redis connection:
- `REDIS_HOST`: Defaults to `redis` or `127.0.0.1`.
- `REDIS_PORT`: Defaults to `6379`.

## Architecture
- **Postgres NOTIFY**: Triggered when a model's cache needs invalidation.
- **Cache Manager Daemon**: A standalone Python service that bridges Postgres NOTIFY to Redis Pub/Sub.
- **Redis Pub/Sub**: Distributes invalidation signals to all Odoo workers.
- **Middleware Interceptor**: Odoo workers check for signals in `ir.http` and flush local caches accordingly.

## Security
Built with the **Zero-Sudo** architecture. Operations are performed by dedicated service accounts with minimal privileges.

## Documentation
Comprehensive documentation is available via the **Manual Library** module after installation.
