# Zero-Sudo Security Core (`zero_sudo`) - API Reference

## Purpose
The `zero_sudo` module enforces the platform's Zero-Sudo Architecture. It provides a centralized, highly secure utility for executing elevated database operations without using Odoo's native `.sudo()` method, which is prone to privilege escalation vulnerabilities. It also mathematically blocks Service Accounts from interactive web or RPC logins.

## Python API

### `zero_sudo.security.utils`
This `AbstractModel` is the only approved way to escalate privileges for system-level operations.

#### `_get_service_uid(xml_id)`
Safely retrieves the database ID of a Service Account without requiring inline `.sudo()`. The result is RAM-cached for extreme performance.
* **Arguments:**
  * `xml_id` (str): The external ID of the service account (e.g., `'your_module.your_service_account'`).
* **Returns:** `int` (The User ID).
* **Usage:**
  ```python
  svc_uid = self.env['zero_sudo.security.utils']._get_service_uid('my_module.my_service_account')
  self.env['target.model'].with_user(svc_uid).create(vals)
  ```

#### `_get_system_param(key, default=None)`
Safely retrieves a system configuration parameter (`ir.config_parameter`). The requested key MUST be hardcoded in the `PARAM_WHITELIST` within `zero_sudo/models/security_utils.py` to prevent Server-Side Template Injection (SSTI).
* **Arguments:**
  * `key` (str): The configuration parameter key.
  * `default` (any): The fallback value.
* **Returns:** `str` or the default value.

#### `_notify_cache_invalidation(model_name, key_value)`
Emits a PostgreSQL `NOTIFY` event to the `ham_cache_invalidation` channel to synchronize distributed in-memory caches across all worker nodes.
* **Arguments:**
  * `model_name` (str): The Odoo model (e.g., `'res.users'`).
  * `key_value` (str): The unique identifier (e.g., a slug or URL).
