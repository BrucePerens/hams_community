# Zero-Sudo Security Core (`zero_sudo`)

*Copyright © Bruce Perens K6BP. Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).*

This is the core security cop for our Odoo ecosystem. It enforces our strict **Zero-Sudo Architecture** (ADR-0002) to stop privilege escalation hacks, and it physically locks down background service accounts so they can't be used to log into the website (ADR-0005).

## 🌟 What It Does

* **Safe Privilege Escalation:** Instead of letting developers use Odoo's dangerous `.sudo()` command, this module provides safe, cached functions (like `_get_service_uid`) to run background tasks securely.
* **Blocks System Hacks:** It forces developers to hardcode a "whitelist" of safe configuration settings. If an attacker tries to trick the system into handing over a cryptographic secret (like a database password), this module blocks it.
* **Locks Out Daemons:** It adds an `is_service_account` checkbox to users. If an account is running a background daemon and someone tries to log into the web browser with that account, this module instantly destroys the session and kicks them out.
