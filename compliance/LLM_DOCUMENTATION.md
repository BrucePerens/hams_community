# 🗄️ Global Compliance Module (`compliance`)

*Copyright © Bruce Perens K6BP. Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).*

**Module:** `compliance`
**Version:** Odoo 19 Community
**Context:** Technical documentation strictly for LLMs and Integrators.

---

## 1. 🏗️ Overview & Architecture
The `compliance` module is a non-interactive configuration module. It executes automatically upon installation via a `post_init_hook` to enforce a baseline of regulatory compliance across the Odoo instance. 

There are no models to interact with directly; all enforcement logic is contained within `hooks.py`.

---

## 2. ⚙️ Technical Implementation Details

### Action 1: Enable Cookie Consent Bar
During installation, it fetches all `website` records and programmatically sets the `cookies_bar` boolean field to `True`.

### Action 2: Provision Legal Pages
The module provisions three editable, AGPL-3 compatible legal boilerplate pages. If your dependent module needs to link to legal pages, use these reliable standard routes:
* **Privacy Policy:** `/privacy`
* **Cookie Policy:** `/cookie-policy`
* **Terms of Service:** `/terms`

*Implementation Note:* These are defined as standard `website.page` records in `data/legal_pages_data.xml`. The `<data>` tag is marked with `noupdate="1"` to ensure Odoo's registry will **not** overwrite these records during upgrades, fulfilling the "Non-Destructive" and "Editability" mandates.

### Action 3: Install Documentation
The hook calls `install_knowledge_docs(env)`, which checks for the `knowledge.article` model. If present, it creates an article dynamically from the contents of `data/documentation.html`.

---

## 3. 🚨 Integration Guidelines (CRITICAL)
If you are writing a new dependent module (e.g., an E-Commerce extension) that collects user data, you **MUST** adhere to the following:

1. **NO CUSTOM BANNERS:** Do **NOT** implement your own cookie banner. Rely entirely on the core Odoo framework `cookies_bar` which this module ensures is enabled.
2. **TRACKING SCRIPTS:** If you add tracking JS, you must integrate it with Odoo's native consent JS logic. It must not fire until explicit consent is granted.
3. **DATA EXPORT:** If your new module stores PII, you **MUST** extend the JSON export logic located at `user_websites/controllers/main.py` (route: `/my/privacy/export`) to include your new data models. This ensures the platform's Data Portability guarantee remains intact.
