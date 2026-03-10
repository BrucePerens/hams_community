# ADR 0068: PostgreSQL View Security & Optimization Pattern

## Status
Accepted

## Context
We frequently need to expose a subset of table data to unauthenticated public routes (e.g., Community Maps, Directories) or cross-domain background daemons.

Historically, developers would grant `base.group_public` read access to the root table (e.g., `business.directory` or `user.location` in an external repository) and rely on the QWeb template to only render the "safe" fields. This is a severe security vulnerability. An attacker can bypass the website entirely, connect to the Odoo XML-RPC port as a public guest, and execute a `search_read` to dump the entire table—exposing hidden columns like `internal_api_key` (which could be attacked), exact street addresses, or private emails..

Furthermore, resolving nested relationships (like checking a user's privacy preference to determine if an address should be masked) inside Python loops before returning API data causes massive N+1 performance bottlenecks.

## Decision
We mandate the **PostgreSQL View Security Pattern** for all public or low-privilege mass-read endpoints.

1. **SQL Masking:** Create a PostgreSQL View (`CREATE OR REPLACE VIEW...`) that mathematically strips, masks, or filters the allowed data natively in the database engine.
2. **Abstract Model:** Create a corresponding Odoo Model using `_auto = False` mapped to this view.
3. **Strict ACL Isolation:** Grant `base.group_public` (or the specific daemon) read access *strictly* to the View model.
4. **Root Revocation:** Revoke public read access from the underlying root table entirely.

## Consequences
* **Absolute Security:** It is mathematically impossible for an XML-RPC scraper to access sensitive columns because the database engine physically excludes them from the accessible view.
* **Performance:** Shifts complex N+1 calculations (like GDPR string concatenation and geographic fuzzing) directly to C-compiled PostgreSQL logic, drastically accelerating API responses.
* **Bypass Odoo ORM Limitations:** Avoids the "Framework ACL Tax" where Odoo attempts to validate parent permissions that daemons shouldn't have access to.
