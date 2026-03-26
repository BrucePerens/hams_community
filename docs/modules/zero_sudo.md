# 🛡️ Zero-Sudo Security Core (`zero_sudo`)

<system_role>
**Context:** Technical documentation strictly for LLMs and Integrators developing custom downstream modules or Open Source apps...

This module acts as the foundational security layer for the entire ecosystem. It implements the platform's strict **Zero-Sudo Architecture** (ADR-0002) and **Service Account Web Isolation** (ADR-0005).
</system_role>

---

<migration_instructions>
## 🚨 MIGRATION INSTRUCTIONS FOR DEPENDENT MODULES

If you are an AI or developer working on downstream modules, you **MUST** perform the following migrations to integrate with this core:

1. **Change Dependencies:** Add `'zero_sudo'` to the `depends` array in your `__manifest__.py`.
2. **Remove Redundant Login Interceptors:** Delete any custom `web_login` controller overrides in your proprietary modules. The `zero_sudo` module now centrally natively intercepts interactive web logins and blocks access for accounts where `is_service_account=True`.
2. **Remove Redundant Login Interceptors:** Delete any custom `web_login` controller overrides in your proprietary modules. Redundant interceptors will cause routing conflicts. *(Note: This lock only applies to the HTML web interface; JSON-RPC interfaces remain open for your external background daemons).*).*
3. **Update Security Utility Calls:** Globally find-and-replace your utility calls to use the new centralized namespace:
   * **Change:** `self.env['custom.security.utils']._get_service_uid(...)`
   * **To:** `self.env['zero_sudo.security.utils']._get_service_uid(...)`
4. **Service Account XML Provisioning:** You may safely continue to use `<field name="is_service_account" eval="True"/>` in your XML data files without crashing, as the structural field is natively defined by this module.
</migration_instructions>

---

<service_account_pattern>
## 1. The Service Account Pattern

You are strictly FORBIDDEN from using `.sudo()` inline. To escalate privileges:
1. Define your service account in your module's XML data and set `<field name="is_service_account" eval="True"/>`.
2. Retrieve its UID securely:
   `svc_uid = self.env['zero_sudo.security.utils']._get_service_uid('your_module.user_xml_id')`
3. Execute using the impersonation idiom:
   `self.env['target.model'].with_user(svc_uid).create(vals)`
</service_account_pattern>

---

<system_parameters>
## 2. System Parameter Whitelisting

If you need to fetch a configuration parameter securely:
`value = self.env['zero_sudo.security.utils']._get_system_param('my.key')`

**CRITICAL:** The key MUST be explicitly added to the `PARAM_WHITELIST` array in `zero_sudo/models/security_utils.py`. Cryptographic keys (like `database.secret`) are permanently banned from this whitelist to prevent Server-Side Template Injection (SSTI) exposure.
</system_parameters>

---

<shared_service_accounts>
## 3. Centralized Shared Service Accounts (The ERP Bridge)

In accordance with ADR-0064 and the Micro-Privilege Mandate, domain-specific service accounts (like those in `pager_duty` or `backup_management`) MUST NOT be granted `base.group_user` (Internal User). Doing so exposes the entire ERP backend to external daemons.

When a daemon or unprivileged user strictly requires native ERP framework interactions that mandate `base.group_user`, they MUST temporarily drop their context and assume one of the two centralized proxy accounts provided by `zero_sudo`:

### A. Central Mail Service Account
* **XML ID:** `zero_sudo.mail_service_internal`
* **Privileges:** Holds `base.group_user`. Granted explicit `1,1,1,0` ACLs to `mail.message`, `mail.mail`, `mail.template`, and `res.partner`. It is also granted `1,1,1,1` (unlink) to `mail.followers`, and read-only (`1,0,0,0`) to `res.users`, `res.company`, and `mail.alias.domain`.
* **Use Case:** You MUST use this account exclusively when your code needs to execute `message_post()`, `send_mail()`, or interact with the `mail.thread` chatter.

### B. Odoo Facility Service Account
* **XML ID:** `zero_sudo.odoo_facility_service_internal`
* **Privileges:** Holds `base.group_user`.
* **Use Case:** You MUST use this account exclusively when an Odoo framework cascade deeply assumes internal user rights (e.g., complex ORM object creations that trigger deep backend evaluations) and the operation cannot be satisfied by the Mail Service Account or a local micro-service ACL.
</shared_service_accounts>

---

<semantic_anchors>
## 4. 🔗 Semantic Anchors
* `[@ANCHOR: get_service_uid]` / `[@ANCHOR: test_get_service_uid]`: Service account resolution and cache.
* `[@ANCHOR: coherent_cache_signal]` / `[@ANCHOR: test_coherent_cache_signal]`: Global Postgres NOTIFY bus trigger.
</semantic_anchors>
