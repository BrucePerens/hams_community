# ADR 0064: Micro-Service Account Strict ACL Isolation

## Status
Accepted

## Context
Our Zero-Sudo architecture relies on Micro-Service Accounts (ADR 0062) to perform highly restricted actions without using `.sudo()`.

During test deployment, an architectural trap was discovered: when a domain-specific Service Account (like `external_sync_internal`) attempts to write to `res.users`, Odoo natively cascades that write to the underlying `res.partner` record. During that cascade, the core Odoo framework iterates over related fields such as `res.partner.bank_ids`. Because our Service Accounts did not have explicit read access to `res.partner.bank`, the ORM threw a hard `AccessError`, crashing the transaction.

The initial reaction is often to assign `base.group_user` (Internal User) or `base.group_system` (Admin) to the Service Account to seamlessly satisfy these core framework relation checks. However, granting `base.group_user` gives the Service Account widespread access to internal ERP menus, chatter history, and HR profiles, violating the principle of least privilege and creating a massive blast radius if the daemon's credentials are compromised.

## Decision
We explicitly forbid assigning `base.group_user` or `base.group_system` to domain-specific Service Accounts simply to bypass ORM cascade traps.

Instead, Service Accounts MUST be granted explicit, microscopic Access Control Lists (`ir.model.access.csv`) for the exact relational tables they trigger.

For example, to solve the `res.users` mutation trap, we created a dedicated `account_service_internal` and explicitly granted it `read` access to `res.partner.bank`, allowing the ORM cascade to succeed without exposing the entire ERP to the daemon.

**Exception:* If native ERP facility interaction is strictly required (like writing to `mail.thread` chatter), the system must temporarily assume the specialized `odoo_facility_service_internal` account, which is the *only* account permitted to hold `base.group_user`.

*## Consequences
Daemons and Service Accounts remain absolutely isolated to their designated tables. A compromised sync daemon cannot read internal financial accounts, messages, or HR data.
