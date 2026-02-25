# Odoo Core Modules & LLM Development Standards

Here you'll find our foundational Odoo 19 modules. We use these for general-purpose tasks like privacy compliance, managing documentation, and letting users build their own websites. 

This repository is also the source of truth for how we instruct LLMs (like AI coding assistants) to write software for us. It contains our strict operational rules and Odoo technical standards.

## 📦 Included Modules

We've built these modules so you can drop them into any Odoo project without them breaking. They don't rely on our specific ham radio apps.

* **`compliance`**: Automatically handles GDPR and CCPA rules. It sets up the cookie consent banner, gives users a way to download their data, and lets them delete their accounts permanently.
* **`manual_library`**: A free, open-source replacement for Odoo's Enterprise Knowledge app. It lets you write, organize, and publish documentation and guides directly from Odoo.
* **`user_websites`**: Lets your users build their own personal or group websites and blogs right inside your Odoo instance.
* **`zero_sudo`**: Secures the system. It forces background tasks and daemons to use highly restricted service accounts, and actively stops those accounts from logging into the web interface.

## 🤖 LLM-Assisted Development Standards

When we use AI to write code, we force it to follow strict rules. This keeps the code secure, accessible, and up to date with Odoo 19 standards.

* **`docs/LLM_GENERAL_REQUIREMENTS.md`**: Our global rules for the AI. It covers how the AI should talk to us (no fluff, conversational tone), how it should handle security, and the JSON format it must use to send us code.
* **`docs/LLM_ODOO_REQUIREMENTS.md`**: Our strict Odoo coding rules. This includes the "Burn List"—a list of old, bad Odoo habits and legacy syntax the AI is explicitly forbidden from using.

## ⚖️ License & Copyright

Copyright © Bruce Perens K6BP. This software is licensed under the **GNU Affero General Public License, version 3 (AGPL-3.0)**. See the `LICENSE` file for more details.
