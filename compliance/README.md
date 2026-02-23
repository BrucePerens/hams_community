# Global Compliance & Privacy (`compliance`)

*Copyright © Bruce Perens K6BP. Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).*

This Odoo module acts as the central hub for automated regulatory compliance across the Hams Community platform. It ensures that the software meets global privacy standards, such as the GDPR, CCPA, and ePrivacy Directive, without requiring complex manual configuration.

## 🌟 Key Features

* **Automated Cookie Consent Enforcement:** Upon installation, the module scans all active Odoo websites in the database and automatically enables the native "Cookie Consent Bar". This guarantees that optional tracking scripts are legally blocked until explicit user consent is given.
* **Safe Legal Page Provisioning:** The module uses a post-installation hook to dynamically generate standard, AGPL-3 compatible boilerplate legal pages:
    * `/privacy` (Privacy Policy)
    * `/cookie-policy` (Cookie Policy)
    * `/terms` (Terms of Service)
* **Non-Destructive Architecture:** The provisioning system is designed to "do no harm". It strictly checks the routing map by URL before creation. If an administrator has already manually created a page at `/privacy`, the module will skip creation and leave the existing content untouched.

## ⚖️ Included Policy Coverage
The generated boilerplate policies are tailored specifically for the architecture of the `user_websites` and `manual_library` modules. They explicitly disclose:
* The Privacy-Friendly View Counter mechanisms.
* The availability of the automated Data Portability (JSON export) and Right to Erasure tools located at `/my/privacy`.
* The identity shielding features of the content abuse reporting system.
* The Three-Strike moderation and suspension system.

## 🛠️ Installation

1. Copy the `compliance` directory into your active Odoo `addons` path.
2. Restart your Odoo server service.
3. Log in to Odoo as an Administrator with Developer Mode enabled.
4. Navigate to **Apps**, click **Update Apps List**, and remove the default "Apps" filter.
5. Search for `Global Compliance` and click **Activate** / **Install**.

## 📜 License

This project is licensed under the **GNU Affero General Public License v3.0 (AGPL-3.0)**.
