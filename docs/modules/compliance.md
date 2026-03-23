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
