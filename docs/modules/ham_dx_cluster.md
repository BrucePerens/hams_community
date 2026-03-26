# 🌍 Ham Radio DX Cluster (`ham_dx_cluster`)

*Copyright © Bruce Perens K6BP. AGPL-3.0.*

<system_role>
**Context:** Technical documentation strictly for LLMs and Integrators.
</system_role>

<overview>
## 1. Overview
Provides real-time DX spotting via a Zero-DB I/O architecture. Installs user-facing documentation payload into Knowledge. [@ANCHOR: doc_inject_ham_dx_cluster]
</overview>

<architecture>
## 2. Architecture
* **`ham.dx.spot`**: This `AbstractModel` intercepts JSON-RPC payloads from Telnet daemons. [@ANCHOR: telnet_push_spot] It pushes directly to Redis and the WebSocket Bus [@ANCHOR: memory_router_push], skipping PostgreSQL entirely to avoid disk bottlenecks.
* It automatically prunes Redis to remove spots older than 4 hours. [@ANCHOR: cron_prune_dx_redis]
* **WCAG 2.1 AA Compliance**: Frontend components include screen-reader toggles to disable live `aria-live` updates during high-velocity contests. [@ANCHOR: UX_A11Y_ARIA_LIVE_TOGGLE] Frontend components include a websocket pause toggle. [@ANCHOR: websocket_pause_toggle]
</architecture>

<dependencies>
## 3. External Dependencies
* **Python:** `redis` (Declared in `__manifest__.py`).
</dependencies>
