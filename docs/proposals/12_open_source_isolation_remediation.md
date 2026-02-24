# Proposal 12: Open Source Isolation Remediation

## 1. Architectural Context
The `user_websites` module is mandated to be fully Open Source and completely isolated from the proprietary `ham_*` modules. However, it currently makes explicit calls to `env['ham.security.utils']` to execute the Proxy Ownership pattern. If a community user installs this module, it will immediately crash due to the missing `ham_base` dependency.

## 2. Integration Design

### A. Security Utility Migration
**Targets:** `user_websites/models/security_utils.py` (New), `ham_base/models/security_utils.py` (Delete/Refactor)
* **The Fix:** The Zero-Sudo `security_utils` must be migrated *down* into the `user_websites` module, effectively renaming the abstract model from `ham.security.utils` to `user_websites.security.utils`.
* **Why?** Since `user_websites` sits at the very bottom of our dependency tree (below all `ham_*` apps), placing the core security utility here allows `user_websites` to remain standalone for the community, while the proprietary `ham_*` apps can safely inherit and utilize it.

### B. Global Refactor
**Targets:** All `ham_*` modules utilizing Zero-Sudo.
* **The Fix:** A global find-and-replace to update `env['ham.security.utils']` to `env['user_websites.security.utils']` across controllers, models, and tests.
* **Dependency Updates:** Ensure `ham_base` formally declares `user_websites` in its `depends` array.

## 3. BDD Acceptance Criteria
* **Story:** As an open-source contributor, I want to install `user_websites` on a clean Odoo instance without it crashing due to missing proprietary dependencies.
    * *Given* a fresh Odoo database without `ham_base` installed
    * *When* `user_websites` is installed and a page is created
    * *Then* the Proxy Ownership pattern MUST successfully elevate using `user_websites.security.utils` without throwing a `KeyError`.
