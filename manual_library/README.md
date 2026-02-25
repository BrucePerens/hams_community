# Manual Library (`manual_library`)

*Copyright © Bruce Perens K6BP. Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).*

This is a free, open-source replacement for Odoo's Enterprise Knowledge app. It lets you write, organize, and publish documentation and user manuals directly inside Odoo Community.

Because it uses the exact same database structure (`knowledge.article`) as the Enterprise version, other modules can easily install their own instruction manuals here without breaking.

**Open Source Rule:** We built this for the open-source community. It runs perfectly on its own and does not rely on any proprietary code.

## 🌟 Key Features

* **Nested Folders:** Organize your articles in a tree (parent/child) so they are easy to navigate.
* **Enterprise Compatible:** You can load XML data files meant for the Enterprise Knowledge app, and they will work perfectly here.
* **Rich Text Editor:** Use Odoo's standard editor to write guides, insert images, and format text.
* **Public Web Portal:** Click "Publish" to instantly push your manuals to the public website (`/manual`). The system automatically builds a handy sidebar menu for visitors.
* **Access Control:** Keep private admin notes hidden, share drafts with logged-in coworkers, or publish finalized guides to the public.

## 🛠️ Installation

1. Drop the `manual_library` folder into your Odoo `addons` directory.
2. Restart your Odoo server.
3. Turn on Developer Mode, go to **Apps**, and click **Update Apps List**.
4. Search for `Manual Library` and click **Install**.

## 📖 How to Use It

### Writing Articles
1. Click the **Manuals** app in the main Odoo menu.
2. Click **New**.
3. If you want this article to sit inside a folder, pick a **Parent Article**.
4. When you're ready to share it with the world, hit the **Is Published** button at the top.

### Reading Articles on the Web
* Go to `/manual` on your website to see the public knowledge base.
* We included a search bar and an automatically generated Table of Contents that reads your headers so users can jump around long documents easily.

## ⚖️ Legal Note

We built this from scratch. We did not copy any code, logic, or proprietary designs from Odoo Enterprise. We just matched the database field names so the two systems are perfectly compatible (known legally as API Interoperability).
