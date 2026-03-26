# 📖 Ham Radio Callbook (`ham_callbook`)

*Copyright © Bruce Perens K6BP. AGPL-3.0.*

<system_role>
**Context:** Technical documentation strictly for LLMs and Integrators.
</system_role>

<overview>
## 1. Overview
A centralized directory for amateur radio operators holding data synced from external authorities (e.g., FCC ULS, ISED Canada). It injects its technical manual payload into the Knowledge base automatically upon initialization. [@ANCHOR: doc_inject_ham_callbook]
</overview>

<data_model>
## 2. Data Model Reference (`ham.callbook`)
* **`callsign`** (`Char`, Indexed)
* **`frn`** (`Char`, Unique): Authority Registration Number.
* **`user_id`** (`Many2one` to `res.users`): Links the directory record to an active user.
* **`public_address`** (`Char`, Computed): A GDPR-compliant dynamically masked address.
* **`latitude`** / **`longitude`** (`Float`, Computed/Stored): Auto-calculated from the `grid_square` using Maidenhead.
</data_model>

<caching_and_sync>
## 3. Caching, Sync & Presentation
* **`model.sync_fcc_batch(batch_data)`**: High-performance JSON-RPC endpoint for sync daemons.
* **Distributed Coherence:** When a callbook record is updated [@ANCHOR: callbook_cache_invalidation] or deleted [@ANCHOR: callbook_cache_invalidation_unlink], the system immediately broadcasts an invalidation payload to the distributed Redis cache to ensure the UI stays synchronized.
* **Map Presentation:** Geographically fuzzed coordinates are safely exposed to frontend components (like the community map) via a specialized SQL view [@ANCHOR: render_fuzzed_map].
</caching_and_sync>

<privacy_and_routing>
## 4. Privacy & Routing
* High-performance batch syncing [@ANCHOR: odoo_sync_fcc_batch].
* Masks street addresses [@ANCHOR: gdpr_address_masking].
* Fuzzes geographic coordinates [@ANCHOR: geographic_fuzzing].
</privacy_and_routing>

<dependencies>
## 5. External Dependencies
* **Python:** None (Declared in `__manifest__.py`).
</dependencies>
