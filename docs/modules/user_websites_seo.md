# 🔍 User Websites SEO Module (`user_websites_seo`)

*Copyright © Bruce Perens K6BP. Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).*

**Context:** Technical documentation strictly for LLMs and Integrators.

## 1. 🏗️ Overview & Architecture
This module is a lightweight domain extension for `user_websites`. It connects our shared blog architecture with Odoo's native frontend SEO engine.

## 2. ⚙️ Technical Implementation Details
* **Model Injection:** It fuses the `website.seo.metadata` mixin into the `res.users` and `user.websites.group` models.
* **Authorization:** It appends the SEO metadata fields to the `SELF_WRITEABLE_FIELDS` property.
* **Controller Interception:** Overrides the `/blog` route to inject the SEO-aware profile object into the QWeb context. Verified by `[@ANCHOR: controller_user_blog_index_seo_override]`.
* **Soft Dependency Documentation:** The module uses a `post_init_hook` and `_register_hook` to dynamically install documentation if `knowledge.article` is present in the environment, without requiring a hard dependency on `manual_library` or `knowledge`.
