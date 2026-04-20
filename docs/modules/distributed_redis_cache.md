# Distributed Redis Cache

## Architecture & Overview
Standard Odoo `@tools.ormcache` relies on a local worker registry cache, which can drift out of sync in horizontally scaled, multi-node environments. This module provides a fine-grained, distributed Redis-backed cache that enforces strict phase coherence across the entire cluster.

**The Invalidation Pipeline:**
1. An Odoo worker mutates a cached model and fires a PostgreSQL `NOTIFY` on the `distributed_cache_invalidation` channel.
2. The standalone `cache_manager.py` daemon receives the `NOTIFY` and publishes the payload to the Redis `odoo_cache_invalidation_bus` pub/sub channel. [@ANCHOR: cache_manager_redis_publish]
3. A background thread running inside every Odoo WSGI worker's `ir.http` middleware intercepts the Redis broadcast and instantly queues the model for local cache flushing before serving its next HTTP request. [@ANCHOR: redis_cache_interceptor]

## Configuration
The daemon can be configured via environment variables. [@ANCHOR: cache_manager_config]

## UI
The module provides a UI to manage the cache and check Redis status. [@ANCHOR: distributed_cache_view]

## API
- `@distributed_cache()`
- `invalidate_model_cache(env, model_name)`
