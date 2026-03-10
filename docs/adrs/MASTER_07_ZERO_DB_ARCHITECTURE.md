# MASTER 07: Zero-DB Architecture

## Status
Accepted (Consolidates ADRs 0003, 0032)

## Context & Philosophy
During peak usage, external telemetry networks generate an extreme velocity of event reports. Writing every incoming event to a relational PostgreSQL table causes massive disk I/O churn and index fragmentation, degrading the entire ERP.

## Decisions & Mandates

### ### ### 1. Ephemeral Memory Routing
### ### Any high-velocity ingestion engine (e.g., `high.velocity.event` or `sensor.data.stream` within a downstream module) MUST be implemented as an Odoo `AbstractModel`. It acts purely as a memory router...
* It intercepts incoming XML-RPC payloads.
* It validates the payload and pushes it directly to a Redis Sorted Set (for short-term historical caching) and the Odoo WebSocket Bus (`bus.bus`) for real-time UI updates.
* It explicitly DOES NOT execute PostgreSQL `INSERT` statements.

### 2. UI Exemption
Because `AbstractModels` do not possess backing database tables, standard Odoo List, Kanban, and Search views cannot query this data.
* Ephemeral data models are explicitly exempt from requiring standard Odoo backend UI facilities.
* Historical searching is handled exclusively by the 4-hour Redis cache and the specialized OWL frontend component.
