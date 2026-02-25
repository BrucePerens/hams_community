# User Websites (`user_websites`)

*Copyright © Bruce Perens K6BP. Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).*

This Odoo 19 module lets users build their own personal or group websites and blogs right inside your Odoo instance.

**Open Source Rule:** We built this for the open-source community. It runs perfectly on its own and does not rely on any proprietary code.

## 🌟 Key Features

* **Personal Sites & Blogs:** Give every user their own URL (like `/<username>/home`) where they can drag and drop pages or write blog posts.
* **Group Sites:** Let teams or clubs share a website. Anyone in the group can edit pages or post to the group's blog.
* **Community Directory:** A public list where users can show off their sites (if they choose to opt-in).
* **Built-in Moderation:** Every page has a "Report Violation" button. If users post bad content, admins can review it, hand out strikes, and automatically suspend accounts that break the rules.
* **Page Limits:** Stop spam by setting limits on how many pages a single user can create.

## 🛠️ Installation

1. Drop the `user_websites` folder into your Odoo `addons` directory.
2. Restart your Odoo server.
3. Turn on Developer Mode, go to **Apps**, and click **Update Apps List**.
4. Search for `User Websites` and click **Install**.

## ⚙️ Configuration

Go to **Settings > General Settings > User Websites** to configure the app.
* **Global Page Limit:** Set the default maximum number of pages a user is allowed to build.
* **Administrators:** Pick the users who are allowed to review abuse reports and manage group websites.

## 🏗️ How It Works Under the Hood

We used a few neat tricks to make this secure and fast:

* **Just-In-Time Creation:** We don't waste database space creating empty blogs for users who never use them. The system only creates the website records the exact moment the user visits their URL for the first time.
* **One Big Blog:** Instead of creating a thousand separate blog containers, everyone shares a single Odoo `blog.blog` record named "Community Blog". We just filter the posts so users only see their own stuff. 
* **Proxy Ownership:** Odoo normally only lets admins build web pages. We get around this securely. When a user creates a page, the system briefly logs in as a background Service Account to save the HTML to the database, but tags the user as the real "owner" so only they can edit it later.
