# 🌐 User Websites Module (`user_websites`)

*Copyright © Bruce Perens K6BP. Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).*

**Module:** `user_websites`
**Version:** Odoo 19 Community
**Context:** Technical documentation strictly for LLMs and Integrators. Use this to build dependent modules without needing the source code.

---

## 1. 🏗️ Overview & Core Patterns

**Open Source Isolation Mandate:** This module is Open Source and available to the Odoo Community. It MUST NEVER be given dependencies on `ham_*` modules or anything else from the proprietary codebase.

The `user_websites` module enables decentralized content creation. It serves two distinct entity types via dynamic routing:

1.  **Personal Websites:** Owned by a specific `res.users` record.
* **URL Base:** `/<website_slug>` (e.g., `/john-doe/home`, `/john-doe/blog`)
2.  **Group Websites:** Owned by a `user.websites.group` record.
* **URL Base:** `/<group_slug>` (e.g., `/chess-club/home`, `/chess-club/blog`)

**🚨 KEY DESIGN PATTERN: Proxy Ownership**
Standard Odoo users cannot create `ir.ui.view`, `website.page`, or `blog.post` records due to core security constraints.
This module securely circumvents this by explicitly assigning an `owner_user_id` or `user_websites_group_id` upon creation, evaluating custom Record Rules against these fields, and then escalating privileges via a dedicated Service Account (`.with_user(svc_uid)`) *strictly* for the database write.

---

## 2. 🗄️ Data Model Reference

### Extended `res.users`
The following fields are added to `res.users` and are available for dependent modules:
* **`website_slug`** (`Char`, Computed/Stored): URL-safe identifier. Guaranteed unique.
* **`website_page_limit`** (`Integer`): Max pages allowed (0 = use global default).
* **`privacy_show_in_directory`** (`Boolean`): Opt-in for the public `/community` directory.
* **`violation_strike_count`** (`Integer`): Number of upheld content violations.
* **`is_suspended_from_websites`** (`Boolean`): If True, all personal pages/blogs are forcefully unpublished and locked.
* **`user_websites_page_ids`** (`One2many` to `website.page`): Pages owned by the user.
* **`user_websites_blog_post_ids`** (`One2many` to `blog.post`): Posts owned by the user.

### Extended `website.page` & `blog.post`
These models gain two critical fields to track the "Proxy Owner":
* **`owner_user_id`** (`Many2one` to `res.users`): The business owner of the record.
* **`user_websites_group_id`** (`Many2one` to `user.websites.group`): If set, access is governed by the linked group instead of a single user.
* **`view_count`** (`Integer`): Privacy-friendly, server-side view tracker.

### New Model: `user.websites.group`
Represents a collaborative group.
* **`name`** (`Char`): Display name.
* **`website_slug`** (`Char`): URL identifier.
* **`odoo_group_id`** (`Many2one` to `res.groups`): The auto-generated underlying Odoo security group.
* **`member_ids`** (`Many2many` to `res.users`): Users with write access (synced to `res.groups.users`).

### New Model: `content.violation.report`
Used for abuse reporting.
* **`target_url`** (`Char`): The URL being reported.
* **`state`** (`Selection`): `new`, `under_review`, `action_taken`, `dismissed`.
* **`content_owner_id`** (`Many2one` to `res.users`): The user who owns the flagged content.

---

## 3. 🐍 Public Python API & Methods

Dependent modules should use these methods when interacting with `user_websites` logic.

### On `res.users`:
* **`self.env['res.users']._get_user_id_by_slug(slug)`**: *(Returns: Integer or False)*. A high-performance, `@tools.ormcache` decorated method to resolve a URL slug to a User ID.
**ALWAYS use this instead of `search()`** in frontend controllers to prevent database hits.
* **`user.action_suspend_user_websites()`**: Forcefully unpublishes all user content and sets `is_suspended_from_websites = True`.
* **`user.action_pardon_user_websites()`**: Resets strikes to 0 and lifts suspension.

---

## 4. 🚀 Programmatic User Enrollment

To enroll a user via a dependent module (e.g., automatically upon subscription purchase):

### Step 1: Assign Permissions (CRITICAL)
Users **cannot** manage content without the base module security group.
```python
group_user_websites = self.env.ref('user_websites.group_user_websites_user')
user.write({'group_ids': [(4, group_user_websites.id)]})
```

### Step 2: Programmatic Page Provisioning (Service Account Proxy)
If you must pre-provision a page for a user, use the Service Account combined with the `owner_user_id` field to bypass `ir.ui.view` creation limits while retaining proper ownership.
```python
slug = user.website_slug
home_url = f"/{slug}/home"

page_vals = {
    'url': home_url,
    'name': 'Home',
    'type': 'qweb',
    'key': f'user_websites.home_{slug}', # Must be unique
    'website_published': True,
    'owner_user_id': user.id, # CRITICAL: Sets true business ownership
    'arch': f'''<t name="Home" t-name="user_websites.home_{slug}">...</t>''',
}
svc_uid = self.env.ref('user_websites.user_user_websites_service_account').id
page = self.env['website.page'].with_user(svc_uid).create(page_vals)
```

---

## 5. 🛡️ Security Reference (XML IDs)

If your module creates records that need to be accessible by User Websites roles, use these XML IDs:

* **`user_websites.group_user_websites_user`**: The baseline "Personal Website Owner" group.
Grants access to create/edit pages and posts where `owner_user_id = user.id`.
* **`user_websites.group_user_websites_administrator`**: The "Administrator" group.
Has full global access to all sites, moderation tools, and settings.

---

## 6. 🎨 QWeb Templates & Frontend Integration

If you are building custom frontend views in a dependent module, you may encounter these templates:

* **Report Violation Modal**: Included globally on all website pages via XPath into `website.layout` (before the footer).
To trigger it manually in a custom view, create a button with `data-bs-toggle="modal" data-bs-target="#reportViolationModal" data-url="/your/target/url"`.
* **Standard Routes**: If you need to redirect users to their blog, the standard route is always `/<website_slug>/blog`.
The homepage is `/<website_slug>/home`.

---

## 7. 🔌 Integration & Extension Architecture

To prevent code duplication and ensure strict security, this module exposes several facilities for dependent modules (e.g., `ham_logbook`, `ham_equipment`) to easily plug into the ecosystem.

### A. The Proxy Ownership Mixin (`user_websites.owned.mixin`)
When creating a new model that belongs to a user or group site, **do not** rewrite the complex proxy ownership security logic.
Inherit the mixin:
```python
class HamEquipment(models.Model):
    _name = 'ham.equipment'
    _inherit = ['mail.thread', 'user_websites.owned.mixin']
    
    @api.model_create_multi
    def create(self, vals_list):
        # The mixin provides this validation method for secure service account escalations
        self._check_proxy_ownership_create(vals_list)
        return super().create(vals_list)

    def write(self, vals):
        self.check_access('write')
        self._check_proxy_ownership_write(vals)
        return super().write(vals)
```

### B. Extending the GDPR Export & Erasure (CRITICAL COMPLIANCE)
If your new module collects data, you **MUST** inject it into the GDPR tools by overriding the hooks on `res.users`:
```python
class ResUsers(models.Model):
    _inherit = 'res.users'

    def _get_gdpr_export_data(self):
        data = super()._get_gdpr_export_data()
        svc_uid = self.env.ref('user_websites.user_user_websites_service_account').id
        equipment = self.env['ham.equipment'].with_user(svc_uid).search([('owner_user_id', '=', self.id)])
        data['equipment'] = [{'name': e.name} for e in equipment]
        return data

    def _execute_gdpr_erasure(self):
        super()._execute_gdpr_erasure()
        # ADR-0017: Permanently hard-delete user data on erasure request via sudo
        self.env['ham.equipment'].sudo().search([('owner_user_id', '=', self.id)]).unlink()  # burn-ignore
```

### C. Adding Links to the User Site Navbar
To add a new route (like `/shack`) to the user's specific site navigation menu, simply XPath into `user_navbar_nav_links`.
The `resolved_slug` context variable is guaranteed to be available.
```xml
<template id="user_navbar_inherit_shack" inherit_id="user_websites.user_navbar">
    <xpath expr="//ul[@id='user_navbar_nav_links']" position="inside">
        <li class="nav-item">
            <a class="nav-link" t-attf-href="/#{resolved_slug}/shack">My Shack</a>
        </li>
    </xpath>
</template>
```
