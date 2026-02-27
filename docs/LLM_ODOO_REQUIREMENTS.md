# ODOO-SPECIFIC TECHNICAL STANDARDS

*Copyright © Bruce Perens K6BP. All Rights Reserved. This software is proprietary and confidential.*

**Inheritance:** This document extends `LLM_GENERAL_REQUIREMENTS.md`. All global operational mandates (Completeness, Refusal Protocol, Pre-Flight Checks, and WCAG Compliance) apply here.
**Context:** These standards apply specifically to Odoo 19+ module development.

---

## 1. ANTI-BIAS & THE BURN LIST (CRITICAL)

Your pre-training data is heavily biased toward older versions of Odoo (e.g., Odoo 14-17) and sloppy open-source security practices. Before outputting *any* code or XML, you MUST consciously run a mental filter to actively suspect your first instincts.

You MUST consult the **[LLM Linter Guide](LLM_LINTER_GUIDE.md)** for the exhaustive, authoritative list of banned syntax, legacy patterns, and security traps. 

**🚨 The Discovery Mandate & Linter Synchronization:**
* Whenever a new rule or architectural trap is discovered, you **MUST** simultaneously update the `RULES` array or AST visitor in `check_burn_list.py` to programmatically enforce the new constraint, and document it in the [LLM Linter Guide](LLM_LINTER_GUIDE.md).
* **Architectural Adherence Policy:** You MUST respect the architectural intent of our linters (`check_burn_list.py`) by fixing the underlying logic of triggered rules. Ensure that code remains syntactically pure and secure without employing evasive semantic tricks.
* You MUST avoid assigning elevated context properties to intermediate variables dynamically.
* You MUST use parameterized psycopg2 queries directly; do not build f-strings mapped to intermediate variables and pass them into execution.
* You MUST resolve architectural flaws at their root, preserving the structural and security integrity of the Odoo framework.
* **Bypass Protocols (`audit-ignore` / `burn-ignore`):** The strict requirements for bypassing the linter using automated AST test verification are exhaustively documented in the [LLM Linter Guide](LLM_LINTER_GUIDE.md).

---

## 2. ARCHITECTURE & COMMUNITY REUSE (NATIVE ECOSYSTEM FIRST)

* **The Reusability Mandate:** Before architecting a new custom module from scratch, you **MUST** actively evaluate existing Odoo 19 Community modules (e.g., `event`, `survey`, `membership`, `website_slides`, `forum`, `website_sale`) to determine if they can fulfill the core functional requirements.
* **Specialization Over Silos:** Do not build redundant custom CRUD pipelines or base architectures for features that Odoo already handles natively. Instead, build lightweight "Domain Extension" modules that inherit (`_inherit` or `_inherits`) from the core Community modules to inject domain-specific fields, validation logic, and security rules.
* **Compatibility Check:** You must mentally ensure that the targeted community module exists and retains the required functionality in **Odoo 19** before committing to its use.
* **External Daemons & Workers:** Long-running processes, heavy ETL tasks, or persistent sockets MUST NOT run inside Odoo WSGI workers. They MUST be offloaded to external Python daemons communicating via XML-RPC. Whenever you architect such a module, you **MUST** offer to write the external daemon. Audits must actively scan for modules that specify a daemon dependency where the daemon does not yet exist.

---

## 3. PYTHON & ORM STANDARDS

### 📂 File Organization
* **Modular Extensions:** Organize code by Model.
    * For new models: Use `models/model_name.py`.
    * For extending core models (e.g., `res.users`):
        * Small extensions (<100 lines): Append to `models/res_users.py` if it exists.
        * Feature-specific extensions: Create `models/res_users_feature.py` (e.g., `res_users_website.py`) to maintain separation of concerns.

### 🗄️ Models & Logic
* **Constraints:** Use `models.Constraint` (Python class attribute) instead of the banned legacy syntax.
* **Bulk Operation Safety:** All creation/update methods MUST support batch processing to avoid N+1 query issues. Never assume a payload contains only a single record.
* **Safe Property Access:** NEVER use `'field' in record` (which causes errors). Use `if 'field' in record._fields:` to check field existence before access.
* **Inverse Relationships:**
    * **Rule:** For every `Many2one` field on Model A linking to Model B, you must implement the inverse `One2many` on Model B to ensure data navigability in the backend.

### 🏎️ Performance & Scalability
* **Cron Batching:** Long-running scheduled actions MUST NOT attempt to process an entire database table in one transaction. They MUST process records in manageable batches (e.g., array slicing) and programmatically re-trigger themselves (`self.env.ref('my_module.my_cron')._trigger()`) if unprocessed records remain.
* **ORM Caching:** High-traffic frontend lookups (e.g., resolving string slugs to database IDs on every page load) MUST utilize Odoo's `@tools.ormcache`. Cache MUST be explicitly cleared (e.g., `self.env.registry.clear_cache()`) in the model's `write` or `unlink` methods when indexed fields change.

### 🔒 Security Patterns & Native Idioms
You are strictly **FORBIDDEN** from using absolute database overrides as a crutch to bypass access errors (See [LLM Linter Guide](LLM_LINTER_GUIDE.md)). You MUST utilize one of the following native Odoo idioms:

* **The "Centralized Security Utility" Pattern:**
    * **Context:** The system needs to retrieve system parameters (`ir.config_parameter`) or resolve XML IDs (`ir.model.data`), which generally require escalated privileges.
    * **Mandate:** Delegate to `user_websites.security.utils` via `request.env['user_websites.security.utils']._get_system_param(key)` or `_get_service_uid(xml_id)`. The latter employs RAM caching (`@tools.ormcache`) to execute the database lookup securely once per boot cycle.
    * **Skeleton Key Prevention (RPC & SSTI):**
        * Methods on the utility model MUST be prefixed with an underscore (`_get_...`) to strictly block public XML-RPC / JSON-RPC execution.
        * `_get_system_param` MUST implement a strict hardcoded `frozenset` whitelist. You MUST NEVER add cryptographic keys (like `database.secret`) to this whitelist, as QWeb template injection could expose it.
        * If a controller strictly requires a cryptographic secret (e.g., for HMAC signing), it must bypass the utility and declare a security exception (See [LLM Linter Guide](LLM_LINTER_GUIDE.md)).

* **The "Service Account" Pattern (Dedicated Execution Context):**
    * **Context:** The system needs to perform an elevated background task, API token validation, or cryptographic operation triggered by an unauthenticated or under-privileged user.
    * **Mandate:**
        1. Create an isolated `res.groups` with no human members.
        2. Create a dedicated internal `res.users` (the Service Account) belonging *only* to that group.
        3. Flag the user with `is_service_account="True"` in the XML to permanently block interactive web logins (See ADR-0005).
        4. Grant that specific group the exact ACLs (`ir.model.access.csv`) and Record Rules (`ir.rule`) required for the task.
        5. In the controller or method, fetch the Service Account's ID securely via `env['user_websites.security.utils']._get_service_uid('module.user_xml_id')` and execute the logic using `.with_user(svc_uid)`.

* **The "Public Guest User" Idiom:**
    * **Context:** An unauthenticated guest needs to submit data (e.g., a contact form, an issue report).
    * **Mandate:** Define an Access Control List (`ir.model.access.csv`) granting `perm_create=1` to `base.group_public` for that specific model. Rely purely on the database layer to restrict read/write access.

* **The "Impersonation" Idiom (`with_user`):**
    * **Context:** An API webhook or background task identifies a specific user via a token, but the request arrives unauthenticated.
    * **Mandate:** Shift the environment context to the identified user: `request.env['target.model'].with_user(user).create(...)`. This ensures the action is strictly bound by the user's Record Rules.

* **The "Self-Writeable Fields" Idiom:**
    * **Context:** A user needs to update their own preferences on `res.users`, which normally requires admin rights.
    * **Mandate:** Override `SELF_WRITEABLE_FIELDS` (or `_get_writeable_fields` in Odoo 18+) on the `res.users` model to explicitly whitelist the specific preference fields.

* **Privilege Hierarchy (Odoo 19+):** When defining security groups in XML, `res.groups` must not link directly to a `category_id`. They MUST be nested under a `res.groups.privilege` record (via `privilege_id`), which in turn links to the `ir.module.category`.

### 🧩 Module Initialization & Dynamic Documentation Injection
* **Documentation Payload Injection:** Every module must expose its documentation to the platform's native `knowledge.article` structure dynamically via a `post_init_hook` in `hooks.py`.
* **Decoupled Content (`file_open`):** HTML documentation payloads must reside in separate files (e.g., `data/documentation.html`). Use Odoo's native `odoo.tools.file_open` utility inside the hook to read the file securely. **Never hardcode HTML into Python.**
* **Soft Dependency Management:** The platform `knowledge.article` API (via `manual_library` or Enterprise) must be treated as a **Soft Dependency**.
    * Do NOT explicitly list it in the `depends` block of `__manifest__.py` unless the module fundamentally cannot operate without it.
    * The `post_init_hook` MUST explicitly check for the API's presence before attempting creation: `if 'knowledge.article' in env: ...`.

---

## 4. XML, VIEWS & QWEB STANDARDS

### 🎨 View Syntax & Accessibility
* **Safety:** Do not use raw HTML entities (`&larr;`). Use numeric entities (`&#8592;`).
* **WCAG in QWeb:** QWeb templates must produce accessible HTML. Use `aria-label` or `title` attributes on icon-only buttons (e.g., `<button class="btn" icon="fa-trash" aria-label="Delete"/>`). Ensure proper heading hierarchy (`<h1>` to `<h6>`) within `website.page` layouts.
* **QWeb Logic:** Python built-ins (`getattr`, `setattr`, `hasattr`) are **FORBIDDEN** in QWeb. Use `t-if="'field' in record._fields"` only if absolutely necessary for polymorphic views.

### ⚙️ Configuration Views
* **Inheritance:** Must inherit `base.res_config_settings_view_form`.
* **Structure:** Target the form directly using `xpath expr="//form" position="inside"`. Do **not** try to locate internal divs like `div[hasclass('settings')]` as they are fragile.
* **Snippets:** Target snippet menus using `xpath expr="/*" position="inside"` rather than explicitly checking for legacy IDs.
* **Isolation:** Create a new `div` block with `class="app_settings_block"` and a unique `data-key` (e.g., `data-key="my_module"`) to create a dedicated sidebar entry.

### 🖥️ Frontend JavaScript & UX
* **Native Toast Notifications:** Frontend feedback for transient actions (e.g., successfully submitting a form, handled via URL parameters like `?success=1`) MUST trigger Odoo's native notification bus (Toast messages) rather than relying solely on static inline text renders.

### 🌍 Internationalization (i18n)
* **Translation Architecture:** Every user-facing module MUST include an `i18n/` directory containing a base `module_name.pot` file.
* **Required Languages:** The module MUST also contain `.po` translated files for the seven most popular languages: German (`de.po`), Spanish (`es.po`), French (`fr.po`), Italian (`it.po`), Japanese (`ja.po`), Dutch (`nl.po`), and Portuguese (`pt.po`).
* **Implementation:** Ensure all user-facing strings in Python (using `_()`), XML, and QWeb templates are properly marked for Odoo's translation engine.

### ⚖️ Regulatory Compliance & Cookie Management
* **Native Consent Integration:** Custom modules MUST integrate with and respect Odoo's native website cookie consent mechanism (`website.cookies_bar`).
* **Prohibition:** You are strictly **FORBIDDEN** from implementing custom, hardcoded cookie banners or third-party consent scripts. All tracking must hook into the core framework's consent state.
* **Data Portability & Erasure (GDPR/CCPA):** Any module that stores Personally Identifiable Information (PII) or user-generated content MUST integrate into the global GDPR framework by extending `res.users`:
    * **Export:** Override `_get_gdpr_export_data(self)` to append the user's records to the export dictionary.
    * **Erasure:** Override `_execute_gdpr_erasure(self)` to permanently cascade delete the user's data. You MUST programmatically execute the deletion in this hook to guarantee execution at the ORM layer.

### 🔍 SEO & Discovery
* **OpenGraph Automation:** Public-facing, user-generated content pages (e.g., Profiles, Portfolios, Blogs) MUST dynamically inject OpenGraph (`<meta property="og:..."/>`) tags to ensure rich social media previews. This is achieved by passing `default_title`, `default_description`, and `default_image` keys into the QWeb rendering dictionary used by `website.layout`.

---

## 5. CONTROLLERS & ROUTING

* **API:** Use `get_current_website()` instead of `get_main_website()`.
* **Slugs:** Dynamic routing must handle slugs safely.
* **Auth:** Routes creating content must require `auth="user"`. Routes for reading content can be `auth="public"`.
* **Public Route Anti-Spam:** All unauthenticated `POST` routes (e.g., public forms, abuse reports) MUST implement anti-spam measures. Use Odoo's native reCAPTCHA context or honeypot fields to prevent malicious bot automation.
* **Standard Template Context:** When rendering built-in Odoo templates (e.g., `website_blog.blog_post_short`), you MUST verify the template's source code and ensure all expected QWeb context variables (e.g., `pager`, `main_object`, `blogs`) are injected into the rendering dictionary to prevent `KeyError` crashes.
* **Explicit Parameter Binding:** When defining HTTP controller methods, you **MUST** explicitly declare expected form inputs and query parameters in the method signature (e.g., `def my_route(self, my_param=None, **kwargs):`) rather than relying solely on `kwargs.get()` or `request.params`. This guarantees reliable parameter binding when executing automated HTTP tests via `self.url_open()` and prevents silent validation bypasses.

---

## 6. ODOO VERIFICATION & AUDIT PROTOCOL

Please refer to the `FINAL VERIFICATION & AUDIT PROTOCOL` section within `LLM_GENERAL_REQUIREMENTS.md` for the overarching checklist regarding Registry, Imports, Schema Sync, Authorization, Test Coverage, and Accessibility.

---

## 7. OUTPUT FORMATTING

Please refer to the `OUTPUT FORMATTING & TRANSPORT PROTOCOLS` section within `LLM_GENERAL_REQUIREMENTS.md` for the strict AEF 4.0 JSON structure, Base64 prohibition, and UI-crashing tag mitigation mandates.
