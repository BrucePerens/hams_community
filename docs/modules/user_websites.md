# 🌐 User Websites Module (`user_websites`)

*Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).*

**Context:** Technical documentation strictly for LLMs and Integrators. Use this to build dependent modules without needing the source code.

---

## 1. 🏗️ Overview & Core Patterns
**Open Source Isolation Mandate:** This module is Open Source and available to the Odoo Community. It MUST NEVER be given dependencies on proprietary modules or anything else from the proprietary codebase.

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
* **`content.violation.report`**: Stores abuse reports. Originator is masked from the target owner. The system automatically generates a report and issues a strike if a user attempts to inject malicious SSTI/XSS payloads into their site architecture. Admin spam is prevented via a daily digest cron (`ir_cron_notify_pending_reports`) and a session-guarded UI toast.
* **`content.violation.appeal`**: Used by suspended users to petition for account restoration.

---

## 3. 🐍 Public API & Extensibility Methods

### Frontend Widget Extensibility (The Dropzone)
* **Context Provider:** The module dynamically injects `<meta name="user_websites_slug" content="...">` into the layout `<head>`. Vanilla JS widgets MUST query this meta tag to discover the current page owner's slug statelessly, rather than parsing the URL.
* **Snippet Dropzone:** The module provides a `user_websites_snippet_category` template with an empty `user_websites_snippets_body` div. Dependent modules MUST use `xpath` to inject their custom profile widgets (e.g., stats, recent logs) into this dropzone to maintain strict Open Source Isolation.

### Endpoints & Webhooks
* **`GET /api/v1/user_websites/pending_reports`**: Returns a JSON object `{'count': int}` of unhandled violation reports. Restricted to administrators. Used by the frontend to trigger session-guarded toast notifications upon login.

### 🚨 Privilege Deprecation & Cross-Module Execution (CRITICAL)
In adherence to the Micro-Service Account Pattern (ADR-0062), the `user_websites` internal service account (`user_websites.user_user_websites_service_account`) has been stripped of omnipotent ERP privileges. It **can no longer create or delete** core identity records (`res.users`, `res.partner`). Furthermore, it retains only microscopic read-only access (`1,0,0,0`) to framework tables like `discuss.channel`, `res.company`, and `res.partner.bank` strictly to satisfy Odoo's internal ORM cascade requirements (The Framework ACL Tax - ADR-0064).

If your dependent module (e.g., `cloudflare`, `advanced_routing`) needs to programmatically resolve slugs or provision websites, **you MUST NOT rely on the `user_websites` service account to bypass ACLs for you.** Instead, you must fetch your own domain-specific service account and pass it using the `override_svc_uid` parameter. Your module must explicitly declare the necessary Access Control Lists (`ir.model.access.csv`) for its own service account to perform the required operations.

### Programmatic Setup & Hooks

**Manifest Dependency:** If your custom module inherits `user_websites.owned.mixin` or relies on these resolvers, you MUST explicitly add `"user_websites"` to your `__manifest__.py` `depends` array to prevent fatal load-order crashes.

**The Secure Cached Resolver Pattern (ADR-0066)**: The `user_websites` module offers high-performance `@tools.ormcache` resolvers for cross-module use. ALWAYS use these instead of `.search()` in frontend controllers to prevent database exhaustion. Callers **MUST** pass their own `override_svc_uid` to execute the database search under their own service account's context instead of relying on the default System Provisioner, preventing cross-module access rule failures due to the privilege deprecation mentioned above.
* **`res.users._get_user_id_by_slug(slug, override_svc_uid=None)`**: Resolves a user's slug to their User ID.
* **`user.websites.group._get_group_id_by_slug(slug, override_svc_uid=None)`**: Resolves a group's slug to its Group ID.
* **`website.page._get_page_id_by_url(url, website_id, override_svc_uid=None)`**: Resolves a page URL to its Page ID.
* **`user_websites.owned.mixin`**: Inherit this in your custom models (e.g., `custom.portfolio`) to instantly inherit the Proxy Ownership security rules via `self._check_proxy_ownership_write(vals)`.
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

### Controllers & Routes
* `[%ANCHOR: controller_community_directory]`: Renders the public community directory with pagination.
* `[%ANCHOR: controller_submit_violation_report]`: Handles abuse reporting with honeypot anti-spam protection.
* `[%ANCHOR: controller_user_websites_home]`: Renders a user's or group's personal homepage.
* `[%ANCHOR: controller_create_site]`: Lazy JIT provisioning of a new user website.
* `[%ANCHOR: controller_user_blog_index]`: Renders the shared blog container filtered by user/group.
* `[%ANCHOR: controller_create_blog_post]`: Lazy JIT provisioning of a user's first blog post.
* `[%ANCHOR: controller_user_websites_documentation]`: Renders the module's documentation page.
* `[%ANCHOR: controller_submit_appeal]`: Handles suspension appeals from users.
* `[%ANCHOR: controller_subscribe_to_site]`: Manages email digest subscriptions.
* `[%ANCHOR: controller_unsubscribe_digest]`: Handles secure, tokenized digest unsubscriptions.
* `[%ANCHOR: controller_my_privacy_dashboard]`: Renders the GDPR compliance portal.
* `[%ANCHOR: controller_export_user_data]`: Streams JSON exports of user data.
* `[%ANCHOR: controller_delete_user_content]`: Triggers the background right-to-erasure cascade.
* `[%ANCHOR: api_pending_reports]`: JSON-RPC endpoint returning unhandled violation counts.
* `[%ANCHOR: test_admin_violation_toast_rpc]`: Tests the pending reports API.

### Security & Ownership
* `[%ANCHOR: mixin_proxy_ownership_create]`: Enforces proxy ownership rules on record creation.
* `[%ANCHOR: mixin_proxy_ownership_write]`: Prevents transferring or modifying proxy ownership.
* `[%ANCHOR: test_mixin_ownership_validation]`: Tests proxy ownership rules.

### Moderation
* `[%ANCHOR: action_take_action_and_strike]`: Applies strikes and handles automated suspensions.
* `[%ANCHOR: test_moderation_suspension]`: Tests 3-strike logic.

### Privacy & GDPR
* `[%ANCHOR: res_users_gdpr_export]`: Packages core user data for JSON export.
* `[%ANCHOR: test_gdpr_export_hook]`: Tests GDPR export generation.
* `[%ANCHOR: gdpr_sudo_erasure]`: Executes the hard-delete cascade for GDPR compliance.
* `[%ANCHOR: test_gdpr_erasure_pages]` / `[%ANCHOR: test_gdpr_erasure_posts]`: Tests deletion cascades.

### Cache Invalidation
* `[%ANCHOR: slug_cache_invalidation]`: Purges cached slugs when user profiles change.
* `[%ANCHOR: slug_cache_invalidation_unlink]`: Purges cached slugs when user profiles are deleted.
* `[%ANCHOR: group_slug_cache_invalidation]`: Purges cached slugs for groups.
* `[%ANCHOR: group_slug_cache_invalidation_unlink]`: Purges cached slugs for deleted groups.

### Crons
* `[%ANCHOR: ir_cron_send_weekly_digest]`: XML record for the weekly digest cron.
* `[%ANCHOR: test_cron_batching_resumption]`: Tests digest batch logic.
* `[%ANCHOR: send_weekly_digest]`: Python logic for generating weekly digest emails.
* `[%ANCHOR: test_weekly_digest_secret]` / `[%ANCHOR: test_weekly_digest_mail_template]`: Tests digest emails.
* `[%ANCHOR: ir_cron_flush_view_counters]`: XML record for Redis view counter flush.
* `[%ANCHOR: test_cron_redis_flush]`: Tests Redis view counters.
* `[%ANCHOR: ir_cron_notify_pending_reports]`: XML record for pending reports notification.
* `[%ANCHOR: cron_notify_pending_reports]`: Python logic for pending reports notification.
* `[%ANCHOR: test_cron_pending_reports]`: Tests pending report notifications.

### Views & XPath
* `[%ANCHOR: xpath_rendering_settings]`: Injects User Websites configuration.
* `[%ANCHOR: xpath_rendering_users]`: Injects user profile preferences.
* `[%ANCHOR: xpath_rendering_blog_post]`: Adds proxy owner fields to blog forms.
* `[%ANCHOR: xpath_rendering_snippets]`: Registers custom website builder snippets.
* `[%ANCHOR: xpath_rendering_templates]`: Extends the portal home with appeal options.
* `[%ANCHOR: xpath_rendering_layout]`: Injects violation report modals into the global layout.
* `[%ANCHOR: xpath_rendering_navbar]`: Injects the custom user site navigation bar.

### UI Logic
* `[%ANCHOR: violation_report_logic]`: JS logic for the abuse reporting modal.
* `[%ANCHOR: toast_notifications_logic]`: JS logic for rendering URL-driven success toasts.
* `[%ANCHOR: admin_toast_logic]`: JS logic for fetching and displaying pending report warnings to admins.
* `[%ANCHOR: test_tour_violation_report]` / `[%ANCHOR: test_tour_toast_notifications]` / `[%ANCHOR: test_tour_admin_toast]`: JS UI tours.

### Other
* `[%ANCHOR: utils_slugify]`: URL-safe slug generation.
* `[%ANCHOR: website_page_quota_check]`: Validates page creation against global/user limits.
* `[%ANCHOR: simulation_environment]`: Full platform simulation test.
* `[%ANCHOR: test_site_creation_performance_scaling]`: Performance regression test.
* `[%ANCHOR: test_acl_overhead_loop_elimination]`: Tests ACL performance.
* `[%ANCHOR: test_tenant_view_isolation]`: Tests view isolation across tenants.
