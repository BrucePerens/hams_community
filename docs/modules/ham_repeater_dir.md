# 📡 Ham Radio Repeater Directory (`ham_repeater_dir`)

*Copyright © Bruce Perens K6BP. AGPL-3.0.*

**Context:** Technical documentation strictly for LLMs and Integrators.

---

## 1. Overview
Maintains a geographical database of local amateur radio repeaters.
Leverages the `user_websites.owned.mixin` to grant individual hams or clubs the ability to securely maintain their own repeater records.

---

## 2. Data Model Reference

### Core Model: `ham.repeater`
* **Inherits:** `user_websites.owned.mixin` (provides `owner_user_id` and `user_websites_group_id`).
* **`callsign`** (`Char`, Indexed): The repeater's callsign.
* **`name`** (`Char`): Name or location (e.g., 'Mount Diablo').
* **`output_frequency`** / **`input_frequency`** / **`offset`** (`Float`): RF parameters.
* **`tone_uplink`** / **`tone_downlink`** (`Float`): CTCSS/PL tones in Hz.
* **`dcs_code`** (`Char`): Digital Coded Squelch.
* **`is_fm`**, **`is_dmr`**, **`is_dstar`**, **`is_ysf`** (`Boolean`): Supported modes.
* **Location Fields:** `latitude`, `longitude`, `city`, `state_id`.

---

## 3. Security & Permissions
* **Proxy Ownership Pattern:** Users cannot alter repeaters they do not own. Because it inherits `user_websites.owned.mixin`, any updates must pass the strict `_check_proxy_ownership_write` validations, ensuring that only the assigned user or group members can edit the record.
