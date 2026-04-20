# 🗄️ Global Compliance Module (`compliance`)

*Copyright © Bruce Perens K6BP. AGPL-3.0.*

<system_role>
**Context:** Technical documentation strictly for LLMs and Integrators.
</system_role>

<enforcement_details>
## 1. Overview
A non-interactive configuration module that enforces baseline regulatory compliance across the Odoo instance upon installation.

## 2. Enforcement Details
* Programmatically enables the Odoo `website` native `cookies_bar` boolean.
* Provisions AGPL-3 compatible legal pages (`/privacy`, `/cookie-policy`, `/terms`) safely via `noupdate="1"` XML records.
* **CRITICAL:** Custom modules MUST NOT implement custom cookie banners. They must utilize the core framework's consent state.
</enforcement_details>

<security_architecture>
## 3. Security & Zero-Sudo
This module adheres to **ADR-0002 (Zero-Sudo)** and **ADR-0005 (Service Account Web Isolation)**.

* **Micro-Privilege Account:** Automated post-install configuration is executed via the `compliance.user_compliance_service` service account.
* **ACLs:** The service account is granted minimal read/write access to `website`, `website.page`, and `ir.ui.view` models.
* **Impersonation:** Escalation is handled via `env.with_user(svc_uid)` instead of `.sudo()` for core operations.

## 4. Documentation Installation
This module implements a **soft dependency** on documentation providers (`manual_library` or Odoo Enterprise `knowledge`).

* **Mechanism:** Documentation is installed via `post_init_hook` and dynamically verified on every registry reload via `compliance.config._register_hook`.
* **Elevation:** Since these are soft dependencies, article creation is executed via `.sudo()` to bypass the absence of static ACLs for external models.
* **Models Supported:** `knowledge.article`, `manual.article`.
* **Article Title:** "Site Owner's Guide to Regulatory Compliance"
</security_architecture>
