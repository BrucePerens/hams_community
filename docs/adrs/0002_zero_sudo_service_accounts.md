# ADR 0002: Zero-Sudo and Service Account Pattern

## Status
Accepted

## Context
In standard Odoo development, it is common to use the `.sudo()` method to bypass Access Control Lists (ACLs) and Record Rules when an unauthenticated or low-privilege user needs to trigger a system-level action. This is a dangerous anti-pattern that frequently leads to privilege escalation vulnerabilities, as it grants absolute database rights to the execution context.

## Decision
The use of the raw `.sudo()` method is strictly forbidden across the codebase.
We will implement a "Zero-Sudo" Service Account Pattern. When elevated privileges are required, the system MUST:
1. Identify a specifically crafted Service Account (e.g., `user_dns_api_service`).
2. Retrieve its UID securely using a centralized security utility module.
3. Execute the operation using the `with_user(svc_uid)` idiom.

## Consequences
* **Positive:** Security by default. If a method is exploited, the attacker is strictly confined to the explicit, surgical ACLs granted to that specific Service Account.
* **Negative:** Slightly increased developer friction. Developers must explicitly define Service Accounts and their associated groups in XML data files for every new system-level integration.
