# 🏗️ Site Initialization & CMS (`ham_init`)

*Copyright © Bruce Perens K6BP. AGPL-3.0.*

<system_role>
**Context:** Technical documentation strictly for LLMs and Integrators.
</system_role>

<overview>
## 1. Overview
Utility module to bootstrap the public homepage and CMS. Installs its documentation payload automatically. [@ANCHOR: doc_inject_ham_init]
</overview>

<implementation>
## 2. Technical Implementation
* Provisions a "News" `blog.blog` via `noupdate="1"` XML.
* Defines a `user.websites.group` for "Front Page News Editors" using Proxy Ownership.
* Overrides the `website.homepage` to strip Odoo boilerplate and inject a custom layout with dynamic blog snippets.
</implementation>

<dependencies>
## 3. External Dependencies
* **Python:** None (Declared in `__manifest__.py`).
</dependencies>
