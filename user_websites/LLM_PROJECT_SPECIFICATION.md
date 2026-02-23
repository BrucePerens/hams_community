# LLM PROJECT SPECIFICATION: USER WEBSITES

*Copyright © Bruce Perens K6BP. Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).*

This document defines the functional specifications and business logic for the `user_websites` Odoo module.

---

## 1. PROJECT OVERVIEW

**Module Name:** `user_websites`
**Summary:** Allows users to create personal or group websites and blogs within an Odoo instance.
**Core Philosophy:** Privacy, Ownership, and Community.
**Open Source Isolation Mandate:** This module is Open Source and available to the Odoo Community. It MUST NEVER depend on `ham_*` modules or anything else from the proprietary codebase.

---

## 2. ARCHITECTURE & DATA MODEL

### A. Blog Architecture: Shared Container
* **Strategy:** Use a single `blog.blog` record (named "Community Blog") to house all user posts to avoid container proliferation.
* **Logic:** Posts are filtered dynamically by `owner_user_id` (the author) in the Controller.
* **Result:** Users perceive they have a personal blog (`/user/blog`), but technically share a backend container.

### B. Group Websites
* **Model:** `user.websites.group`
* **Security:** A custom Odoo Security Group is auto-created for every Website Group.
* **Content:** Groups can own `website.page` and `blog.post` records via the `user_websites_group_id` field.

---

## 3. FEATURE SPECIFICATIONS

### A. Personal Websites
* **Route:** `/<username>/home`
* **Functionality:** Users can create/edit a homepage. Access is controlled by `res.users` privacy settings.

### B. Group Websites
* **Route:** `/<group-slug>/home`
* **Functionality:** Collaborative site editing for members. Admins manage membership via the standard Odoo Groups interface.

### C. Community Directory
* **Route:** `/community`
* **Logic:** Displays a list of users who have opted-in via `res.users.privacy_show_in_directory`.

### D. Abuse Reporting & Moderation
* **Mechanism:** A modal available on all user pages/blogs.
* **Model:** `content.violation.report` and `content.violation.appeal`.
* **Logic:** Public users can submit reports. Content Owners have NO visibility into who reported them. Admins manage strikes. 3 strikes result in automatic suspension. Suspended users can file an appeal.

### E. Regulatory Compliance (GDPR/CCPA)
* **View Counters:** `view_count` on content is updated server-side without reliance on cookies or PII logging.
* **Data Portability:** Users can export all owned website pages and blog posts via JSON format in the `/my/privacy` portal dashboard.
* **Right to Erasure:** Users can permanently hard-delete (`unlink`) all owned content and remove themselves from the community directory instantly from the `/my/privacy` dashboard.

---

## 4. PERMISSIONS & ACLs

* **User (Base):** Can create/edit their own Pages and Posts. Read-only on the "Community Blog" container. Can download and delete their own content.
* **Group Member:** Can create/edit Pages/Posts assigned to their Group.
* **Guest:** Can view public pages and submit Abuse Reports. Cannot create content.
* **Administrator:** Full access to all user sites, reports, and appeals.
