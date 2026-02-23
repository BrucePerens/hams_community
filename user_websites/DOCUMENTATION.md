# User Websites Module Documentation

*Copyright © Bruce Perens K6BP. Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).*

**Module Name:** `user_websites`
**Version:** Odoo 19 Community
**Summary:** Enables decentralized, multi-tenant content creation within a single Odoo instance, allowing users to build personal or group-managed websites and blogs.

**Open Source Isolation Mandate:** This module is Open Source and available to the Odoo Community. It MUST NEVER be given dependencies on `ham_*` modules or anything else from the proprietary codebase.

---

## 1. System Configuration

Administrators can configure global module behaviors by navigating to **Settings > General Settings > User Websites**.
* **Global Page Limit:** Define the default maximum number of web pages a standard user can create. (Note: A user-specific limit defined on their profile will override this global setting).
* **User Websites Administrators:** Assign specific users to the administrative group. These users receive full access to manage all group sites, personal sites, and content violation reports.

---

## 2. End-User Guide

The User Websites module allows you to host your own personal corner of the community or collaborate with others on a group page.

### 2.1. Managing Your Personal Website & Blog
* **Your URL:** Your personal website is located at `/<your-username>/home` (e.g., `/john-doe/home`). Your blog is located at `/<your-username>/blog`.
* **Getting Started:** Your site is not created automatically. To build it, simply navigate to your personal URL while logged in. The system will prompt you to create your homepage.
* **Editing:** Once created, you can use the standard Odoo website builder to drag and drop blocks, write text, and publish your pages.

### 2.2. Joining the Community Directory
By default, your website is hidden from the public community list to protect your privacy. To make your site discoverable:
1. Click on your profile picture in the top right corner and go to **My Profile** (or Preferences).
2. Navigate to the **User Websites** tab.
3. Check the box labeled **"Show in Public Directory"**. 
4. Your name and a link to your site will now appear at the `/community` route.

### 2.3. Group Websites
If you are part of a User Website Group (like a club, committee, or project team), you share ownership of a group website.
* Group sites function exactly like personal sites but are located at the group's specific URL.
* Any member of the group can edit pages and publish blog posts on behalf of the group.

### 2.4. Reporting Content Violations
Our community relies on safe, respectful content. If you see a page or blog post that violates community guidelines:
1. Click the **Report Violation** button (marked with a flag icon) located at the bottom of the content.
2. Provide your email (if you are a guest) and a description of the issue.
3. Submit the report. 
*Note: To protect you against retaliation, the owner of the content cannot see who reported them, nor can they view the report itself. It goes directly to the site administrators.*

---

## 3. Integrator & Developer Guide

### 3.1. Core Architecture & Design Patterns
* **Lazy JIT Provisioning:** Websites and Blogs do not exist upon user creation. They are provisioned Just-In-Time when the owner visits their slug root and triggers a POST request to `create_site`. This ensures explicit user consent to publish.
* **Shared Blog Container:** To prevent database bloat, all user blog posts are housed in a single standard `blog.blog` record named exactly `"Community Blog"`. The controller dynamically filters standard Odoo views by the `owner_user_id` so users perceive they have isolated blogs.
* **Proxy Ownership Pattern:** Standard users cannot create `ir.ui.view` or `website.page` records due to Odoo core security. The module circumvents this securely by explicitly assigning the `owner_user_id` or `user_websites_group_id` upon creation, evaluating custom Record Rules against these fields, and then escalating privileges via `.sudo()` exclusively for the database write. **Never use raw SQL to alter `create_uid`.**

### 3.2. Programmatic User Enrollment
To enroll a user via API, XML-RPC, or external module, follow these steps strictly:

**1. Create the User:**

    user = self.env['res.users'].create({
        'name': 'New User',
        'login': 'newuser',
        'email': 'user@example.com',
    })

**2. Assign Permissions (CRITICAL):**
Users cannot manage content without the base module security group.

    group_user_websites = self.env.ref('user_websites.group_user_websites_user')
    user.write({
        'group_ids': [(4, group_user_websites.id)]
    })

**3. Programmatic Page Provisioning (Optional):**
If you must pre-provision a page, you must use `.sudo()` combined with the Proxy Ownership field.

    slug = user.website_slug
    home_url = f"/{slug}/home"

    page_vals = {
        'url': home_url,
        'name': 'Home',
        'type': 'qweb',
        'key': f'user_websites.home_{slug}',
        'website_published': True,
        'owner_user_id': user.id,
        'arch': f'''<t name="Home" t-name="user_websites.home_{slug}">...</t>''',
    }
    page = self.env['website.page'].sudo().create(page_vals)

### 3.3. Development Constraints (Odoo 19)
If extending this module, adhere to the following Odoo 19 strict requirements:
1.  **Routing Safety:** Always use `werkzeug.exceptions.NotFound()` for 404s in controllers.
2.  **QWeb Context:** When rendering upstream templates (e.g., `website_blog.blog_post_short`), you must manually construct and inject the `pager` object to prevent template KeyErrors.
3.  **Slug Collision:** The utility function automatically checks against `RESERVED_SLUGS` and increments the user's slug to prevent hijacking system routes. Update this constant if new base routes are added.

---

## 4. Running Tests

The module includes **58 exhaustive unit and integration tests** covering security edge cases, routing constraints, slug generation utility functions, and the proxy ownership patterns.

To execute the test suite locally:

    odoo-bin -c /etc/odoo/odoo.conf -d your_db_name -i user_websites --test-enable --stop-after-init

Expected output should return 0 failures and 0 errors, validating the complete isolation of user data and the integrity of the routing constraints.
