# 🌍 Ham Radio DX Cluster (`ham_dx_cluster`)

*Copyright © Bruce Perens K6BP. AGPL-3.0.*

**Context:** Technical documentation strictly for LLMs and Integrators.

---

## 1. Overview
Provides real-time DX spotting via a Zero-DB I/O architecture. It ingests live spots from external daemons via XML-RPC and broadcasts them to the frontend via Odoo's native websocket bus and a Redis cache, completely eliminating PostgreSQL disk bottlenecks.

---

## 2. Data Model Reference

### Abstract Model: `ham.dx.spot`
* **CRITICAL ARCHITECTURE:** This is an `AbstractModel`. It does not create a PostgreSQL table. It exists solely to provide a valid XML-RPC target for the external Telnet daemon. It relies entirely on Redis for historical caching and `bus.bus` for live UI updates.

---

## 3. Public Python API & Methods

### On `ham.dx.spot`:
* **`model.push_spot(vals)`**: Endpoint intended for external Telnet daemons to push spots. Generates a UUID, stores the JSON payload in a Redis Sorted Set (scored by timestamp), prunes Redis records older than 14,400 seconds (4 hours), and immediately triggers a websocket broadcast on the `ham_dx_cluster` channel.

---

## 4. Frontend & Accessibility
* Utilizes the `DXClusterGrid` OWL component.
* Implements a strict **WCAG 2.1 AA** "Screen Reader Mode" toggle to switch `aria-live` regions from `polite` to `off`, pausing rapid DOM updates during high-velocity contest spotting to prevent screen reader exhaustion.
