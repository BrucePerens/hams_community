# Jules Issues - user_websites

## Environment & Infrastructure
* **PostgreSQL Socket Permissions:** The `/opt/hams/pgsock` directory required a manual `chmod 755` to allow the Odoo process to connect to the database via unix domain sockets.
* **Post-Init Hook Access Errors:** The service account used in `post_init_hook` failed to read the `is_service_account` field on `res.users` due to base Odoo security restrictions on that field. **Resolution:** Implemented direct SQL updates in the hook to populate group memberships and flags, bypassing the ORM for initial setup.

## SQL View Architectural Decisions
* **Total Views Aggregation:** Implemented `user_websites.public_directory_view` which aggregates `website_page` and `blog_post` view counts.
* **Routing Reliability:** Discovered that joining `res_users` directly for names in SQL views can cause performance bottlenecks; used `res_partner` joins instead for Odoo 19 compatibility.
* **Slug Integrity:** Enforced a `website_slug IS NOT NULL` filter at the view level to prevent broken "Home" links in the Community Directory for system/internal users who haven't provisioned a site.

## Testing Hurdles
* **Transaction Isolation:** Standard `mail.mail` assertions failed in `RealTransactionCase` because the mail dispatcher operates in a separate transaction. **Resolution:** Updated tests to search for mail records using the dedicated mail service account.
* **Exclusive Group Validation:** Odoo 19 enforces that a user cannot be both in `base.group_portal` and `base.group_user`. Test `setUp` methods were refactored to clear `group_ids` before assigning the correct single role.
* **Tour Race Conditions:** `test_02b_violation_report_tour` occasionally reports a falsy "ready" state in constrained VM environments. Added `step_delay` and optimized selector wait times to mitigate.
