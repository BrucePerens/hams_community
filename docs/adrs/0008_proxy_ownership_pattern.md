# ADR 0008: Proxy Ownership Pattern

*Copyright © Bruce Perens K6BP. Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).*

## Status
Accepted

## Context
The platform requires users to manage their own personal websites, blog posts, and classified listings. However, Odoo's native security model restricts the creation of core UI elements (like `ir.ui.view` and `website.page`) strictly to backend administrators. Granting standard users global CMS designer rights would compromise the entire platform.

## Decision
We implement the "Proxy Ownership Pattern" via a central mixin (`user_websites.owned.mixin`). 
1. Records are assigned an `owner_user_id` or `user_websites_group_id`.
2. Custom Record Rules (`ir.rule`) strictly isolate read/write access to the specific owner.
3. When a user creates or modifies their content, the controller temporarily escalates privileges using `with_user()` to a dedicated Service Account (`user_websites.user_user_websites_service_account`) *strictly* for the database transaction. 
4. The mixin executes `_check_proxy_ownership_write()` prior to the transaction to ensure the originating user mathematically owns the record they are attempting to mutate through the proxy.

## Consequences
* **Positive:** Enables a decentralized, multi-tenant CMS and peer-to-peer marketplace without violating Odoo's strict core permissions.
* **Negative:** Requires careful developer discipline. If a developer forgets to invoke `_check_proxy_ownership_write()` before escalating, it introduces a severe Insecure Direct Object Reference (IDOR) vulnerability.
