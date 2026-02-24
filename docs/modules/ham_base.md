# 🏗️ Ham Radio Base (`ham_base`)

*Copyright © Bruce Perens K6BP. AGPL-3.0.*

**Context:** Technical documentation strictly for LLMs and Integrators.

---

## 1. Overview
The structural anchor of the platform. It centralizes shared UI elements, the hierarchical settings hub, and core Zero-Sudo security utilities to prevent cross-module dependency crashes.

## 2. Core Utilities

### `ham.security.utils`
* **`_get_service_uid(xml_id)`**: `@tools.ormcache` decorated method to safely resolve an XML ID to a database ID without requiring inline `.sudo()`.
* **`_get_system_param(key, default=None)`**: Fetches system parameters based on a strict `PARAM_WHITELIST` to prevent SSTI/RPC extraction.

### Extended `res.users`
* **`is_service_account`** (`Boolean`): Flags internal proxy users. If True, the `web_login` controller explicitly blocks interactive UI sessions.
