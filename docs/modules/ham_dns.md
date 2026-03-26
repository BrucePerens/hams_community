# 🌐 Ham Radio DNS (`ham_dns`)

*Copyright © Bruce Perens K6BP. AGPL-3.0.*

<system_role>
**Context:** Technical documentation strictly for LLMs and Integrators.
</system_role>

<overview>
## 1. Overview
Integrates Odoo with PowerDNS via REST API. Automatically provisions `<callsign>.hams.com` zones [@ANCHOR: provision_personal_dns_zone]. Injects its own user manual dynamically during setup. [@ANCHOR: doc_inject_ham_dns]
</overview>

<data_model>
## 2. Data Model Reference
* **Extended `res.users`**: `dns_zone_id`.
* **`ham.dns.zone`**: `name`, `owner_user_id`, `pdns_synced`.
* **`ham.dns.record`**: `zone_id`, `name`, `record_type`, `content`, `ttl`. Users can add records via the frontend UI [@ANCHOR: UX_FRONTEND_DNS_RECORD_ADD]. External routers can update dynamic records via the DynDNS2 API [@ANCHOR: ddns_update_api]. Certificate authorities can perform ACME challenges via the validation webhook [@ANCHOR: acme_challenge_api].
</data_model>

<pdns_sync_and_gdpr>
## 3. PDNS Sync & GDPR Cleanup
When a record is modified, it triggers an asynchronous RabbitMQ sync to PowerDNS [@ANCHOR: trigger_pdns_sync]. Upon GDPR account erasure, the user's DNS zones are explicitly unlinked and purged from the edge routing infrastructure to prevent dangling domain routing. [@ANCHOR: gdpr_dns_cleanup]
</pdns_sync_and_gdpr>

<dependencies>
## 4. External Dependencies
* **Python:** `pika` (Declared in `__manifest__.py`).
</dependencies>
