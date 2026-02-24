# ADR 0036: Public Guest User Access Control (No-Sudo Forms)

## Status
Accepted

## Context
When an unauthenticated user submits data via a public website form (such as an event correction report or a contact form), Odoo controllers typically require the developer to use `.sudo().create()` because the guest user lacks native database permissions. This is a severe anti-pattern. If the controller payload is not strictly validated, an attacker can use RPC mass-assignment to inject malicious data using the system's absolute administrative privileges.

## Decision
Public-facing form ingestion MUST NOT use `.sudo()`.

Instead, modules must utilize the "Public Guest User" idiom:
1. Define the data model intended to receive the form data.
2. In the module's `ir.model.access.csv`, explicitly grant `perm_create=1` to `base.group_public` for that specific model.
3. The controller can then execute `request.env['target.model'].create(vals)` naturally, relying on the PostgreSQL database and ORM to strictly sandbox the transaction to creation-only.

## Consequences
* **Positive:** Eliminates controller-level privilege escalation. Completely neutralizes the threat of arbitrary data manipulation via mass-assignment on public routes.
* **Negative:** Requires creating dedicated staging models (like `ham.event.issue`) to receive the public data, rather than allowing public users to directly append data to core models (like `event.event`).
