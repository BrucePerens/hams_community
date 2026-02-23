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

### Programmatic Setup & Hooks
* **`res.users._get_user_id_by_slug(slug)`**: A high-performance `@tools.ormcache` method. ALWAYS use this instead of `search()` in frontend controllers.
* **`user_websites.owned.mixin`**: Inherit this in your custom models (e.g., `ham.equipment`) to instantly inherit the Proxy Ownership security rules via `self._check_proxy_ownership_write(vals)`.
* **GDPR Hooks**: The module extends `_get_gdpr_export_data()` and `_execute_gdpr_erasure()` on `res.users`. Dependent modules storing PII MUST override these to append their data to the export payload and hard-delete it during erasure.

---

## 4. 📧 Weekly Digests & Subscriptions
* Features an automated `ir.cron` job (`send_weekly_digest`) that iterates through `blog.post` objects and dispatches emails to followers.
* Utilizes HMAC-SHA256 tokens to generate secure, one-click `List-Unsubscribe` header links for GDPR/CAN-SPAM compliance.
