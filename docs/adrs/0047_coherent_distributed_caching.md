# ADR 0047: Coherent Distributed Caching via Postgres NOTIFY

## Status
Accepted

## Context
The Hams.com platform relies heavily on resolving human-readable string identifiers to database IDs on nearly every page load. For example, routing traffic to personal websites requires resolving `website_slug` to a `res.users` ID, and the Web Shack relies on resolving `callsign` to a directory profile.

While Odoo's native `@tools.ormcache` provides rapid L1 memory caching per-worker, in a horizontally scaled multi-worker or multi-server environment, these local caches can fall out of phase. If a user updates their callsign, Worker A might process the write and clear its local cache, but Worker B will continue serving the stale slug until the cache naturally expires or the worker restarts. Relying purely on Redis with a Time-To-Live (TTL) also introduces unacceptable synchronization drift for immediate UI feedback.

## Decision
We will implement a strongly coherent caching strategy utilizing PostgreSQL `NOTIFY` as the universal invalidation trigger.

1. **Targeted Caching:** High-frequency, read-heavy operations (slug-to-ID routing, callbook directory lookups) MUST utilize Odoo's `@tools.ormcache`.
2. **PostgreSQL Event Triggers:** Any ORM `write` or `unlink` operation that mutates a cached field (e.g., a user changing their `website_slug`) MUST emit a PostgreSQL `NOTIFY` payload containing the affected table and identifier.
3. **The Invalidation Bus:** A centralized background daemon (`cache_manager`) will `LISTEN` to this PostgreSQL channel. Upon receiving a mutation event, it will instantly broadcast a cache-invalidation command to the central Redis pub/sub layer.
4. **Immediate Flush:** All active WSGI workers will intercept this broadcast during their request lifecycle and flush the specific stale key from their local RAM registries, ensuring 100% phase coherence.

## Consequences
* **Positive:** Eliminates database CPU burn for repetitive routing queries, drastically speeding up the UI. Guarantees absolute phase coherence across all horizontal nodes.
* **Negative:** Increases architecture complexity. Developers must explicitly define `write`/`unlink` overrides to emit `NOTIFY` events for any newly cached model.
