# Epics & User Stories: HTML Sanitization

## Epic: Extended Content Support
* **Story:** As a content creator, I want to embed interactive elements like scripts and iframes in HTML fields, so I can include external maps, videos, and dynamic widgets. *(Reference: ham_sanitizer/__init__.py -> [@ANCHOR: expand_tag_safelist])*
    * **BDD Criteria:**
        * *Given* the Odoo mail module is loaded
        * *When* the `ham_sanitizer` module initializes
        * *Then* `script`, `iframe`, and `dfn` tags MUST be added to the `safe_html_tags` list.
* **Story:** As a developer, I want specific HTML attributes like `allowfullscreen` and `async` to be preserved during sanitization, so that embedded content functions correctly. *(Reference: ham_sanitizer/__init__.py -> [@ANCHOR: expand_attribute_safelist])*
    * **BDD Criteria:**
        * *Given* the Odoo mail module is loaded
        * *When* the `ham_sanitizer` module initializes
        * *Then* attributes like `src`, `allowfullscreen`, and `async` MUST be added to the `safe_html_attributes` list.
* **Story:** As a system administrator, I want the underlying HTML cleaner to be globally configured to allow scripts and frames, ensuring consistent behavior across all Odoo components. *(Reference: ham_sanitizer/__init__.py -> [@ANCHOR: patch_lxml_cleaner])*
    * **BDD Criteria:**
        * *Given* the `lxml_html_clean` library is in use
        * *When* a `Cleaner` instance is initialized
        * *Then* it MUST be forced to set `scripts=False` and `frames=False` regardless of the initial arguments.
