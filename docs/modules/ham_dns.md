# 🌐 Ham Radio DNS (`ham_dns`)

*Copyright © Bruce Perens K6BP. AGPL-3.0.*

**Context:** Technical documentation strictly for LLMs and Integrators.

---

## 1. Overview
Integrates Odoo with an external PowerDNS (PDNS) server via REST API.
It automatically provisions `<callsign>.hams.com` zones for verified users and provides a portal dashboard for them to manage their DNS records.

---

## 2. Data Model Reference

### Extended `res.users`
* **`dns_zone_id`** (`Many2one` to `ham.dns.zone`): The user's personal assigned DNS zone.

### Core Model: `ham.dns.zone`
* **`name`** (`Char`): The FQDN of the zone (e.g., `k6bp.hams.com.`).
* **`owner_user_id`** (`Many2one` to `res.users`): The owner of the zone.
* **`pdns_synced`** (`Boolean`): Whether the zone has been successfully created in the PDNS server.

### Core Model: `ham.dns.record`
* **`zone_id`** (`Many2one` to `ham.dns.zone`): The parent zone.
* **`name`** (`Char`): The prefix or `@` for root.
* **`record_type`** (`Selection`): `A`, `AAAA`, `CNAME`, `TXT`, `MX`.
* **`content`** (`Char`): The target IP or text.
* **`ttl`** (`Integer`): Time to live in seconds.
* **`priority`** (`Integer`): For MX records.

---

## 3. PowerDNS API Integration Mechanics
* **Zone Creation:** Executed via `POST /api/v1/servers/localhost/zones`.
* **Record Updates:** Executed via `PATCH /api/v1/servers/localhost/zones/{zone_name}`.
When *any* record is created, modified, or deleted in Odoo, the `sync_records_to_pdns()` method groups all records for the zone into RRSets (Resource Record Sets) and sends a `REPLACE` payload to PDNS, ensuring Odoo remains the absolute source of truth.
