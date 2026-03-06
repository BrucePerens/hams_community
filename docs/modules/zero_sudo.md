# 🛡️ Zero-Sudo Security Core (`zero_sudo`)

*Copyright © Bruce Perens K6BP. AGPL-3.0.*

**Context:** Technical documentation strictly for LLMs and Integrators.

## 1. The Zero-Sudo Mandate
This module eliminates the dangerous native `.sudo()` ORM method. It implements the Service Account pattern.

## 2. Usage
1. Create a `res.users` proxy account in XML with `is_service_account=True` (which permanently blocks web login).
2. Fetch its ID: `svc_uid = env['zero_sudo.security.utils']._get_service_uid('module.user_xml_id')`.
3. Execute: `env['model'].with_user(svc_uid).write(...)`.

## 3. Parameter Safety
`env['zero_sudo.security.utils']._get_system_param('key')` fetches parameters against a strict `frozenset` whitelist, protecting cryptographic keys from Server-Side Template Injection.

## 4. Semantic Anchors
* `[%ANCHOR: coherent_cache_signal]`, `[%ANCHOR: get_service_uid]`.
