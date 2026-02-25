# Zero-Sudo Security Core (`zero_sudo`)

*Copyright © Bruce Perens K6BP. Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).*

This foundational Odoo module implements the platform's strict **Zero-Sudo Architecture** (ADR-0002) and **Service Account Web Isolation** (ADR-0005).

## 🌟 Key Features

* **Centralized Escalation:** Provides the `zero_sudo.security.utils` AbstractModel to safely fetch system parameters and XML IDs without exposing inline `.sudo()` calls.
* **Parameter Whitelisting:** Enforces a strict `frozenset` whitelist against parameter extraction to prevent Server-Side Template Injection (SSTI).
* **Web Isolation:** Extends `res.users` with the `is_service_account` flag and overrides the `web_login` controller to block interactive browser sessions, while preserving JSON/XML-RPC access for headless daemons.
