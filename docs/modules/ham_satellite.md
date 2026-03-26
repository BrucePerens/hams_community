# 🛰️ Ham Radio Satellite Tracker (`ham_satellite`)

*Copyright © Bruce Perens K6BP. AGPL-3.0.*

<system_role>
**Context:** Technical documentation strictly for LLMs and Integrators.
</system_role>

<overview>
## 1. Overview
Live pass predictions calculated locally using the `ephem` library. Deploys satellite operational manuals during initialization. [@ANCHOR: doc_inject_ham_satellite]
Provides live AMSAT satellite pass predictions calculated locally via ephem. [@ANCHOR: UX_FRONTEND_SATELLITE_TRACKER]
Calculates orbital events locally against stored TLEs. [@ANCHOR: calculate_satellite_passes]
</overview>

<data_model>
## 2. Data Model (`ham.satellite.tle`)
* Stores `line1` and `line2` parameters from AMSAT.
* **Cache Control:** When AMSAT data syncs from the background daemon [@ANCHOR: odoo_sync_tles], the module explicitly invalidates TLE caches across the platform to ensure immediate precision updates. [@ANCHOR: satellite_tle_cache_invalidation]
</data_model>

<dependencies>
## 3. External Dependencies
* **Python:** `ephem`, `redis` (Declared in `__manifest__.py`).
</dependencies>
