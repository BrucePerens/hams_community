# 🏗️ Ham Radio Base (`ham_base`)

*Copyright © Bruce Perens K6BP. AGPL-3.0.*

<system_role>
**Context:** Technical documentation strictly for LLMs and Integrators.
</system_role>

<overview>
## 1. Overview
This module anchors the platform. It centralizes shared UI parts, the settings hub, and the Zero-Sudo security utilities so other modules don't crash into each other.
</overview>

<core_utilities>
## 2. Core Utilities
* **`zero_sudo.security.utils`**:
  * **`_get_service_uid(xml_id)`**: `@tools.ormcache` decorated method to safely resolve an XML ID to a database ID without requiring inline `.sudo()`.
  * **`_get_system_param(key, default=None)`**: Fetches system parameters based on a strict `PARAM_WHITELIST` to prevent SSTI/RPC extraction.
* **Extended `res.users`**:
  * **`is_service_account`** (`Boolean`): Flags internal proxy users. If True, the `web_login` controller explicitly blocks interactive UI sessions.
</core_utilities>

<administrative_actions>
## 3. Administrative Actions
Administrators can securely impersonate users to troubleshoot dashboard states without requiring their passwords. [@ANCHOR: action_impersonate_user] Automated testing mathematically guarantees this functionality generates the required immutable audit log in the target user's chatter history before permitting the session swap. [@ANCHOR: test_impersonation]
</administrative_actions>

<dependencies>
## 4. External Dependencies
* **Python:** `pgeocode` (Declared in `__manifest__.py`).
</dependencies>
