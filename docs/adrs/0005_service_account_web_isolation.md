# ADR 0005: Service Account Web Isolation and Daemon Least Privilege

*Copyright © Bruce Perens K6BP. Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).*

## Status
Accepted

## Context
Daemons and external integration endpoints frequently require escalated database access. Transitioning these daemons to the Zero-Sudo Service Account pattern restricts their database rights. However, if a service account's credentials were leaked, an attacker could theoretically still log into the Odoo web interface to exploit those rights interactively.

## Decision
1. **Daemon Execution:** All background operations MUST execute using dedicated, explicitly defined Service Accounts.
2. **Web Isolation:** The `res.users` model should be extended with an `is_service_account` boolean. The core Odoo `web_login` controller should be intercepted. If a successful login belongs to a user flagged as a service account, the session is instantly destroyed and access is denied. This restricts service accounts strictly to headless XML-RPC/JSON-RPC or internal proxy operations.
3. **Scoped Parameter Access:** The `ir.config_parameter` model should be wrapped to permit service accounts to securely update specific configuration hashes without requiring global admin rights.

## Consequences
* **Positive:** Eliminates the UI attack surface for leaked daemon credentials.
* **Negative:** Developers must remember to set `is_service_account="True"` in the XML data files when provisioning new proxy users.
