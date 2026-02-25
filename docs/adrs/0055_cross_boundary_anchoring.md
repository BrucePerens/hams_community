# ADR 0055: Cross-Boundary Semantic Anchoring (Odoo to Daemons)

## Status
Accepted

## Context
The Hybrid Monolith-Daemon Architecture (ADR-0001) relies heavily on decoupled communication methods such as RabbitMQ, PostgreSQL `NOTIFY`, and XML-RPC to offload heavy processing from the Odoo web workers. While this is excellent for performance, it creates a documentation gap. It is difficult for a developer to trace an event producer in Odoo to its corresponding event consumer in a background daemon without manually searching the entire codebase.

## Decision
We mandate bidirectional semantic anchoring for all interactions that cross the Odoo application and background daemon boundary.
1. **The Producer (e.g., Odoo):** Near the execution logic that fires the event, developers MUST add a comment pointing to the consumer's anchor. Example: `# Triggers [%ANCHOR: daemon_consumer_name]`.
2. **The Consumer (e.g., Daemon):** Near the handler that receives the event, developers MUST add a comment referencing the source code anchor that generated it. Example: `# Triggered by [%ANCHOR: odoo_producer_name]`.

## Consequences
* **Positive:** Restores direct traceability across distributed asynchronous workflows. Developers and AI agents can instantly navigate from a database trigger to the daemon that processes it.
* **Negative:** Requires strict maintenance when adding new background queue workers to ensure the links do not become stale or detached.
