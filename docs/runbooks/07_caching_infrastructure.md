# Runbook: Distributed Caching Infrastructure

## 1. Coherent Phase Caching
To maintain high performance across a distributed, horizontally scaled environment without serving stale data, the platform uses a Redis-backed pub/sub bus for cache invalidation.

## 2. The Cache Manager Daemon
When an Odoo worker mutates a cached model, it emits a PostgreSQL `NOTIFY`. The cache manager daemon listens for this and broadcasts the payload to the Redis bus.

## 3. Worker Interception
Every HTTP request to the Odoo web workers passes through the `ir.http` middleware, which checks the Redis bus. If an invalidation signal is found, it flushes the local worker RAM cache.

## 4. Explicit Invalidation Implementations
To maintain distributed state, several modules explicitly trigger the Redis bus upon mutation:
* **User Websites Routing:** `[%ANCHOR: slug_cache_invalidation]` and `[%ANCHOR: slug_cache_invalidation_unlink]`
