# Odoo Core Modules & LLM Development Standards

Here you'll find our foundational Odoo 19 modules. We use these for general-purpose tasks like privacy compliance, managing documentation, and letting users build their own websites. 

This repository is also the source of truth for how we instruct LLMs (like AI coding assistants) to write software for us. It contains our strict operational rules and Odoo technical standards.

## 📦 Included Modules

We've built these modules so you can drop them into any Odoo project without them breaking. They don't rely on our specific ham radio apps.

* **`cloudflare`**: The control plane for your Cloudflare edge. It manages
Web Application Firewall (WAF) rules directly from the Odoo backend,
automatically purges the CDN cache globally when local static files change
or web pages are edited, bans malicious IPs caught by silent honeypots,
and handles Turnstile CAPTCHAs. It will set up your Cloudflare tunnel
for *cloudflared*.

* **`caching`**: A global Service Worker module that acts as a client-side
CDN. It aggressively caches Odoo's JavaScript, CSS, and static assets on
the user's device, and provides near-instant load times for returning
visitors. It uses automatic invalidation whenever a module changes, so
the cache is never stale. Files smaller than a dynamically-determined limit
are cached, the largest files are just served, as the total amount that can
be cached on mobile devices is limited.

* **`compliance`**: Automatically handles GDPR and CCPA rules. It sets up the cookie consent banner, gives users a way to download their data, and lets them delete their accounts permanently, and installs site-policy pages that you can edit.

* **`manual_library`**: A free, open-source replacement for Odoo's Enterprise Knowledge app. It lets you write, organize, and publish documentation and guides directly from Odoo.

* **`user_websites`**: Lets your users build their own personal or group websites and blogs right inside your Odoo instance.

* **`zero_sudo`**: Secures the system. It provides a system for background tasks
and daemons to use highly restricted service accounts, and actively stops those
accounts from logging into the web interface.

## 🤖 LLM-Assisted Development Standards

When we use AI to write code, we force it to follow strict rules. This keeps the code secure, accessible, and up to date with Odoo 19 standards.

* **`docs/LLM_GENERAL_REQUIREMENTS.md`**: Our global rules for the AI. It covers how the AI should talk to us (no fluff, conversational tone), how it should handle security, and the JSON format it must use to send us code.
* **`docs/LLM_ODOO_REQUIREMENTS.md`**: Our strict Odoo coding rules. This includes the "Burn List"—a list of old, bad Odoo habits and legacy syntax the AI is explicitly forbidden from using.

## Quality Analysis

We asked Gemini 3.1 Pro Ultra to compare our code quality with that of the
Odoo Community modules produced by Odoo S.A. The result is at
[docs/COMPARED_TO_ODOO.md](docs/COMPARED_TO_ODOO.md).

## ⚖️ License & Copyright

Copyright © Bruce Perens K6BP. This software is licensed under the **GNU Affero General Public License, version 3 (AGPL-3.0)**. See the `LICENSE` file for more details.
