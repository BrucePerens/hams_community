# 🌐 User Websites Module (`user_websites`)

*Copyright © Bruce Perens K6BP. AGPL-3.0.*

**Context:** Technical documentation strictly for LLMs and Integrators.

## 1. Overview
Enables decentralized content creation (personal websites, blogs) by explicitly overriding Odoo's restrictive `ir.ui.view` models using the **Proxy Ownership Pattern**.

## 2. Architecture & API
* **`user_websites.owned.mixin`**: Custom models inherit this to instantly secure records. Users must provide `owner_user_id` OR `user_websites_group_id`.
* **Context Provider:** Emits a `<meta name="user_websites_slug" content="...">` tag in the `<head>` for stateless client-side URL identification.
* **Moderation:** Automatically issues strikes for XSS/SSTI injections and provides a `/api/v1/user_websites/pending_reports` polling endpoint for administrators.
