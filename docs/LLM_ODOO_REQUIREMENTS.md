# ODOO-SPECIFIC TECHNICAL STANDARDS

## Metadata

* *Copyright © Bruce Perens K6BP. All Rights Reserved. This software is proprietary and confidential.*

* *Inheritance:* This document extends `LLM_GENERAL_REQUIREMENTS.md`. All global operational mandates apply here.
* *Context:* These standards apply specifically to Odoo 19+ module development.

## 1. ANTI-BIAS & THE BURN LIST (CRITICAL)

Your pre-training data is heavily biased toward older versions of Odoo (e.g., Odoo 14-17) and sloppy open-source security practices.
Before outputting *any* code or XML, you MUST consciously run a mental filter to actively suspect your first instincts.
You MUST consult the **[LLM Linter Guide](LLM_LINTER_GUIDE.md)** for the exhaustive, authoritative list of banned syntax, legacy patterns, and security traps.

**🚨 The Discovery Mandate & Linter Synchronization:**
* Whenever a new rule or architectural trap is discovered, you **MUST** simultaneously update the `RULES` array or AST visitor in `check_burn_list.py` to programmatically enforce the new constraint.
* **Architectural Adherence Policy:** You MUST respect the architectural intent of our linters by fixing the underlying logic of triggered rules. Ensure that code remains syntactically pure and secure without employing evasive semantic tricks.
* You MUST avoid assigning elevated context properties to intermediate variables dynamically.
* You MUST use parameterized psycopg2 queries directly for data values.
* **Dynamic SQL Mandate:** If you must dynamically alter the query structure or inject schema identifiers (e.g., column names in a SQL View), you are strictly forbidden from using f-strings. You MUST use the `psycopg2.sql` module.

---

## 2. ARCHITECTURE & COMMUNITY REUSE (NATIVE ECOSYSTEM FIRST)

* **The Reusability Mandate:** Before architecting a new custom module from scratch, you **MUST** actively evaluate existing Odoo 19 Community modules (e.g., `event`, `survey`, `website_slides`) to determine if they can fulfill the core functional requirements.
* **Specialization Over Silos:** Do not build redundant custom CRUD pipelines or base architectures for features that Odoo already handles natively. Instead, build lightweight "Domain Extension" modules.
* **Compatibility Check:** You must mentally ensure that the targeted community module exists and retains the required functionality in **Odoo 19** before committing to its use.
* **External Daemons & Workers:** Long-running processes, heavy ETL tasks, or persistent sockets MUST NOT run inside Odoo WSGI workers. They MUST be offloaded to external Python daemons communicating via XML-RPC.
* **JIT Binary Self-Healing:** When orchestrating third-party applications (like `kopia` or `cloudflared`), use `shutil.which` to detect if the package is installed. If absent, the code should dynamically fetch the pre-compiled static binary.

---

## 3. PYTHON & ORM STANDARDS

### 📂 File Organization
* **Modular Extensions:** Organize code by Model.
  * For new models: Use `models/model_name.py`.
  * For extending core models: Create `models/res_users_feature.py` to maintain separation of concerns.

### 🗄️ Models & Logic
* **Constraints:** Use `models.Constraint` (Python class attribute) instead of the banned legacy syntax.
* **Bulk Operation Safety:** All creation/update methods MUST support batch processing to avoid N+1 query issues.
* **Zero-Orphan Custom Models:** Every single custom model created in Odoo must have at least one corresponding CRUD entry in `ir.model.access.csv`.
* **Inverse Relationships & Test Cache Anomalies:**
  * **Rule:** For every `Many2one` field on Model A linking to Model B, you must implement the inverse `One2many` on Model B.
  * **Test Isolation Mandate:** In Odoo's `TransactionCase`, `One2many` inverse relations are not automatically populated in the local cache immediately after record creation. If a test relies on a `One2many` field, you MUST explicitly wire the relation in the test's `setUp` using the link command. You are strictly **FORBIDDEN** from replacing `One2many` calls with explicit searches in production code just to bypass this test environment caching artifact. If testing a method that iterates over a `One2many` field, you MUST call `self.user.invalidate_recordset()` inside the test *before* executing the method.

### 🏎️ Performance & Scalability
* **Ban Brittle ORM Query Counting in CI/CD:** Do not use `self.assertQueryCount()` to validate functional success. Use deterministic Behavior-Driven Development (BDD) tests instead. For testing ormcache hits, mock the cursor and verify the specific table wasn't queried.
* **Cron Batching:** Long-running scheduled actions MUST NOT attempt to process an entire database table in one transaction. They MUST process records in manageable batches and programmatically re-trigger themselves.
* **ORM Caching:** High-traffic frontend lookups MUST utilize Odoo's `@tools.ormcache`. Cache MUST be explicitly cleared in the model's `write` or `unlink` methods.

---

## 4. SECURITY PATTERNS & NATIVE IDIOMS

You are strictly **FORBIDDEN** from using absolute database overrides (like `.sudo()`) as a crutch to bypass access errors.

* **The Domain Sandbox Mandate:** You MUST NEVER grant `base.group_user` (Internal User) to community members or use it as a catch-all in Record Rules or ACLs. Doing so exposes the internal ERP backend to external users. All external community access MUST be governed by `base.group_portal` combined with custom domain groups. The ONLY exception is the special `odoo_facility_service_internal` proxy account. Use views (`_auto = False`) preferentially rather than increasing privilege when a view will work.

You MUST utilize one of the following native Odoo idioms:

* **The "Centralized Security Utility" Pattern:**
  * **Context:** The system needs to retrieve system parameters or resolve XML IDs.
  * **Mandate:** Delegate to `zero_sudo.security.utils`.
  * **Skeleton Key Prevention (RPC & SSTI):**
      * Methods on the utility model MUST be prefixed with an underscore to strictly block public XML-RPC / JSON-RPC execution.
      * System parameter fetching MUST implement a strict hardcoded `frozenset` whitelist. You MUST NEVER add cryptographic keys to this whitelist.

* **The "Service Account" Pattern (Dedicated Execution Context):**
  * **Context:** The system needs to perform an elevated background task, API token validation, or cryptographic operation triggered by an unauthenticated or under-privileged user.
  * **Mandate:**
      1. Create an isolated `res.groups` with no human members.
      2. Create a dedicated internal `res.users` (the Service Account) belonging *only* to that group.
      3. **Separation of Privilege & Explicit Scoping:** Ensure the account is a *Micro-Service Account* dedicated to a single domain action. Service accounts must be explicitly granted the security groups of the external models they interact with, but only a special user may have `base.group_user`. Do not bundle disparate permissions or fall back to `base.user_admin`.
      4. Flag the user with `is_service_account="True"` in the XML to permanently block interactive web logins.
      5. Grant that specific group the exact ACLs and Record Rules required for the task.
      6. Fetch the Service Account's ID securely and execute the logic using `.with_user(svc_uid)`.

* **The "Public Guest User" Idiom:**
  * **Context:** An unauthenticated guest needs to submit data (e.g., a contact form, an issue report).
  * **Mandate:** Define an Access Control List granting `perm_create=1` to `base.group_public` for that specific model. Rely purely on the database layer to restrict read/write access.

* **The "Impersonation" Idiom:**
  * **Context:** An API webhook or background task identifies a specific user via a token, but the request arrives unauthenticated.
  * **Mandate:** Shift the environment context to the identified user: `request.env['target.model'].with_user(user).create(...)`.

* **The "Login As" Session Swap Idiom:**
  * **Context:** A System Administrator needs to investigate a user's isolated portal state.
  * **Mandate:** Swap the underlying `request.session.uid` directly in the HTTP controller. This action MUST ALWAYS be preceded by a `message_post` to the target user's chatter log to maintain an immutable audit trail.

* **The "Self-Writeable Fields" Idiom:**
  * **Context:** A user needs to update their own preferences on `res.users`.
  * **Mandate:** Override `SELF_WRITEABLE_FIELDS` (or `_get_writeable_fields` in Odoo 18+) on the `res.users` model to explicitly whitelist the specific preference fields.

* **Privilege Hierarchy (Odoo 19+):** When defining security groups in XML, `res.groups` must not link directly to a `category_id`. They MUST be nested under a `res.groups.privilege` record (via `privilege_id`).

### 🧩 Module Initialization & Strict Dependencies
* **Strict Manifest Dependency Declarations:** If a module interacts with, inherits from, or links to a model from another module, that target module **MUST** be explicitly declared in the `depends` array of the manifest file.
* **Documentation Payload Injection:** Every module must expose its documentation to the platform's native `knowledge.article` structure dynamically via a hook. HTML documentation payloads must reside in separate files (e.g., `data/documentation.html`). Use Odoo's native `odoo.tools.file_open` utility inside the hook. **Never hardcode HTML into Python.**

---

## 5. XML, VIEWS & QWEB STANDARDS

### 🎨 View Syntax & Accessibility
* **WCAG in QWeb:** QWeb templates must produce accessible HTML. Use `aria-label` or `title` attributes on icon-only buttons. Ensure proper heading hierarchy.
* **QWeb Logic:** Python built-ins (`getattr`, `setattr`, `hasattr`) are **FORBIDDEN** in QWeb. Use `t-if` to check field existence only if absolutely necessary.

### ⚙️ Menus and Configuration Views
* **Autonomous Menu Roots:** If building a module intended for standalone open-source distribution, it MUST declare its own top-level menu root.
* **Inheritance:** Must inherit `base.res_config_settings_view_form`.
* **Structure:** Target the form directly using `xpath`. Do **not** try to locate internal divs like `div[hasclass('settings')]` as they are fragile.
* **Snippets:** Target snippet menus using `xpath expr="/*"` rather than explicitly checking for legacy IDs.

### 🖥️ Frontend JavaScript & UX
* **Native Toast Notifications:** Frontend feedback for transient actions (e.g., successfully submitting a form) MUST trigger Odoo's native notification bus (Toast messages) rather than relying solely on static inline text renders.

### 🌍 Internationalization (i18n)
* **Translation Architecture:** Every user-facing module MUST include an `i18n/` directory containing a base `.pot` file.
* **Required Languages:** The module MUST also contain `.po` translated files for the seven most popular languages.
* **Implementation:** Ensure all user-facing strings in Python (using `_()`), XML, and QWeb templates are properly marked for Odoo's translation engine.

### ⚖️ Regulatory Compliance & Cookie Management
* **Native Consent Integration:** Custom modules MUST integrate with and respect Odoo's native website cookie consent mechanism. You are strictly **FORBIDDEN** from implementing custom, hardcoded cookie banners.
* **Data Portability & Erasure (GDPR/CCPA):** Any module that stores Personally Identifiable Information (PII) or user-generated content MUST integrate into the global GDPR framework by extending `res.users`:
  * **Export:** Override `_get_gdpr_export_data(self)` to append the user's records to the export dictionary.
  * **Erasure:** Override `_execute_gdpr_erasure(self)` to permanently cascade delete the user's data natively at the ORM layer.

### 🔍 SEO & Discovery
* **OpenGraph Automation:** Public-facing, user-generated content pages (e.g., Profiles, Blogs) MUST dynamically inject OpenGraph tags to ensure rich social media previews by passing keys into the QWeb rendering dictionary used by `website.layout`.

---

## 6. CONTROLLERS & ROUTING

* **Application vs. CMS Page Segregation:** Build system facilities and interactive applications using dedicated HTTP controllers that return standard QWeb `<template>` views. You MUST NOT provision them as CMS-editable `website.page` records in XML unless the paradigm explicitly requires end-user drag-and-drop CMS editing.
* **API:** Use `get_current_website()` instead of `get_main_website()`.
* **Auth:** Routes creating content must require `auth="user"`. Routes for reading content can be `auth="public"`.
* **CSRF Exemption:** Any controller route that explicitly disables CSRF protection (`csrf=False`) MUST physically reside in a Python file ending in `_api.py`.
* **Public Route Anti-Spam:** All unauthenticated `POST` routes MUST implement anti-spam measures (reCAPTCHA or honeypot fields) to prevent malicious bot automation.
* **Standard Template Context:** When rendering built-in Odoo templates, you MUST verify the template's source code and ensure all expected QWeb context variables are injected into the rendering dictionary to prevent `KeyError` crashes.
* **Explicit Parameter Binding:** When defining HTTP controller methods, you **MUST** explicitly declare expected form inputs and query parameters in the method signature rather than relying solely on `kwargs.get()` or `request.params`.
* **HTTP Exception Handling:** Controllers MUST raise `werkzeug.exceptions.Forbidden()` or `werkzeug.exceptions.NotFound()` for access denials or missing records. You MUST NOT raise raw ORM exceptions inside controllers.
