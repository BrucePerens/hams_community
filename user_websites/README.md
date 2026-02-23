# User Websites (`user_websites`)

*Copyright © Bruce Perens K6BP. Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).*

This Odoo module is designed for **Odoo Community / Enterprise 19**. It enables decentralized, multi-tenant content creation within a single Odoo instance, allowing users to build personal or group-managed websites and blogs.

**Open Source Isolation Mandate:** This module is Open Source and available to the Odoo Community. It MUST NEVER be given dependencies on `ham_*` modules or anything else from the proprietary codebase.

## 🌟 Key Features

* **Personal Websites & Blogs:** Each user can dynamically generate their own personal website (e.g., `/<username>/home`) and blog (`/<username>/blog`).
* **Group Websites:** Users can collaborate via "User Websites Groups". These auto-generate dedicated Odoo security groups to safely manage shared sites (e.g., `/<group-slug>/home`).
* **Community Directory:** An opt-in public directory (`/community`) that showcases participating users and their websites.
* **Integrated Abuse Reporting:** A built-in "Report Violation" modal available to both guests and users, funneling moderation requests directly to site administrators while strictly protecting the complainant's identity.
* **Page Limits:** Global and user-specific quotas to control the maximum number of pages a user can create.

## 🛠️ Installation

1. Copy the `user_websites` directory into your active Odoo `addons` path.
2. Restart your Odoo server service.
3. Log in to Odoo as an Administrator with Developer Mode enabled.
4. Navigate to **Apps**, click **Update Apps List**, and remove the default "Apps" filter.
5. Search for `User Websites` and click **Activate** / **Install**.
*(Note: Installing this module automatically provisions a comprehensive User Manual inside the Odoo Knowledge app).*

## ⚙️ Configuration

Administrators can configure global settings by navigating to **Settings > General Settings > User Websites**.
* **Global Page Limit:** Define the default maximum number of web pages a standard user can create. (Can be overridden per user on their profile).
* **User Websites Administrators:** Assign users to the administrative group. These users receive full access to manage all group sites, personal sites, and review content violation reports.

## 🏗️ Technical Architecture Highlights

This module employs several advanced design patterns to ensure scalability and strict security within Odoo:

* **Lazy JIT Provisioning:** Websites and Blogs do not exist upon user creation. They are provisioned "Just-In-Time" when the owner visits their slug root and triggers the creation process, ensuring explicit user consent.
* **Shared Blog Container:** To prevent database bloat, all user blog posts are housed in a single standard `blog.blog` record named "Community Blog". The controller dynamically filters standard Odoo views by the `owner_user_id`.
* **Proxy Ownership Pattern:** Standard Odoo users cannot create `ir.ui.view` or `website.page` records due to core security. The module securely circumvents this by explicitly assigning an `owner_user_id` or `user_websites_group_id` upon creation, evaluating custom Record Rules against these fields, and then escalating privileges via `.sudo()` *strictly* for the database write.

## 🧪 Testing

This module includes 60 exhaustive unit and integration tests covering security edge cases, routing constraints, slug generation, and proxy ownership patterns. 

To execute the test suite locally:
```bash
odoo-bin -c /etc/odoo/odoo.conf -d your_db_name -i user_websites --test-enable --stop-after-init
```
