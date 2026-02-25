# User Websites SEO (`user_websites_seo`)

*Copyright © Bruce Perens K6BP. Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).*

This module is a lightweight domain extension for `user_websites`. It bridges the platform's multi-tenant shared blog architecture with Odoo's native frontend SEO engine.

## Technical Implementation
* **Model Injection:** It fuses the `website.seo.metadata` mixin into the `res.users` and `user.websites.group` models.
* **Authorization:** It appends the SEO metadata fields to the `_get_writeable_fields` whitelist, adhering to ADR-0015. This allows standard users to save their customized Meta Title and Description via the frontend widget without requiring backend Administrator rights.
* **Controller Interception:** It overrides the `/<slug>/blog` route. After the base controller prepares the data, this module injects the SEO-aware user or group record as the `main_object`, seamlessly activating the "Optimize SEO" UI menu for the blog owner while hiding it from guests.
