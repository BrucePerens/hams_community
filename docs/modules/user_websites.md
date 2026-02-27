# 🌐 User Websites Module (`user_websites`)

*Copyright © Bruce Perens K6BP. Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).*

**Context:** Technical documentation strictly for LLMs and Integrators. Use this to build dependent modules without needing the source code.

---

## 1. 🏗️ Overview & Core Patterns
**Open Source Isolation Mandate:** This module is Open Source and available to the Odoo Community. It MUST NEVER be given dependencies on `ham_*` modules or anything else from the proprietary codebase.

The `user_websites` module enables decentralized content creation. It employs the **Proxy Ownership Pattern**: standard Odoo users cannot create `ir.ui.view` or `website.page` records due to core security. The module securely circumvents this by assigning an `owner_user_id`, evaluating custom Record Rules against it, and escalating privileges via a dedicated Service Account (`.with_user(svc_uid)`) strictly for the database write.

---

## 2. 🗄️ Data Model Reference

### Extended `res.users`
* **`website_slug`**: URL-safe identifier.
* **`privacy_show_in_directory`**: Opt-in for the public `/community` directory.
* **`violation_strike_count`**: Number of upheld content violations.
* **`is_suspended_from_websites`**: If True, all personal content is forcefully unpublished.
* **`appeal_ids`** (`One2many`): Links to Moderation Appeals.

### Content Models (`website.page`, `blog.post`)
* **`owner_user_id`**: The proxy owner.
* **`user_websites_group_id`**: For shared group websites.
* **`view_count`**: Privacy-friendly server-side view tracker.

### Moderation Models
* **`content.violation.report`**: Stores abuse reports. Originator is masked from the target owner.
* **`content.violation.appeal`**: Used by suspended users to petition for account restoration.

---

## 3. 🐍 Public API & Extensibility Methods

### Frontend Widget Extensibility (The Dropzone)
* **Context Provider:** The module dynamically injects `<meta name="user_websites_slug" content="...">` into the layout `<head>`. Vanilla JS widgets MUST query this meta tag to discover the current page owner's slug statelessly, rather than parsing the URL.
* **Snippet Dropzone:** The module provides a `user_websites_snippet_category` template with an empty `user_websites_snippets_body` div. Dependent modules MUST use `xpath` to inject their custom profile widgets (e.g., stats, recent logs) into this dropzone to maintain strict Open Source Isolation.

### Programmatic Setup & Hooks
* **`res.users._get_user_id_by_slug(slug)`**: A high-performance `@tools.ormcache` method. ALWAYS use this instead of `search()` in frontend controllers.
* **`user_websites.owned.mixin`**: Inherit this in your custom models (e.g., `ham.equipment`) to instantly inherit the Proxy Ownership security rules via `self._check_proxy_ownership_write(vals)`.
  * **Mandatory Assignment:** Standard users MUST supply either `owner_user_id` OR `user_websites_group_id` upon record creation.
  * **Mutual Exclusivity:** A record CANNOT be owned by both a user and a group simultaneously. Attempting to assign both will raise a strict `ValidationError`.
  * *(Note: This mixin internally utilizes `zero_sudo.security.utils` for escalation).*
* **GDPR Hooks**: The module extends `_get_gdpr_export_data()` and `_execute_gdpr_erasure()` on `res.users`. Dependent modules storing PII MUST override these to append their data to the export payload and hard-delete it during erasure.

---

## 4. 📧 Weekly Digests & Subscriptions
* Features an automated `ir.cron` job (`send_weekly_digest`) that iterates through `blog.post` objects and dispatches emails to followers.
* Utilizes HMAC-SHA256 tokens to generate secure, one-click `List-Unsubscribe` header links for GDPR/CAN-SPAM compliance.

---

## 5. 🔗 Semantic Anchors
* **Controllers & Routes:** `[%ANCHOR: controller_community_directory]`, `[%ANCHOR: controller_submit_violation_report]`, `[%ANCHOR: controller_user_websites_home]`, `[%ANCHOR: controller_create_site]`, `[%ANCHOR: controller_user_blog_index]`, `[%ANCHOR: controller_create_blog_post]`, `[%ANCHOR: controller_user_websites_documentation]`, `[%ANCHOR: controller_submit_appeal]`, `[%ANCHOR: controller_subscribe_to_site]`, `[%ANCHOR: controller_unsubscribe_digest]`, `[%ANCHOR: controller_my_privacy_dashboard]`, `[%ANCHOR: controller_export_user_data]`, `[%ANCHOR: controller_delete_user_content]`.
* **Security & Ownership:** `[%ANCHOR: mixin_proxy_ownership_create]`, `[%ANCHOR: mixin_proxy_ownership_write]`, `[%ANCHOR: test_mixin_ownership_validation]`.
* **Moderation:** `[%ANCHOR: action_take_action_and_strike]`, `[%ANCHOR: test_moderation_suspension]`.
* **Privacy & GDPR:** `[%ANCHOR: res_users_gdpr_export]`, `[%ANCHOR: test_gdpr_export_hook]`, `[%ANCHOR: gdpr_sudo_erasure]`, `[%ANCHOR: test_gdpr_erasure_pages]`, `[%ANCHOR: test_gdpr_erasure_posts]`.
* **Cache Invalidation:** `[%ANCHOR: slug_cache_invalidation]`, `[%ANCHOR: slug_cache_invalidation_unlink]`, `[%ANCHOR: group_slug_cache_invalidation]`, `[%ANCHOR: group_slug_cache_invalidation_unlink]`.
* **Crons:** `[%ANCHOR: ir_cron_send_weekly_digest]`, `[%ANCHOR: test_cron_batching_resumption]`, `[%ANCHOR: send_weekly_digest]`, `[%ANCHOR: test_weekly_digest_secret]`, `[%ANCHOR: test_weekly_digest_mail_template]`, `[%ANCHOR: ir_cron_flush_view_counters]`, `[%ANCHOR: test_cron_redis_flush]`.
* **Views & XPath:** `[%ANCHOR: xpath_rendering_settings]`, `[%ANCHOR: xpath_rendering_users]`, `[%ANCHOR: xpath_rendering_blog_post]`, `[%ANCHOR: xpath_rendering_snippets]`, `[%ANCHOR: xpath_rendering_templates]`, `[%ANCHOR: xpath_rendering_layout]`, `[%ANCHOR: xpath_rendering_navbar]` (and corresponding tests).
* **UI Logic:** `[%ANCHOR: violation_report_logic]`, `[%ANCHOR: toast_notifications_logic]`, `[%ANCHOR: test_tour_violation_report]`, `[%ANCHOR: test_tour_toast_notifications]`.
* **Other:** `[%ANCHOR: utils_slugify]`, `[%ANCHOR: website_page_quota_check]`, `[%ANCHOR: simulation_environment]`, `[%ANCHOR: test_site_creation_performance_scaling]`, `[%ANCHOR: test_acl_overhead_loop_elimination]`, `[%ANCHOR: test_tenant_view_isolation]`.
