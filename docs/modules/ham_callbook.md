# 📖 Ham Radio Callbook (`ham_callbook`)

*Copyright © Bruce Perens K6BP. AGPL-3.0.*

**Context:** Technical documentation strictly for LLMs and Integrators.

---

## 1. Overview
A centralized directory for amateur radio operators holding data synced from external authorities (e.g., FCC ULS, ISED Canada).
It features strict GDPR data masking for unauthenticated or unconsented address views, as well as an automated geographic fuzzing engine for map plotting.

---

## 2. Data Model Reference

### Core Model: `ham.callbook`
* **`callsign`** (`Char`, Indexed): The operator's callsign.
* **`frn`** (`Char`, Unique): Authority Registration Number. Immutable identifier used to track operators through callsign changes.
* **`first_name`**, **`last_name`**, **`street`**, **`city`**, **`state_id`**, **`zip_code`**, **`country_id`**: Standard PII fields.
* **`license_class`**, **`grid_square`**, **`cq_zone`**, **`itu_zone`**: Ham-specific data.
* **`user_id`** (`Many2one` to `res.users`): Links the directory record to an active user in the Odoo instance.
* **`public_address`** (`Char`, Computed): A GDPR-compliant dynamically masked address.
* **`latitude`** / **`longitude`** (`Float`, Computed/Stored): Auto-calculated from the `grid_square` field using the Maidenhead locator algorithm.

---

## 3. Public Python API & Methods

### On `ham.callbook`:
* **`model.sync_fcc_batch(batch_data)`**: High-performance endpoint called by external sync daemons via XML-RPC. Accepts an array of dictionaries. Automatically maps Country/State strings to Odoo IDs, handles creations, and cascades callsign updates to linked `res.users` records.

---

## 4. Security, GDPR & Privacy Masking Rules
* **Address Masking:** Accessing `public_address` strips the `street` field unless the record is linked to a `res.users` record where `privacy_show_in_directory` is `True`.
* **Geographic Fuzzing:** The `_compute_coordinates` method evaluates the Maidenhead `grid_square` into decimal latitude/longitude. If the linked user has not explicitly set `privacy_show_in_directory` to `True`, the algorithm artificially truncates the user's grid square to 4 characters before calculation. This drops the map pin in the mathematical center of a ~70x100 mile box, making it impossible to deduce their home address from the map UI, while still allowing for regional querying.
