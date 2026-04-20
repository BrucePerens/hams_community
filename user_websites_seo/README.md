# User Websites SEO (`user_websites_seo`)

*Copyright © Bruce Perens K6BP. Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).*

This module is a lightweight domain extension for `user_websites`. It connects our shared blog architecture with Odoo's native frontend SEO engine.

## Technical Implementation
* **Model Injection:** It fuses the `website.seo.metadata` mixin into the `res.users` and `user.websites.group` models.
* **Authorization:** It appends the SEO metadata fields to the `SELF_WRITEABLE_FIELDS` property. This allows standard users to save their customized Meta Title and Description via the frontend widget.
* **Controller Interception:** It overrides the `/<slug>/blog` route. After the base controller prepares the data, this module injects the SEO-aware user or group record as the `main_object`, seamlessly activating the "Optimize SEO" UI menu for the blog owner while hiding it from guests.
* **Documentation:** Automatically installs its guide into the Knowledge/Manual Library if either module is present. It uses a soft dependency approach, ensuring it works in environments with or without a documentation module.
