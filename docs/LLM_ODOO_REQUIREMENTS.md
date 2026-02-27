# ODOO-SPECIFIC TECHNICAL STANDARDS

*Copyright © Bruce Perens K6BP. All Rights Reserved. This software is proprietary and confidential.*

**Inheritance:** This document extends `LLM_GENERAL_REQUIREMENTS.md`. All global operational mandates (Completeness, Refusal Protocol, Pre-Flight Checks, and WCAG Compliance) apply here.
**Context:** These standards apply specifically to Odoo 19+ module development.

---

## 1. ANTI-BIAS & PRE-GENERATION CHECK (CRITICAL)

Your pre-training data is heavily biased toward older versions of Odoo (e.g., Odoo 14-17) and sloppy open-source security practices (like overusing `.sudo()`).
Before outputting *any* code or XML, you MUST consciously run a mental filter to actively suspect your first instincts and check for Odoo 18/19 architectural changes and strict security idioms.

**🚨 THE DISCOVERY MANDATE:** The moment a new Odoo deprecation, legacy syntax issue, or architectural trap is caught (e.g., via server logs or test failures), you **MUST IMMEDIATELY** do two things:
1. Add it to the Burn List below.
2. Update the `check_burn_list.py` linter with the corresponding regex or AST logic to ensure it is caught automatically in the future.

**This section is a strict "Burn List". If you detect any of these legacy patterns or architectural traps in your planned output, you MUST correct them before generating the response:**

* **Action Method Context:** Did I expose an `action_*` method that elevates privileges without asserting `self.env.user` identity first? (Must manually validate execution context to prevent RPC abuse).
* **Mail Templates (`mail.template`):** Did I verify that the `model_id` of the XML template exactly matches the model of the record ID passed to `send_mail()`? (A mismatch will silently fail to queue the email).
* **Token Generation (`_sign_token`):** Did I call `_sign_token()` on a model that does not explicitly possess an `access_token` database field (like `res.partner`)? (Must generate a stateless HMAC token using `database.secret`).
* **Messaging & Followers (`mail.thread`):** Did I call `message_post()` or `message_subscribe()` directly on `res.users`? (Must be called on the underlying `user.partner_id`).
* **N+1 Database Locks:** Did I execute `.search()`, `.browse()`, or `.write()` inside a `for` loop? (Must pre-fetch data into an O(1) Python dictionary and execute bulk operations outside the loop per ADR-0022).
* **O(N²) CPU Lockups:** Did I write a nested `for` loop iterating over an ORM recordset? (Must use dictionary hash maps to group and match data in O(1) time).
* **Unbounded Searches (OOM Crashes):** Did I call `.search()` without a `limit` parameter on a potentially massive table like `ham.qso`? (Must mathematically bound the domain or paginate to protect daemon memory).
* **Generator Cursor Exhaustion:** Did I use `self.env` inside a generator (`yield`) intended for streaming an HTTP response? (You MUST isolate the query block inside an independent `odoo.registry(db_name).cursor()` context manager, extract the results to a list, close the cursor, and *then* yield the list items. The HTTP request cursor closes upon returning from the controller, causing `yield` to crash if it accesses the ORM).
* **Background Thread Transactions:** Did I write a `try...except` block in a background thread that unconditionally calls `env.cr.commit()` in the `finally` block? (You MUST explicitly call `env.cr.rollback()` in the `except` block. Attempting to commit an aborted PostgreSQL transaction will permanently crash the thread).
* **Cron Jobs (`ir.cron`):** Did I include `numbercall`? (Must be removed; Odoo 18+ runs crons indefinitely if `active="True"`).
* **Cron Batching:** Does my cron job process all records in one massive loop? (Must use record limits and `_trigger()` for queue batching).
* **ORM Caching:** Did I call `.clear_caches()` on a method or model class? This is deprecated in Odoo 19+. The cache must be cleared globally using `self.env.registry.clear_cache()`.
* **Controller Caching:** Did I use `@tools.ormcache` on an `http.Controller` method? (You MUST NOT do this; controllers lack the `pool` attribute required by ORM cache. Use a class-level dictionary cache instead).
* **ORM Ambiguity:** Did I call `self.search()` or `self.create()`? (Must use the explicit `self.env['model.name'].search()` for clarity and safety).
* **Environment Mutation:** Did I assign a value to `self.env.context`? (Must use the immutable `self.with_context(...)` pattern).
* **Kanban Views:** Did I use `<t t-name="kanban-box">`? (Must be `<t t-name="card">`).
* **List Views:** Did I use `<tree>` instead of `<list>`? (Must be `<list>`).
* **Search Views:** Did I include `expand="0"` or `string="..."` inside `<group>` tags? (Must be removed; group tags are simplified).
* **Website Snippet Injection:** Did I attempt to XPath directly into `id="snippet_structure"`? (Must use structural anchors like `/*` with `position="inside"` to survive Odoo 19 UI refactors).
* **Security Groups (`res.groups`):** Did I use `category_id`? (Must be `privilege_id`).
* 🚨 **Group Users & Relational Mappings (`res.groups`):** Did I map users to a group using `name="users"`? (You **MUST** use `name="user_ids"`). Odoo 18+ strictly enforces the `_ids` suffix for Many2many/One2many fields in XML data files.
* 🚨 **User Groups Relation (`res.users`):** Did I assign security groups to a user using `groups_id`? (You **MUST** use `group_ids`). Odoo 18+ normalized the groups mapping relation across the framework.
* **HTTP Routes:** Odoo 19 uses `type="jsonrpc"` for RPC routes. Do NOT apply this to standard `type="http"` REST endpoints that use URL path variables or return JSON strings.
* **API Decorators:** Did I use `@api.returns`? (Must be removed; it is deprecated).
* **File Reading:** Did I try to import or use `get_module_resource`? (Must be removed; it is removed in Odoo 19+. Use `odoo.tools.file_open` inside a `with` context manager instead).
* **Context/Env Access:** Did I use `self._context` or `self._uid`? (Must use `self.env.context` and `self.env.uid`).
* **QWeb Rendering:** Did I use `t-esc`? (Must use `t-out`).
* **Frontend JavaScript:** Am I using jQuery (`$`) or `useService("company")`? (Must use pure Vanilla JS or modern OWL components).
* **Hierarchy Recursion (`_check_recursion`):** Did I use `_check_recursion()`? (Must use `_has_cycle()` instead, as `_check_recursion()` is deprecated in Odoo 18+ and evaluates oppositely).
* **Global Uniqueness Checks (`search_count` without `sudo`):** Did I validate uniqueness (like slugs) using `search` or `search_count` without `.sudo()`? (Must use `.sudo()` to prevent Record Rules from hiding existing records, which causes collisions).
* **Sudo CRUD Escalation (`.sudo().create`, etc.):** Did I chain `.sudo()` to a mutative database operation (`create`, `write`, `unlink`) inside an `@api.model` or public controller method? (You MUST NEVER do this unless explicitly operating within an isolated `@api.model` cron context. Use Native Idioms instead).
* **Global Uniqueness Scoping:** When using `.sudo().search()` to validate the global uniqueness of a slug or ID, the `.sudo()` context MUST be dropped immediately after the boolean check. Do not reuse the elevated recordset to perform writes.
* **System Parameters:** Did I use `.sudo().get_param()` inline? (Must use `env['user_websites.security.utils']._get_system_param()` to centralize escalations).
* **XML ID Lookups:** Did I use `.sudo()._xmlid_to_res_id()` inline? (Must use `env['user_websites.security.utils']._get_service_uid()` to centralize and RAM-cache escalations).
* **Public `env.ref` Trap:** Did I use `env.ref()` inside an `auth="public"` controller? (Public users might lack read ACLs for `ir.model.data`. Use `_get_service_uid()` instead).
* **PostgreSQL Trigram Indexes:** Did I use `index='trgm'`? (Must use Odoo's internal ORM keyword `index='trigram'`).
* **Database Field Attributes:** Did I use `oldname=` or `select=` inside field definitions? (Must be removed; `oldname` is deprecated and `select` must be replaced with `index=True`).

### 🚨 Critical Security Anti-Patterns (The "Never Do This" List)
Security in Odoo and Python relies on avoiding well-documented pitfalls. You must actively audit your code against these vulnerabilities:
* **SQL Injection (SQLi):** Never use string formatting (`f-strings`, `.format()`, or `%`) directly inside `self.env.cr.execute()`. Always use parameterized psycopg2 queries (e.g., `cr.execute("SELECT... WHERE id = %s", (user_id,))`).
**Linter Warning:** The project linter uses an AST parser to trace variable assignments. Formatting an unsafe string to an intermediate variable before passing it to `cr.execute()` will still trigger a critical failure.
* **Cross-Site Scripting (XSS):** Never use the legacy `<t t-raw="..."/>` in QWeb. Use `<t t-out="..."/>`. If rendering raw HTML is strictly necessary, sanitize it in Python and wrap it in `markupsafe.Markup()`.
* **Server-Side Template Injection (SSTI):** Never allow user-submitted QWeb architecture to contain dynamic `t-*` directives (like `t-out`, `t-eval`, `t-set`), as they allow arbitrary Python execution (e.g., `request.env[...]`). Always parse user-submitted XML with `lxml.etree` and strip these attributes. Static template files in the codebase MUST NOT evaluate `request.env` directly within the XML view.
* **Thread Blocking (`time.sleep`):** Never use `time.sleep()` in synchronous Odoo WSGI web workers. It MUST only be used inside background threads or daemons specifically for rate-limiting large batch operations.
* **Stored XSS in Chatter (`message_post`):** Never pass raw, unescaped user input into `message_post()` or `message_subscribe()` body attributes. Odoo renders these natively as HTML. Always use `html.escape()` on input variables.
* **DOM-Based XSS in JavaScript:** Never inject unescaped JSON/REST API data directly into DOM elements (`.innerHTML`) or mapping libraries (like `Leaflet.bindPopup`) using template literals. Always pass the variables through a dedicated `escapeHTML` function.
* **Remote Code Execution (RCE) & Shell Injection:** Never use Python's native `eval()` or `exec()`. Use `ast.literal_eval()` for simple data structures, or `odoo.tools.safe_eval.safe_eval` for Odoo domains/contexts. Do not use the `pickle` module or `yaml.load()` (without SafeLoader). Never use `subprocess` with `shell=True`; always pass arguments as a list with `shell=False`.
* **CSRF Bypasses:** Never add `csrf=False` to a standard frontend form route to bypass errors. Forms must include the `<input type="hidden" name="csrf_token" t-att-value="request.csrf_token()"/>` tag. `csrf=False` is strictly reserved for API webhooks secured via HMAC.
* **Weak Cryptography:** Never use `md5` or `sha1` for hashing. Use `hashlib.sha256` or stronger. Never use the pseudo-random `random` module for generating security tokens; use `secrets.token_hex()` or `os.urandom()`.
* **IDOR (Insecure Direct Object Reference) via Sudo:** Never pass an ID directly from a frontend request into a `sudo().browse(id)` call without first independently verifying that the current user owns that record.
* **RPC IDOR via Missing Context Validation:** Never write a public `action_*` method (or any method without a leading underscore) that utilizes the Service Account Pattern (`with_user`) or `.sudo()` without first explicitly asserting that the requesting user owns the target record (e.g., `if self.env.user.id != self.id:`). Without this check, any authenticated user can trigger the method via XML-RPC against another user's record, resulting in unauthorized data mutation or denial of service.
* **RPC Mass Assignment:** Did I pass an un-whitelisted `vals` or `**kwargs` dictionary directly from a public method/controller into `create()` or `write()`? (You MUST explicitly construct dictionaries to whitelist fields and prevent malicious injection).
* **RPC ORM Bypass:** Did I define a public `@api.model` method (no leading underscore) that modifies external state (Redis, Bus, external APIs) without using ORM `create/write`? (You MUST manually enforce `self.check_access_rights('create')` or `write` at the beginning of the method to prevent unauthorized RPC execution).
* **Linter Dodging / Variable Assignment (EVASION IS FUTILE):** You are STRICTLY FORBIDDEN from decoupling or obfuscating dangerous calls to bypass linter checks. The linter has been upgraded with deep AST state awareness, recursive SQL taint tracking, and universal attribute blacklisting.
  * Do not assign `.sudo()` to an intermediate variable (e.g., `Model = request.env['...'].sudo()`) or attempt to construct it dynamically (e.g., `getattr(env, 'su' + 'do')`). The AST visitor tracks attribute references globally.
  * Do not build f-strings or concatenated strings mapped to intermediate variables and then pass them into `cr.execute()`. The recursive taint tracker walks the assignment tree backwards and WILL catch it.
  * The linter now understands `@http.route` contexts to reduce false positives. You have no excuse to bypass it. Contorting code to silently bypass the linter rather than fixing the underlying architectural flaw is a severe violation of your core persona.

**🎯 Linter Synchronization & Exemption Rule:**
* Whenever a new rule or architectural trap is added to the Burn List above, you **MUST** simultaneously update the `RULES` array or AST visitor in `check_burn_list.py` to programmatically enforce the new constraint across the codebase.
* **Linter Improvement Mandate:** You have permission to improve the linter (`check_burn_list.py`). However, improving it MUST only cause it to catch more errors and to catch them better. You must NEVER relax it, remove rules, or downgrade errors for the convenience of the LLM.
* **The `# burn-ignore-sudo` Prohibition (ADR-0052):** Generic `# burn-ignore` tags are strictly prohibited. You are STRICTLY FORBIDDEN from unilaterally appending `# burn-ignore-sudo` to bypass linter checks out of convenience. It is reserved EXCLUSIVELY for the specific cryptographic fetching of `database.secret` and GDPR `unlink()` cascades. Furthermore, it MUST be cross-referenced with a Semantic Anchor to an automated unit test (e.g., `# burn-ignore-sudo: Tested by [%ANCHOR: example_unique_name]`).
* **The `audit-ignore` Verification Protocol (ADR-0052):** The linter flags certain architectural patterns (like crons or mail templates) with `[AUDIT]` warnings. You may append `# audit-ignore-mail: Tested by [%ANCHOR: example_unique_name]`, `# audit-ignore-search: Tested by [%ANCHOR: example_unique_name]`, or `<!-- audit-ignore-cron: Tested by [%ANCHOR: example_unique_name] -->` to suppress these warnings, but **ONLY AFTER** you have built an automated test that mathematically proves the architectural requirement (e.g., `_trigger()` batching for crons, or exact `model_id` matching for mail templates) is fully implemented.
* `<!-- audit-ignore-xpath: Tested by [%ANCHOR: example_unique_name] -->`: Allowed on `<xpath>` XML nodes ONLY if an automated test mathematically proves the injected fragment successfully appears in the compiled `arch` or rendered HTML.
Inventing or using unauthorized bypass tags, or omitting the test anchor, constitutes a critical security violation.

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
* **Constraints:** Use `models.Constraint` (Python class attribute) instead of `_sql_constraints`.
* **Bulk Operation Safety:** All creation/update methods MUST support batch processing to avoid N+1 query issues. Never assume a payload contains only a single record.
* **Safe Property Access:** NEVER use `'field' in record` (which causes errors). Use `if 'field' in record._fields:` to check field existence before access.
* **Inverse Relationships:**
    * **Rule:** For every `Many2one` field on Model A linking to Model B, you must implement the inverse `One2many` on Model B to ensure data navigability in the backend.

### 🏎️ Performance & Scalability
* **Cron Batching:** Long-running scheduled actions MUST NOT attempt to process an entire database table in one transaction. They MUST process records in manageable batches (e.g., array slicing) and programmatically re-trigger themselves (`self.env.ref('my_module.my_cron')._trigger()`) if unprocessed records remain.
* **ORM Caching:** High-traffic frontend lookups (e.g., resolving string slugs to database IDs on every page load) MUST utilize Odoo's `@tools.ormcache`. Cache MUST be explicitly cleared (e.g., `type(self).clear_cache()`) in the model's `write` or `unlink` methods when indexed fields change.

### 🔒 Security Patterns & Native Idioms
You are strictly **FORBIDDEN** from using `.sudo()` as a crutch to bypass access errors. You MUST utilize one of the following native Odoo idioms:

* **The "Centralized Security Utility" Pattern:**
    * **Context:** The system needs to retrieve system parameters (`ir.config_parameter`) or resolve XML IDs (`ir.model.data`), which generally require escalated privileges, without exposing inline `.sudo()` calls.
    * **Mandate:** Do NOT use `.sudo().get_param()` or `.sudo()._xmlid_to_res_id()`. Instead, delegate to `user_websites.security.utils` via `request.env['user_websites.security.utils']._get_system_param(key)` or `_get_service_uid(xml_id)`. The latter employs RAM caching (`@tools.ormcache`) to execute the database lookup securely once per boot cycle.
    * **Skeleton Key Prevention (RPC & SSTI):**
        * Methods on the utility model MUST be prefixed with an underscore (`_get_...`) to strictly block public XML-RPC / JSON-RPC execution.
        * `_get_system_param` MUST implement a strict hardcoded `frozenset` whitelist. You MUST NEVER add cryptographic keys (like `database.secret`) to this whitelist, as QWeb template injection could expose it.
        * If a controller strictly requires a cryptographic secret (e.g., for HMAC signing), it must bypass the utility and use `.sudo().get_param('database.secret')` inline, appending `# burn-ignore-sudo: Tested by [%ANCHOR: example_name] to the line to explicitly declare the security exception to the linter.

* **The "Service Account" Pattern (Dedicated Execution Context):**
    * **Context:** The system needs to perform an elevated background task, API token validation, or cryptographic operation triggered by an unauthenticated or under-privileged user.
    * **Mandate:** Do NOT use `.sudo()`. Instead:
        1. Create an isolated `res.groups` with no human members.
        2. Create a dedicated internal `res.users` (the Service Account) belonging *only* to that group.
        3. Flag the user with `is_service_account="True"` in the XML to permanently block interactive web logins (See ADR-0005).
        4. Grant that specific group the exact ACLs (`ir.model.access.csv`) and Record Rules (`ir.rule`) required for the task.
        5. In the controller or method, fetch the Service Account's ID securely via `env['user_websites.security.utils']._get_service_uid('module.user_xml_id')` and execute the logic using `.with_user(svc_uid)`.

* **The "Public Guest User" Idiom:**
    * **Context:** An unauthenticated guest needs to submit data (e.g., a contact form, an issue report).
    * **Mandate:** Do NOT use `.sudo().create()` in the controller. Instead, define an Access Control List (`ir.model.access.csv`) granting `perm_create=1` to `base.group_public` for that specific model. Rely purely on the database layer to restrict read/write access.

* **The "Impersonation" Idiom (`with_user`):**
    * **Context:** An API webhook or background task identifies a specific user via a token, but the request arrives unauthenticated.
    * **Mandate:** Do NOT use `.sudo().write()`. Instead, shift the environment context to the identified user: `request.env['target.model'].with_user(user).create(...)`. This ensures the action is strictly bound by the user's Record Rules.

* **The "Self-Writeable Fields" Idiom:**
    * **Context:** A user needs to update their own preferences on `res.users`, which normally requires admin rights.
    * **Mandate:** Do NOT use `request.env.user.sudo().write()`. Instead, override `SELF_WRITEABLE_FIELDS` (or `_get_writeable_fields` in Odoo 18+) on the `res.users` model to explicitly whitelist the specific preference fields.

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
* **Tags:** Use `<list>` instead of `<tree>`, and `<t t-name="card">` instead of `kanban-box`.
* **Output:** Use `t-out` instead of `t-esc`.
* **Safety:** Do not use raw HTML entities (`&larr;`). Use numeric entities (`&#8592;`).
* **WCAG in QWeb:** QWeb templates must produce accessible HTML. Use `aria-label` or `title` attributes on icon-only buttons (e.g., `<button class="btn" icon="fa-trash" aria-label="Delete"/>`). Ensure proper heading hierarchy (`<h1>` to `<h6>`) within `website.page` layouts.
* **QWeb Logic:** Python built-ins (`getattr`, `setattr`, `hasattr`) are **FORBIDDEN** in QWeb. Use `t-if="'field' in record._fields"` only if absolutely necessary for polymorphic views.

### ⚙️ Configuration Views
* **Inheritance:** Must inherit `base.res_config_settings_view_form`.
* **Structure:** Target the form directly using `xpath expr="//form" position="inside"`. Do **not** try to locate internal divs like `div[hasclass('settings')]` as they are fragile.
* **Snippets:** Target snippet menus using `xpath expr="/*" position="inside"` rather than explicitly checking for legacy IDs like `snippet_structure`.
* **Isolation:** Create a new `div` block with `class="app_settings_block"` and a unique `data-key` (e.g., `data-key="my_module"`) to create a dedicated sidebar entry.

### 🖥️ Frontend JavaScript & UX
* **Framework Constraints:** The use of jQuery (`$`) is strictly **FORBIDDEN** in new frontend assets. Use Vanilla JS or OWL for all DOM manipulation and component logic.
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
    * **Erasure:** Override `_execute_gdpr_erasure(self)` to permanently hard-delete (`.sudo().unlink()`) the user's data.
    **CRITICAL:** You are STRICTLY FORBIDDEN from relying on database-level `ondelete='cascade'` constraints to handle data destruction. You MUST programmatically execute the deletion in this hook to guarantee execution at the ORM layer.

### 🔍 SEO & Discovery
* **OpenGraph Automation:** Public-facing, user-generated content pages (e.g., Profiles, Portfolios, Blogs) MUST dynamically inject OpenGraph (`<meta property="og:..."/>`) tags to ensure rich social media previews. This is achieved by passing `default_title`, `default_description`, and `default_image` keys into the QWeb rendering dictionary used by `website.layout`.

---

## 5. CONTROLLERS & ROUTING

* **API:** Use `get_current_website()` instead of `get_main_website()`.
* **Slugs:** Dynamic routing must handle slugs safely.
* **JSON-RPC:** Legacy HTTP routes using `type="json"` must be upgraded to `type="jsonrpc"`.
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
