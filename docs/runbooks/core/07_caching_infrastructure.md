# Runbook: Distributed Caching Infrastructure

## 1. Coherent Phase Caching
To maintain high performance across a distributed, horizontally scaled environment without serving stale data, the platform uses a Redis-backed pub/sub bus for cache invalidation.

## 2. The Cache Manager Daemon
When an Odoo worker mutates a cached model, it emits a PostgreSQL `NOTIFY`. The `cache_manager` daemon listens for this and triggers `[%ANCHOR: cache_manager_redis_publish]` to broadcast the payload to the Redis bus.

## 3. Worker Interception
Every HTTP request to the Odoo web workers passes through the `ir.http` middleware, which checks the Redis bus. If an invalidation signal is found (`[%ANCHOR: redis_cache_interceptor]`), it flushes the local worker RAM cache.

## 4. Explicit Invalidation Implementations
To maintain distributed state, several modules explicitly trigger the Redis bus upon mutation:
* **Callbook Directory:** `[%ANCHOR: callbook_cache_invalidation]` and `[%ANCHOR: callbook_cache_invalidation_unlink]`
* **NCVEC Survey Questions:** `[%ANCHOR: survey_question_cache_invalidation]`, `[%ANCHOR: survey_question_cache_invalidation_create]`, and `[%ANCHOR: survey_question_cache_invalidation_unlink]`
* **Satellite TLEs:** `[%ANCHOR: satellite_tle_cache_invalidation]`
