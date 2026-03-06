# ADR 0066: Secure Cached Resolver Pattern

## Status
Accepted

## Context
High-frequency string lookups (like resolving slugs, callsigns, URLs, or UUIDs to database IDs) must be cached in RAM via `@tools.ormcache` to prevent database exhaustion (ADR-0047). However, under the Micro-Service Account Pattern (ADR-0062), internal service accounts are microscopically scoped. If a centralized lookup method hardcodes its own module's service account, external modules calling that method will be forced into a context they do not control, often resulting in `AccessError` crashes because the central service account lacks access to the caller's required tables.

## Decision
We mandate the **Secure Cached Resolver Pattern** for all models that serve as directories or routing tables.

Any method exposing a cached ID lookup MUST implement the `override_svc_uid` parameter in its signature:
`def _get_id_by_identifier(self, identifier, override_svc_uid=None):`

When an external module calls the resolver, it MUST pass its own domain-specific service account ID. If the value is not in the `@tools.ormcache` RAM cache, the underlying database `.search()` will execute strictly under the caller's authorized micro-service context, keeping privileges perfectly isolated while still benefiting from the shared in-memory cache.

## Consequences
* Eliminates the "God Account" anti-pattern where a central service account requires read access to the entire database just to handle routing queries.
* Guarantees safe cross-module integrations without triggering unexpected ACL denials.
