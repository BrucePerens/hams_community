# MASTER 01: Security & Zero-Sudo Architecture

## Status
Accepted (Consolidates ADRs 0002, 0005, 0013, 0039)

## Context & Philosophy
Odoo's native `.sudo()` method grants absolute database rights, bypassing Access Control Lists (ACLs) and Record Rules. This is a dangerous anti-pattern that frequently leads to privilege escalation vulnerabilities. The Hams.com platform strictly enforces a Zero-Sudo architecture to ensure least-privilege execution across all boundaries.

## Decisions & Mandates

### 1. The Service Account Pattern
When elevated privileges are required, the system MUST NOT use `.sudo()`. Instead:
1. Identify or create a specifically crafted Service Account (e.g., `user_dns_api_service`).
2. Retrieve its UID securely using the centralized security utility.
3. Execute the operation using the `with_user(svc_uid)` impersonation idiom.

### 2. Service Account Web Isolation
To prevent leaked daemon credentials from being used interactively:
* All Service Accounts MUST be flagged with `is_service_account=True`.
* The `web_login` controller intercepts logins and instantly destroys the session if a Service Account attempts to access the frontend UI.
* **Open Source Compatibility:** The central `zero_sudo` module provides this field and logic natively to the open-source layer, ensuring both proprietary and community modules benefit from absolute daemon isolation without breaking external RPC integration.

### 3. Centralized Security Utility
All allowed privilege escalations (such as resolving XML IDs or fetching configuration parameters) MUST route through `ham.security.utils`:
* `_get_service_uid(xml_id)`: Safely resolves Service Account IDs.
* `_get_system_param(key)`: Fetches parameters against a strict `frozenset` whitelist. Cryptographic keys are explicitly excluded to prevent QWeb extraction (SSTI).

### 4. Strict Linter Bypass Confinement (ADR-0052)
Generic `# burn-ignore` tags are strictly prohibited. The bypass comment MUST specify the exact rule or pattern being bypassed (e.g., `# burn-ignore-sudo`, `# audit-ignore-mail`, `# audit-ignore-search`).

Furthermore, ANY bypassed line MUST include an inline comment cross-referencing the specific Semantic Anchor of the automated unit test that validates it (e.g., `# burn-ignore-sudo: Tested by [%ANCHOR: example_unique_name]`).

The `# burn-ignore-sudo` directive is strictly confined to two exact operations:
1. Cryptographic Fetching: `.sudo().get_param('database.secret')`
2. GDPR Erasure Cascades: `.sudo().unlink()` (As defined in Master 02).

**Audit Bypass Tags:**
To silence false-positive architectural warnings, developers and AI agents may use specific `audit-ignore` tags, provided they have manually verified the underlying logic AND provided the mandatory test anchor:
* ``: Allowed on `ir.cron` XML records ONLY if the test proves the Python method utilizes `_trigger()` loop batching.
* `# audit-ignore-mail: Tested by [%ANCHOR: example_unique_name]`: Allowed on `send_mail()` calls ONLY if the test proves the target template's `model_id` matches.
* `# audit-ignore-search: Tested by [%ANCHOR: example_unique_name]`: Allowed on `.search()` calls ONLY if the test proves the search does not introduce an OOM vector or bypass a required uniqueness check.
Inventing or using unauthorized bypass tags, or omitting the test anchor, constitutes a critical security violation.
