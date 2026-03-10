# ADR 0064: Shadow Profile Pattern (Search Indexes)

## Status
Accepted

## Context
The platform relies heavily on background daemons and headless APIs to perform cross-user lookups (e.g., verifying API HMAC signatures, polling external bios, discovering newly granted licenses via ID correlation, or resolving website slugs).

Initially, these daemons queried the core `res.users` table using domain-specific Service Accounts. However, Odoo's native ORM contains hardcoded Python-level security checks in `res.users` that violently reject read/write operations spanning multiple users unless the executing account explicitly belongs to the `base.group_user` (Internal User) group. Granting `base.group_user` to our public-facing portal daemons violates the Zero-Sudo and Micro-Privilege mandates, as it would expose the entire internal ERP surface area to compromised external microservices.

## ## Decision
## We mandate the **Shadow Profile Pattern** to completely decouple Identity lookups from Odoo's core ERP security assumptions.

## 1. **Isolated PostgreSQL Views:** We introduce dedicated, domain-specific PostgreSQL views (e.g., `premium.user.index` or `basic.user.index`) that exist entirely outside of the `res.users` Python security hierarchy by using `_auto = False`.
## 2. **Strict Group Gating:** The views use SQL `JOIN` constraints to only expose users belonging to specific external community groups. Standard Odoo ERP users (e.g., internal company employees) are entirely excluded from the ecosystem.
## 3. **Daemon Rerouting:** All external daemons, webhooks, and APIs from external repositories MUST execute their searches against these shadow indexes, rather than querying `res.users` directly.
## 4. **The Identity Manager Proxy:** When a daemon finds a match in the index and must alter the actual user (e.g., flipping a verification flag to True), it escalates exclusively to a dedicated micro-service account (e.g., `identity_manager_service_internal`). This account is restricted and acts as a secure, one-way drawbridge between the isolated portal apps and the core ERP..

## Consequences
* Daemons remain strictly sandboxed with zero native ERP access.
* The platform no longer collides with Odoo's internal user matrix security checks.
* Because they are SQL Views, there is zero data duplication or synchronization drift, but absolute read isolation is maintained.
