# ADR 0015: The "Self-Writeable Fields" Idiom

*Copyright © Bruce Perens K6BP. Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).*

## Status
Accepted

## Context
Users frequently need to update their own preferences (e.g., `privacy_show_in_directory`, `website_page_limit`). These fields exist on the `res.users` model. By default, Odoo restricts write access on `res.users` strictly to system administrators. Historically, developers bypassed this by using `.sudo().write()` inside frontend controllers, which is an anti-pattern that can lead to Mass Assignment vulnerabilities if the controller payload isn't strictly validated.

## Decision
To allow users to modify their preferences securely, we mandate the use of Odoo's native "Self-Writeable Fields" idiom.
1. Modules adding user preferences must inherit `res.users`.
2. The module must override the `@api.model def _get_writeable_fields(self):` method.
3. The override explicitly appends the new preference fields to the allowed list (e.g., `return super()._get_writeable_fields() + ['grid_privacy_level']`).
4. Frontend controllers can then execute `request.env.user.write(vals)` safely without `.sudo()`, as the ORM inherently respects this whitelist for the current user.

## Consequences
* **Positive:** Eliminates controller-level privilege escalation. Protects against RPC and HTTP mass-assignment attacks natively at the ORM layer.
* **Negative:** None. This aligns perfectly with Odoo's intended security design.
