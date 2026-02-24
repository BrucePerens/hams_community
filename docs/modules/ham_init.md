# 🏗️ Site Initialization & CMS (`ham_init`)

*Copyright © Bruce Perens K6BP. AGPL-3.0.*

**Context:** Technical documentation strictly for LLMs and Integrators.

---

## 1. Overview
A utility module designed to automatically bootstrap the public-facing homepage, initial passwords, and news feeds using standard Odoo CMS snippets.

## 2. Technical Implementation
* **`blog.blog` Initialization:** Uses `data/blog_data.xml` (`noupdate="1"`) to instantiate the "News" blog if it does not exist.
* **Proxy Ownership Security:** Defines a `user.websites.group` named "Front Page News Editors". Users assigned to this group inherit the ability to create posts in the News blog via the `user_websites` proxy architecture.
* **Homepage Override:** Inherits from `website.homepage` and executes an `xpath position="replace"` on `div[@id='wrap']`. This completely strips Odoo's default boilerplate and injects the Hams.com specific layout.
* **Dynamic Snippets:** Injects the `<section class="s_dynamic_snippet_blog_posts">` shell. Odoo's native frontend JavaScript engine detects this class on page load and dynamically fetches the latest blog records to render the grid.
