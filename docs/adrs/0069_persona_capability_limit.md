# ADR 0069: Persona Capability Limit & View Abstraction

## Status
Accepted

## Context
Controllers, widgets, and APIs frequently need to present aggregated or masked data (e.g., Usage Statistics, fuzzed geographic locations, or active resource lists) to public guests or unprivileged standard users.

Previously, to fetch this data, the system escalated privileges by invoking a Micro-Service Account (e.g., `with_user(svc_uid)`) to query the restricted root tables (`core.transaction`, `core.directory`). The Python controller would then manually count the records or mask the sensitive fields (like exact street addresses) before returning the JSON response.

This violates the principle of least privilege. Escalating to a Service Account pulls highly sensitive, restricted data into the Python WSGI worker's memory during a public request. If the controller logic contains a flaw, that sensitive data could be leaked to an unauthorized persona.

## Decision
We mandate the **Persona Capability Limit**: We do not increase privilege beyond the capability of the persona requesting the data, unless there is absolutely no other programmatic way to achieve the task (e.g., cryptographic signing or cross-domain writes).

To present restricted data to an unprivileged persona, you MUST use a PostgreSQL View (`_auto = False`) to sanitize, aggregate, or mask the data at the database layer.

1.  **Shift-Left Masking:** The SQL `CREATE VIEW` statement is responsible for stripping PII, truncating location coordinates, or counting rows.
2.  **Native ACLs:** The unprivileged persona (e.g., `base.group_public` or `base.group_portal`) is granted native `perm_read=1` access explicitly to this new View model via `ir.model.access.csv`.
3.  **Zero Escalation:** The Python controller executes the `.search()` or `.read_group()` natively as the requesting user (`request.env.user`), completely dropping the `with_user()` Service Account escalation.

## Consequences
* **Security:** It is mathematically impossible for the Python controller to accidentally leak an exact address or private email because the database engine physically excludes that data from the View. Sensitive data never enters the WSGI worker's memory.
* **Performance:** Shifts complex N+1 Python masking and counting loops directly into C-compiled PostgreSQL logic.
* **Service Account Purity:** Service Accounts are reserved strictly for cross-domain writes, state mutations, and cryptographic execution, drastically reducing their exposure footprint.
