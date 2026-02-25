# Global Compliance & Privacy (`compliance`)

*Copyright © Bruce Perens K6BP. Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).*

This module automatically handles the annoying parts of running a legal website. It makes sure your Odoo instance complies with GDPR, CCPA, and ePrivacy rules without you having to configure anything manually.

## 🌟 What It Does

* **Turns on the Cookie Banner:** As soon as you install this, it flips the switch to turn on Odoo's native Cookie Consent Bar across all your websites. This stops optional tracking scripts until the user clicks "Accept."
* **Writes Your Legal Pages:** It automatically creates standard, editable pages for your Privacy Policy (`/privacy`), Cookie Policy (`/cookie-policy`), and Terms of Service (`/terms`).
* **Doesn't Break Your Edits:** If you've already written a privacy policy at `/privacy`, the module detects it and leaves yours alone. If you edit the pages it creates, it won't overwrite your work when you update the module.

## ⚖️ Included Policy Coverage
The boilerplate policies we generate are written specifically to cover the features in our other open-source modules. They explain:
* How our privacy-friendly view counters work.
* How users can download or permanently delete their data at the `/my/privacy` dashboard.
* How our abuse reporting system hides the reporter's email to protect them.
* How our 3-strike moderation and suspension system works.

## 🛠️ Installation

1. Drop the `compliance` folder into your Odoo `addons` directory.
2. Restart your Odoo server.
3. Turn on Developer Mode, go to **Apps**, and click **Update Apps List**.
4. Search for `Global Compliance` and click **Install**.
