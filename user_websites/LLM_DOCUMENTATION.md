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
* **`user_websites.owned.mixin`**: Inherit this in your custom models (e.g., `ham.equipment`) to instantly inherit the Proxy Ownership security rules via `self._check_proxy_ownership_write(vals)`. *(Note: This mixin internally utilizes `zero_sudo.security.utils` for escalation).*
* **GDPR Hooks**: The module extends `_get_gdpr_export_data()` and `_execute_gdpr_erasure()` on `res.users`. Dependent modules storing PII MUST override these to append their data to the export payload and hard-delete it during erasure.

---

## 4. 📧 Weekly Digests & Subscriptions
* Features an automated `ir.cron` job (`send_weekly_digest`) that iterates through `blog.post` objects and dispatches emails to followers.
* Utilizes HMAC-SHA256 tokens to generate secure, one-click `List-Unsubscribe` header links for GDPR/CAN-SPAM compliance.

---

## 5. 🔗 Semantic Anchors
* **Controllers & Routes:** `controller_community_directory`, `controller_submit_violation_report`, `controller_user_websites_home`, `controller_create_site`, `controller_user_blog_index`, `controller_create_blog_post`, `controller_user_websites_documentation`, `controller_submit_appeal`, `controller_subscribe_to_site`, `controller_unsubscribe_digest`, `controller_my_privacy_dashboard`, `controller_export_user_data`, `controller_delete_user_content`.
* **Security & Ownership:** `mixin_proxy_ownership_create`, `mixin_proxy_ownership_write`, `test_mixin_ownership_validation`.
* **Moderation:** `action_take_action_and_strike`, `test_moderation_suspension`.
* **Privacy & GDPR:** `res_users_gdpr_export`, `test_gdpr_export_hook`, `gdpr_sudo_erasure`, `test_gdpr_erasure_pages`, `test_gdpr_erasure_posts`.
* **Cache Invalidation:** `slug_cache_invalidation`, `slug_cache_invalidation_unlink`, `group_slug_cache_invalidation`, `group_slug_cache_invalidation_unlink`.
* **Crons:** `ir_cron_send_weekly_digest`, `test_cron_batching_resumption`, `send_weekly_digest`, `test_weekly_digest_secret`, `test_weekly_digest_mail_template`, `ir_cron_flush_view_counters`, `test_cron_redis_flush`.
* **Views & XPath:** `xpath_rendering_settings`, `xpath_rendering_users`, `xpath_rendering_blog_post`, `xpath_rendering_snippets`, `xpath_rendering_templates`, `xpath_rendering_layout`, `xpath_rendering_navbar` (and corresponding tests).
* **UI Logic:** `violation_report_logic`, `toast_notifications_logic`, `test_tour_violation_report`, `test_tour_toast_notifications`.
* **Other:** `utils_slugify`, `website_page_quota_check`, `simulation_environment`, `test_site_creation_performance_scaling`, `test_acl_overhead_loop_elimination`, `test_tenant_view_isolation`.
