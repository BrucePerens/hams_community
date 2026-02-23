### Explanation of `ir.model.access.csv`

This CSV file is a critical part of Odoo's security system. It defines the base access control rights for various user groups on different data models. Each row in this file grants or denies permissions (Read, Write, Create, Delete) to a specific security group for a specific model.

Here's a breakdown of the rules in this file:

- **`access_content_violation_report_admin`**
  - **Group:** User Websites Administrator
  - **Model:** `content.violation.report`
  - **Permissions:** Full access (Read, Write, Create, Delete).
  - **Purpose:** Allows administrators to manage all aspects of content violation reports.

- **`access_content_violation_report_user`**
  - **Group:** Internal User (logged-in users)
  - **Model:** `content.violation.report`
  - **Permissions:** Read, Write, Create (but not Delete).
  - **Purpose:** Allows any logged-in user to submit a new report and view existing ones, but they cannot delete them.

- **`access_content_violation_report_public`**
  - **Group:** Public User (not logged in)
  - **Model:** `content.violation.report`
  - **Permissions:** Read, Write, Create (but not Delete).
  - **Purpose:** Allows non-logged-in users (guests) to submit new reports.

- **`access_res_users_admin`**
  - **Group:** User Websites Administrator
  - **Model:** `res.users` (Users)
  - **Permissions:** Read, Write (but not Create or Delete).
  - **Purpose:** Allows administrators to modify user settings related to user websites (like page limits), but not to create or delete system users through this module's access rights.

- **`access_res_config_settings_admin`**
  - **Group:** User Websites Administrator
  - **Model:** `res.config.settings` (Settings)
  - **Permissions:** Full access.
  - **Purpose:** Allows administrators to access and modify the settings for the User Websites module in the general settings area.

- **`access_website_page_user`**
  - **Group:** User Website Owner
  - **Model:** `website.page`
  - **Permissions:** Full access.
  - **Purpose:** This is the baseline permission that allows a user in the "User Website Owner" group to create, view, edit, and delete their own website pages. Record rules will further restrict this to only their *own* pages.

- **`access_blog_post_user`**
  - **Group:** User Website Owner
  - **Model:** `blog.post`
  - **Permissions:** Full access.
  - **Purpose:** Allows users in the group to manage their own blog posts.

- **`access_blog_blog_user`**
  - **Group:** User Website Owner
  - **Model:** `blog.blog`
  - **Permissions:** Full access.
  - **Purpose:** Allows users to manage their own blogs.

- **`access_user_websites_group_admin`**
  - **Group:** User Websites Administrator
  - **Model:** `user.websites.group`
  - **Permissions:** Full access.
  - **Purpose:** Allows administrators to create, edit, and delete any group website configuration.

- **`access_user_websites_group_user`**
  - **Group:** Internal User
  - **Model:** `user.websites.group`
  - **Permissions:** Read-only.
  - **Purpose:** Allows any logged-in user to see the list of available group websites, but they cannot modify them.

- **`access_user_websites_group_public`**
  - **Group:** Public User
  - **Model:** `user.websites.group`
  - **Permissions:** Read-only.
  - **Purpose:** Allows non-logged-in users to see the list of public group websites.
