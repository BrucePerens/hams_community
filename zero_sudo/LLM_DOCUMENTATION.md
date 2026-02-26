# 🛡️ Zero-Sudo Security Core (`zero_sudo`)

**Context:** Technical documentation strictly for LLMs and Integrators developing proprietary (`hams_private`) or Open Source modules.

This module acts as the foundational security layer for the entire ecosystem. It implements the platform's strict **Zero-Sudo Architecture** (ADR-0002) and **Service Account Web Isolation** (ADR-0005).

---

## 🚨 MIGRATION INSTRUCTIONS FOR PROPRIETARY MODULES (`ham_*`)

If you are an AI or developer working on the proprietary layer (e.g., `ham_base`, `ham_logbook`, `ham_dx_cluster`), you **MUST** perform the following migrations to integrate with this core:

1. **Change Dependencies:** Add `'zero_sudo'` to the `depends` array in your `__manifest__.py`.
2. **Remove Redundant Login Interceptors:** Delete any custom `web_login` controller overrides in your proprietary modules (e.g., inside `ham_base`). The `zero_sudo` module now centrally natively intercepts interactive web logins and blocks access for accounts where `is_service_account=True`. Redundant interceptors will cause routing conflicts. *(Note: This lock only applies to the HTML web interface; XML-RPC and JSON-RPC interfaces remain open for your external background daemons).*
3. **Update Security Utility Calls:** Globally find-and-replace your utility calls to use the new centralized namespace:
   * **Change:** `self.env['ham.security.utils']._get_service_uid(...)`
   * **To:** `self.env['zero_sudo.security.utils']._get_service_uid(...)`
4. **Service Account XML Provisioning:** You may safely continue to use `<field name="is_service_account" eval="True"/>` in your XML data files without crashing, as the structural field is natively defined by this module.

---

## 1. The Service Account Pattern

You are strictly FORBIDDEN from using `.sudo()` inline. To escalate privileges:
1. Define your service account in your module's XML data and set `<field name="is_service_account" eval="True"/>`.
2. Retrieve its UID securely:
   `svc_uid = self.env['zero_sudo.security.utils']._get_service_uid('your_module.user_xml_id')`
3. Execute using the impersonation idiom:
   `self.env['target.model'].with_user(svc_uid).create(vals)`

---

## 2. System Parameter Whitelisting

If you need to fetch a configuration parameter securely:
`value = self.env['zero_sudo.security.utils']._get_system_param('my.key')`

**CRITICAL:** The key MUST be explicitly added to the `PARAM_WHITELIST` array in `zero_sudo/models/security_utils.py`. Cryptographic keys (like `database.secret`) are permanently banned from this whitelist to prevent Server-Side Template Injection (SSTI) exposure.

---

## 3. 🔗 Semantic Anchors
* `get_service_uid` / `test_get_service_uid`: Service account resolution and cache.
* `coherent_cache_signal` / `test_coherent_cache_signal`: Global Postgres NOTIFY bus trigger.
