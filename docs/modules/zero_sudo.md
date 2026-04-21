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
2. **Remove Redundant Login Interceptors:** Delete any custom `web_login` controller overrides in your proprietary modules. The `zero_sudo` module now centrally natively intercepts interactive web logins and blocks access for accounts where `is_service_account=True`. Redundant interceptors will cause routing conflicts. *(Note: This lock only applies to the HTML web interface; XML-RPC and JSON-RPC interfaces remain open for your external background daemons).*
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

* **Cache & Resolution:** `_get_service_uid` `[@ANCHOR: get_service_uid]` safely resolves and caches the service account UID to prevent redundant database hits. This logic is verified by `[@ANCHOR: test_get_service_uid]`.
</service_account_pattern>

---

<system_parameters>
## 2. System Parameter Whitelisting

If you need to fetch a configuration parameter securely:
`value = self.env['zero_sudo.security.utils']._get_system_param('my.key')` `[@ANCHOR: get_system_param]`

**CRITICAL:** The key MUST be explicitly added to the `PARAM_WHITELIST` array in `zero_sudo/models/security_utils.py`. Cryptographic keys (like `database.secret`) are permanently banned from this whitelist to prevent Server-Side Template Injection (SSTI) exposure. If you need to access cryptographic keys, you MUST use `self.env['zero_sudo.security.utils']._get_crypto_secret()` `[@ANCHOR: get_crypto_secret]`.
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

<global_cache>
## 4. Global Cache Signaling
* **Postgres NOTIFY Bus:** The `_notify_cache_invalidation` function `[@ANCHOR: coherent_cache_signal]` provides an entry point to trigger cross-worker cache flushes via the distributed event bus, guaranteeing consistency in clustered setups. This behavior is covered by `[@ANCHOR: test_coherent_cache_signal]`.
</global_cache>

---

<stories_and_journeys>
## 5. Architectural Stories & Journeys

For detailed narratives and end-to-end workflows, refer to the following:

### Stories
* **Secure Privilege Escalation** `[@ANCHOR: story_secure_escalation]`: Narrative on how developers securely escalate privileges using service accounts instead of `.sudo()`. [Read Story](docs/stories/zero_sudo/secure_escalation.md)
* **Blocking Service Account Login** `[@ANCHOR: story_login_blocking]`: How the system prevents service accounts from accessing the interactive web interface. [Read Story](docs/stories/zero_sudo/login_blocking.md)
* **Parameter Whitelisting** `[@ANCHOR: story_parameter_whitelisting]`: Protection of sensitive system parameters from unauthorized access. [Read Story](docs/stories/zero_sudo/parameter_whitelisting.md)
* **Coherent Cache Signaling** `[@ANCHOR: story_cache_signaling]`: Ensuring cache consistency across multiple Odoo workers using Postgres NOTIFY. [Read Story](docs/stories/zero_sudo/cache_signaling.md)
* **Deterministic Hashing** `[@ANCHOR: story_deterministic_hash]`: Generation of stable integer hashes for PostgreSQL advisory locks. [Read Story](docs/stories/zero_sudo/deterministic_hashing.md)
* **Python VENV Management** `[@ANCHOR: story_venv_management]`: How administrators can trigger updates of system Python dependencies safely. [Read Story](docs/stories/zero_sudo/venv_management.md)

### Journeys
* **Service Account Lifecycle** `[@ANCHOR: journey_service_account_lifecycle]`: The end-to-end flow of a service account from provisioning to secure execution. [Read Journey](docs/journeys/zero_sudo/service_account_lifecycle.md)
* **Securing Configuration Parameters** `[@ANCHOR: journey_securing_configuration]`: The workflow for safely integrating and accessing new configuration parameters. [Read Journey](docs/journeys/zero_sudo/securing_configuration.md)
</stories_and_journeys>

---

<additional_features>
## 5. Additional Utilities

### Deterministic Hashing
* **Function:** `_get_deterministic_hash` `[@ANCHOR: deterministic_hash]`
* **Use Case:** Generating stable integer hashes for PostgreSQL advisory locks.

### VENV Management
* **Function:** `_update_python_venv` `[@ANCHOR: update_python_venv]`
* **Use Case:** Triggering `pip install` for module dependencies (restricted to Administrators).

### Web Login Security
* **Field:** `is_service_account` `[@ANCHOR: is_service_account_field]` on `res.users`.
* **Interceptor:** `web_login` `[@ANCHOR: web_login_interceptor]` in `Home` controller.
* **Security Check:** Performs direct SQL check `[@ANCHOR: web_login_interceptor_check]` for isolation.
* **Effect:** Prevents interactive web logins for any user flagged as a service account.
</additional_features>
