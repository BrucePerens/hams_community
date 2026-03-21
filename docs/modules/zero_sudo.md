# 🛡️ Zero-Sudo Security Core (`zero_sudo`)

*Copyright © Bruce Perens K6BP. AGPL-3.0.*

**Context:** Technical documentation strictly for LLMs and Integrators.

## 1. The Zero-Sudo Mandate
This module eliminates the dangerous native `.sudo()` ORM method. It implements the Service Account pattern.

## 2. Usage & Utilities
1. Create a `res.users` proxy account in XML with `is_service_account=True` (which permanently blocks web login).
2. Fetch its ID: `svc_uid = env['zero_sudo.security.utils']._get_service_uid('module.user_xml_id')`. This securely resolves the Service Account ID. [@ANCHOR: get_service_uid]
3. Execute: `env['model'].with_user(svc_uid).write(...)`.

**Parameter Safety:** `env['zero_sudo.security.utils']._get_system_param('key')` fetches parameters against a strict `frozenset` whitelist, protecting cryptographic keys from Server-Side Template Injection.

**Coherent Caching:** The utility provides `_notify_cache_invalidation` which emits a PostgreSQL `NOTIFY` event to synchronize distributed caches across workers. [@ANCHOR: coherent_cache_signal]

## 3. Centralized Shared Service Accounts (The ERP Bridge)
To comply with the Micro-Privilege Mandate, domain-specific service accounts MUST NOT hold `base.group_user` (Internal User). When native ERP interaction is required, code MUST proxy through one of these two centralized accounts:

* **Central Mail Service Account (`zero_sudo.mail_service_internal`):** Holds `base.group_user` and explicit ACLs for `mail.*` models. Use this exclusively for `message_post()` and `send_mail()` calls.
* **Odoo Facility Service Account (`zero_sudo.odoo_facility_service_internal`):** Holds `base.group_user`. Use this for deep framework cascades that cannot be satisfied by the mail proxy or a local micro-service ACL.
