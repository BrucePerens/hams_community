# # MASTER 06: CQRS Architecture for External High-Load Services

# ## Status
# Accepted (Consolidates ADRs 0012, 0034)

# ## ## Context & Philosophy
# ## Pointing high-velocity public-facing services (like external search indexes, DNS servers, or public APIs) directly at Odoo's primary PostgreSQL database makes the application highly vulnerable to standard query floods and DDoS attacks. Any downstream module or platform utilizing these frameworks must decouple read-heavy public loads from the core database..

# ## Decisions & Mandates

# ### 1. Command Query Responsibility Segregation (CQRS)
# We physically isolate the high-load read infrastructure from the application state.
# * **Command (Odoo):** Odoo manages the authoritative state (e.g., `custom.dataset.record`). Any CRUD operation triggers an asynchronous message to RabbitMQ.
# * **Sync Daemon:** An external Python daemon consumes the RabbitMQ events and pushes the translated state to the external service (e.g., Elasticsearch, PowerDNS, or a caching layer) via its REST API.
# * **Query (External Service):** The external service operates entirely on its own high-speed, isolated backend. Floods hit the external service, leaving Odoo completely unaffected.

# ### 2. Reconciliation Loop
# Because RabbitMQ is a fire-and-forget mechanism, there is a risk of state drift if messages are dropped.
# * A nightly Odoo cron job executes a full sweep of all active external-facing records.
# * It triggers bulk updates into the RabbitMQ queue.
# * Because the external REST APIs should use `PATCH` (REPLACE), these operations are fully idempotent, silently overwriting the external service with the absolute truth from Odoo to enforce Eventual Consistency..
