# ADR 0049: Cache Verification via Query Counting Mandate

## Status
Accepted

## Context
The platform relies heavily on memory caching (`@tools.ormcache`) and distributed Redis caching to prevent PostgreSQL I/O exhaustion under massive concurrent load. However, caching logic is fragile. If a developer accidentally calls an ORM method like `.browse()` inside a cached loop, or if a decorator is accidentally dropped during a refactor, the application will silently fall back to executing N+1 database queries. Standard unit tests verify that data is returned correctly, but they do not verify *how* it was retrieved.

## Decision
All caching implementations MUST be strictly and mathematically verified using Odoo's native SQL query counter.
1. Every cached method MUST have a corresponding unit test within a `TransactionCase`.
2. The test MUST prime the cache, then execute the method again wrapped inside `with self.assertQueryCount(0):` to categorically prove that zero SQL queries are emitted during a cache hit.
3. The test MUST subsequently trigger the cache invalidation hook (e.g., executing a `write` or `unlink`) and assert that the subsequent query count is strictly greater than 0, proving the invalidation bus is functioning.

## Consequences
* **Positive:** Eliminates silent N+1 regressions. Any modification that accidentally bypasses the cache will immediately fail the CI/CD pipeline.
* **Negative:** Requires developers to deeply understand Odoo's internal query batching, as some ORM reads evaluate lazily and can trip the query counter unexpectedly if not carefully isolated.
