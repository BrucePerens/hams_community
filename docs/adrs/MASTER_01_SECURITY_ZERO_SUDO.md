# MASTER 01: Security & Zero-Sudo Architecture

## Status
Accepted (Consolidates ADRs 0002, 0005, 0013, 0039, 0062)

## Context & Philosophy
Odoo's native `.sudo()` method grants absolute database rights, bypassing Access Control Lists (ACLs) and Record Rules. This is a dangerous anti-pattern that frequently leads to privilege escalation vulnerabilities. The Hams.com platform strictly enforces a Zero-Sudo architecture to ensure least-privilege execution across all boundaries.

## Decisions & Mandates

### 1. The Service Account Pattern
When elevated privileges are required, the system MUST NOT use `.sudo()`. Instead:
1. Identify or create a specifically crafted Service Account (e.g., `user_dns_api_service`).
2. Retrieve its UID securely using the centralized security utility.
3. Execute the operation using the `with_user(svc_uid)` impersonation idiom.

**Separation of Privilege (Micro-Service Accounts):** Disparate permissions MUST NOT be bundled into monolithic, omnipotent service accounts, and you MUST NOT fall back to `base.user_admin` for automated tasks. When a brief privilege-raise is necessary to cross a domain boundary (e.g., sending an email or exporting GDPR data across restricted tables), the system MUST temporarily assume a highly specialized micro-service account (like `mail_service_internal`, `gdpr_service_internal`, or `config_service_internal`) dedicated exclusively to that exact flow. This ensures the general execution continues at a lower privilege and strictly limits the blast radius of any individual proxy account.

**The Framework ACL Tax (Micro-Service Caveat):** By deliberately removing the monolithic `base.group_user` from Service Accounts to secure them, you will expose hidden core framework dependencies. If your service account interacts with `res.users` or models inheriting `mail.thread` (chatter), the ORM will silently attempt to cascade reads to underlying tables. You MUST explicitly grant your Service Account microscopic read/write ACLs to `res.company`, `mail.message`, `discuss.channel.member`, and `mail.alias.domain` in your `ir.model.access.csv` to prevent `AccessError` transaction crashes.

### 2. Service Account Web Isolation
To prevent leaked daemon credentials from being used interactively:
* All Service Accounts MUST be flagged with `is_service_account=True`.
* The `web_login` controller intercepts logins and instantly destroys the session if a Service Account attempts to access the frontend UI.
* **Open Source Compatibility:** The central `zero_sudo` module provides this field and logic natively to the open-source layer, ensuring both proprietary and community modules benefit from absolute daemon isolation without breaking external RPC integration.

### 3. Centralized Security Utility
All allowed privilege escalations (such as resolving XML IDs or fetching configuration parameters) MUST route through `zero_sudo.security.utils`:
* `_get_service_uid(xml_id)`: Safely resolves Service Account IDs.
* `_get_system_param(key)`: Fetches parameters against a strict `frozenset` whitelist. Cryptographic keys are explicitly excluded to prevent QWeb extraction (SSTI).

### 4. Persona Capability Limit & View Abstraction (ADR-0068, ADR-0069)
We do not increase privilege beyond the capability of the persona requesting the data, unless there is absolutely no other way. 

To present restricted, masked, or aggregated data to an unprivileged user (e.g., public directories, maps, or statistics), you MUST NOT use a Service Account to fetch the raw records and mask them in Python. 

Instead, create a PostgreSQL View (`_auto = False`) that strictly selects only the safe columns or applies SQL-level masking. Grant the public/portal persona read access exclusively to the View via `ir.model.access.csv`, and execute the read natively without privilege escalation. Sensitive data must never enter the WSGI worker's memory during an unprivileged request.

### 5. Strict Linter Bypass Confinement (ADR-0052)
Generic `# burn-ignore` tags are strictly prohibited. The bypass comment MUST specify the exact rule or pattern being bypassed (e.g., `# burn-ignore-sudo`, `# audit-ignore-mail`, `# audit-ignore-search`).

Furthermore, ANY bypassed line MUST include an inline comment cross-referencing the specific Semantic Anchor of the automated unit test that validates it (e.g., `# burn-ignore-sudo: Tested by [%ANCHOR: example_unique_name]`).

The `# burn-ignore-sudo` directive is strictly confined to a single operation:
1. Cryptographic Fetching: `.sudo().get_param('database.secret')`

**Audit Bypass Tags:**
To silence false-positive architectural warnings, developers and AI agents may use specific `audit-ignore` tags, provided they have manually verified the underlying logic AND provided the mandatory test anchor:
* ``: Allowed on `ir.cron` XML records ONLY if the test proves the Python method utilizes `_trigger()` loop batching.
* `# audit-ignore-mail: Tested by [%ANCHOR: example_unique_name]`: Allowed on `send_mail()` calls ONLY if the test proves the target template's `model_id` matches.
* `# audit-ignore-search: Tested by [%ANCHOR: example_unique_name]`: Allowed on `.search()` calls ONLY if the test proves the search does not introduce an OOM vector or bypass a required uniqueness check.
Inventing or using unauthorized bypass tags, or omitting the test anchor, constitutes a critical security violation.
