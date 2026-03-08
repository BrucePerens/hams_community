# 🚨 LLM LINTER GUIDE & ANTI-EVASION REFERENCE

*Copyright © Bruce Perens K6BP.*

**Purpose:** This document is the ultimate reference sheet for the platform's DevSecOps pipeline. It exhaustively details every syntax pattern, AST structure, and architectural anti-pattern that the custom linters (`check_burn_list.py`, `verify_anchors.py`) will physically reject.

You MUST consult this guide to understand the *intent* of the rules and format your code to pass the CI/CD pipeline on the first attempt.

**CRITICAL ANTI-EVASION MANDATE:** This document is a blueprint for *architectural alignment and secure design*, NOT a recipe book for bypassing security checks. You are strictly forbidden from using this guide to engineer semantic tricks, obfuscations, or workarounds that evade the AST linters without fixing the underlying architectural flaw. You MUST resolve the root cause of any flagged error by adopting the approved, secure platform idioms described herein.

**DEAD CODE, LOOP, & MOCK EVASION IS BANNED:** You MUST NOT place required method calls (like `send_mail()`, `_trigger()`) inside unreachable execution blocks (e.g., `if False:` or after a `return`, `raise`, `break`, or `continue`) or use empty context managers (e.g., `with self.assertQueryCount(0): pass`) simply to trick the AST parser. Additionally, wrapping assertions (like `get_view` or `url_open`) inside `for` or `while` loops is strictly forbidden. Finally, you MUST NOT mock required functions (via `patch` or `patch.object`); the test must legitimately invoke the targeted logic sequentially and perform genuine functional assertions.

---

## 1. 🛡️ Privilege Escalation & Security (Zero-Sudo)

The AST linter recursively tracks assignments and function calls to block absolute privilege escalation. You MUST use the **Service Account Pattern** (`with_user(svc_uid)`) or the **Public User Idiom**.

* **`sudo()` is Blocked:** Any use of `.sudo()` on recordsets, environments, or intermediate variables is physically blocked.
  * *Exception:* Fetching cryptographic keys (`.sudo().get_param('database.secret')`) is permitted ONLY if tagged with `# burn-ignore-sudo: Tested by [%ANCHOR: example_name]`.
* **Obfuscation is Caught:** The linter tracks `getattr(..., 'sudo')` and intermediate variable assignments (e.g., `AdminEnv = env.sudo()`). Do not attempt to evade the AST.
* **Shell Injection:** `subprocess.run` MUST explicitly use `shell=False` and pass arguments as lists.
* **Code Execution:** `eval()`, `exec()`, `pickle.loads/dumps`, and `yaml.load` are strictly banned. Use `ast.literal_eval()`, `odoo.tools.safe_eval()`, or `json`.
* **Service Account Base Groups:** Internal Service Accounts (`is_service_account=True`) must explicitly be granted `base.group_user` in XML. Without it, they cannot access standard ERP features like `mail.thread` (chatter) or basic employee fields, leading to `AccessError` during proxy execution.
* **Weak Cryptography:** `md5`, `sha1`, and the `random` module are banned for security tokens. Use `hashlib.sha256` and the `secrets` module.

---

## 2. 🗄️ Database & ORM Integrity

The AST linter defends PostgreSQL from lock exhaustion, OOM crashes, and SQL injection.

* **SQL Injection (SQLi) & Dynamic Queries:** You MUST use parameterized queries for data values (`cr.execute("SELECT * FROM table WHERE id = %s", (my_id,))`).
  * The linter recursively traces and physically blocks string concatenation (`+`), `%` formatting, `.format()`, and `f-strings` applied to `cr.execute()`. Formatting strings into intermediate variables before execution will still trigger the ban.
  * **Dynamic Schema Mandate:** If you must dynamically inject identifiers (like column names, table names, or dynamic `WHERE` clauses for SQL Views), you are strictly **FORBIDDEN** from using f-strings. Standard `%s` parameterization does not work for schema identifiers. You MUST use the `psycopg2.sql` module (e.g., `query = sql.SQL("...").format(col=sql.Identifier("..."))`).
* **N+1 Loops:** Calling `.search()`, `.search_count()`, or `.read_group()` inside a `for` loop is banned. You MUST pre-fetch data into memory-mapped dictionaries outside the loop (O(1) lookups).
* **Unbounded Searches:** Calling `.search()` without a `limit=` keyword argument is flagged as a potential Out-Of-Memory (OOM) vector. You MUST paginate or limit bulk searches. If you are tempted to replace a `One2many` relation with an explicit `.search([('parent_id', '=', self.id)])` to fix an empty list during automated testing, **STOP**. That is an ORM test cache anomaly. Use explicit wiring `[(4, id)]` in the test setup instead. If you are tempted to replace a `One2many` relation with an explicit `.search([('parent_id', '=', self.id)])` to fix an empty list during automated testing, **STOP**. That is an ORM test cache anomaly. Use `record.invalidate_recordset()` in the test instead.
* **Cursor Mismanagement:** Using `env.cr.commit()` or `env.cr.rollback()` directly inside a `with registry.cursor():` block breaks psycopg2 state. You MUST use `cr = registry.cursor()` followed by `try/except/finally`.
* **Proxy Ownership Constraints:** When assigning proxy ownership to a dictionary payload in Python, assigning BOTH `owner_user_id` and `user_websites_group_id` simultaneously will trigger an AST trap. They are mutually exclusive.
* **RPC Mass Assignment:** Passing `kwargs` directly into `.create(**kwargs)` or `.write(kwargs)` inside a controller routes is blocked. You MUST explicitly map and whitelist fields into a new dictionary.
* **Non-Deterministic Hashes:** Using Python's native `hash()` is banned because it is salted per-process. You MUST use `env['zero_sudo.security.utils']._get_deterministic_hash(val)`.
* **XML-RPC Kwargs Crash:** Passing a dictionary of kwargs as a positional argument to `client.execute()` for read operations (e.g., `client.execute('model', 'search_read', domain, {'fields': [...]})`) is banned. The underlying XML-RPC wrapper expects keyword arguments natively. You MUST use explicit kwargs (e.g., `fields=[...]`).
* **Cache Purging:** `.clear_caches()` is deprecated in Odoo 19. You MUST use `self.env.registry.clear_cache()` or `self.method_name.clear_cache(self)` for specific `@tools.ormcache` methods.
* **Test Cursor Corruption:** Odoo 19 tests run in a single transaction. Calling `env.cr.commit()` or `env.cr.rollback()` inside a `test_` file will raise an `AssertionError: Cannot commit or rollback a cursor from inside a test`. If testing background loop functions, you MUST conditionally bypass commits using `if not odoo.tools.config.get('test_enable'):`.
* **Controller Caching:** Using `@tools.ormcache` on an `@http.route` controller method is banned because controllers lack the required `pool` attribute.

---

## 3. 🐍 Python Odoo 19 Core Deprecations & Formatting

* **Single Statement Per Line & Short Lines:** You MUST NOT use multiple statements on a single line (no semicolons). You MUST proactively shorten lines by extracting complex logic or deep attributes into intermediate variables. This guarantees that Black will not wrap the line and detach inline linter comments (`# burn-ignore`, `# audit-ignore`) from the AST nodes they apply to.
* **Long String Formatting:** Strings longer than 40 characters MUST NOT be defined inline. Extract them to variables or constants and use multi-line triple-quotes (`"""`) to enforce the 70-character line limit before passing them into methods.
* **Constraints:** `_sql_constraints = [...]` is banned. Use `models.Constraint(...)` class attributes.
* **File Reading:** `get_module_resource` is banned. Use `odoo.tools.file_open`.
* **Security Groups Mapping:** When mapping users to groups in Python dictionaries or XML, you MUST use `group_ids` (for `res.users`) and `user_ids` (for `res.groups`). Legacy `groups_id` and `users` strings are hard-blocked as bias traps.
* **Hierarchy Recursion:** `_check_recursion()` is banned. Use `_has_cycle()`.
* **Field Attributes:** `oldname=...` is banned. `select=True` is banned (use `index=True`).
* **Survey States:** The `state` field on `survey.survey` was completely removed in Odoo 19. You MUST use the native `active` boolean field instead. Do not query `('state', '=', 'open')`.
* **Product Types:** The `detailed_type` field on `product.template` was reverted to `type` in Odoo 19. Do not use `detailed_type`.
* **Trigram Indexes:** `index='trgm'` is banned. Use `index='trigram'`.
* **API Decorators:** `@api.returns` is deprecated and banned.
* **HTTP Routes:** `type='json'` is banned for routes. Use `type='jsonrpc'`.
* **Search Count Parameter:** `search(..., count=True)` is banned. Use `search_count(...)`.
* **Thread Blocking:** `time.sleep()` in main application code is banned. If used in a background daemon for rate-limiting, it MUST be appended with `# audit-ignore-sleep`.
* **Thread Spawning:** `threading.Thread` is banned as a DoS vector. Use `concurrent.futures.ThreadPoolExecutor`.

---

## 4. 🎨 XML, QWeb, and UI Elements

* **XSS Prevention:** `<t t-raw...>` is banned. Use `<t t-out...>`.
* **SSTI Prevention:** Using `request.env` anywhere inside an XML QWeb template is a critical Server-Side Template Injection vector and is banned. Compute values in Python controllers and pass them to the rendering context.
* **Legacy View Tags:** `<tree>` is banned (use `<list>`). `t-name="kanban-box"` is banned (use `t-name="card"`).
* **Deprecated Directives:** `t-esc` is banned. Use `t-out`.
* **Search Views:** `<group expand="0">` and `<group string="...">` are banned. Odoo 19 requires clean group tags.
* **Snippet Options Deprecation:** Inheriting `website.snippet_options` or `web_editor.snippet_options` is highly volatile and leads to `ValueError: External ID not found` in Odoo 19. Do not implement custom snippet option menus.
* **Snippet Anchors:** Targeting `id="snippet_structure"` via XPath is banned as fragile. Target `/*` instead.
* **Fragile Form XPaths:** Targeting `hasclass('field-*')` (e.g., `field-login`, `field-name`) is banned. Odoo 19 refactored frontend authentication templates and removed these wrappers.
* **Label Targeting Banned:** Targeting `//label[@for='...']` is strictly banned. Odoo 19 frequently removes `<label>` elements in favor of placeholders or floating labels. Target the `//input[@name='...']` element directly instead.
* **Button String Targeting Banned:** Targeting `//button[@string='...']` is strictly banned. Visible strings frequently change or are translated. Target the button by its method name (`//button[@name='...']`).
* **Legacy `attrs` Banned:** The `attrs` attribute (e.g., `attrs="{'invisible': ...}"`) was removed in Odoo 17+. Use `invisible`, `readonly`, and `required` directly with Python expressions.
* **Parent Axis Traversals:** Using `..` (e.g., `//input[@name='login']/..`) or complex container predicates (`//div[input[@name='login']]`) is strictly banned. Odoo's XML compiler often fails to resolve these when patching inherited views. You MUST target the specific structural element directly (e.g., `//input[@name='login']`).
* **Security Categories:** Using `name="category_id"` in `<record model="res.groups">` is banned. Use `privilege_id`.
* **Cron Infinity:** Specifying `numbercall` in an `ir.cron` XML record is banned. Odoo 18+ runs crons indefinitely when `active="True"`.

---

## 5. 🖥️ Frontend JavaScript

* **jQuery Ban:** The `$` identifier is banned. You MUST use Vanilla JS or modern OWL components.
* **DOM XSS:** Passing template literals (\`...\`) into `.innerHTML` or `.bindPopup` is flagged. Ensure all dynamic data injected into the DOM is sanitized.
* **Deprecated Services:** `useService('company')` is banned.

---

## 6. 🚥 CI/CD Bypasses & Automated Test Audits (The `ignore` Protocol)

The linter outputs `[AUDIT]` warnings for specific architectural patterns. You MUST silence these by appending specific `audit-ignore` tags, but **ONLY** if you write an automated Python test to mathematically verify the constraint.

The AST parser physically reads your test files to verify the assertions exist.

| Audit Target | Bypass Tag | Required AST Assertion in Test |
| :--- | :--- | :--- |
| `ir.cron` XML | `<!-- audit-ignore-cron: Tested by [%ANCHOR: example_name] -->` | The test MUST execute `_trigger()` to prove batching. |
| `send_mail()` | `# audit-ignore-mail: Tested by [%ANCHOR: example_name]` | The test MUST execute `send_mail` or `message_post`. **CRITICAL TRAP:** The integer `res_id` passed to `send_mail(res_id)` MUST match an existing record of the exact model defined in the template's `model_id`, otherwise Odoo's rendering mixin will crash with a `MissingError`. |
| `.search()` | `# audit-ignore-search: Tested by [%ANCHOR: example_name]` | The test MUST pass `limit=` or utilize `patch.object(self.env.cr, 'execute')` to assert caching behavior. |
| `@tools.ormcache` | N/A (Tested implicitly by logic) | To verify a cache hit, NEVER use `self.assertQueryCount(0)`. Odoo's background GC will cause false positives. You MUST use `with patch.object(self.env.cr, 'execute', wraps=self.env.cr.execute) as mock_execute:` and assert `self.assertNotIn("target_table", query)` in `mock_execute.call_args_list`. |
| Boolean Checks | N/A (Flake8 E712) | NEVER use `== True` or `== False`. You MUST use `is True`, `is False`, or `if cond:`. |
| `<xpath>` | `<!-- audit-ignore-xpath: Tested by [%ANCHOR: example_name] -->` | The test MUST execute `get_view`, `url_open`, or `_get_combined_arch` to prove DOM injection. **Note:** `get_view()` only works on `ir.ui.view` records. For testing structural `<template>` records (QWeb), you MUST use `self.env.ref('...').with_context(lang=None)._get_combined_arch()`. |
| `time.sleep()` | `# audit-ignore-sleep` | (Visual check only; indicates daemon rate-limiting). |
| `ir.ui.view` | `<!-- audit-ignore-view: Tested by [%ANCHOR: example_name] -->` | MUST be placed on the EXACT same line as the `<record>` or `<template>` node. Test MUST execute `get_view` or `url_open`. |
| I18N Strings | `# audit-ignore-i18n: Tested by [%ANCHOR: example_name]` | Safely ignore headless API translations (ADR-0065). |
| Sudo Override | `# burn-ignore-sudo: Tested by [%ANCHOR: example_name]` | Exclusively for `database.secret` extraction. |
| Test Commit | `# burn-ignore-test-commit` | Exclusively for `RealTransactionCase` where real DB commits are required to test ORM caches. |

### 🚨 Critical Formatting & Placement Rules for Bypasses
1. **The Python Formatter (`# fmt: skip`) Trap:** The Black code formatter will wrap long lines (like dictionaries, lists, or long method signatures) and detach your inline linter comments, causing the AST linter to fail. **Whenever you apply an `# audit-ignore-*` or `# burn-ignore` comment to a multi-line structure, you MUST append `  # fmt: skip` to the exact same line.** This mathematically locks the bypass tag to the correct AST node.
2. **The Dual XML Anchor Placement:** To satisfy both the XML architecture linter (`check_burn_list.py`) and the bidirectional traceability linter (`verify_anchors.py`) simultaneously, you MUST use the following dual-comment structure:
   * The traceability anchor `<!-- Verified by [%ANCHOR: test_name] -->` MUST be placed immediately **above** the `<record>` or `<template>` tag.
   * The burn list bypass `<!-- audit-ignore-view: Tested by [%ANCHOR: test_name] -->` MUST be placed immediately **inside** the `<record>` or `<template>` tag (on the exact same line as the opening bracket).

---

## 7. ⚓ Semantic Anchors & UI Tour Mandate

The `verify_anchors.py` script enforces strict documentation traceability:

1. **Bidirectional Verification:** Any execution logic marked with `# Verified by [%ANCHOR: example_name]` MUST possess a corresponding test file containing `# Tests [%ANCHOR: example_name]`. (CRITICAL: The test file anchor MUST be prefixed exactly with `# Tests ` or the CI script will misinterpret it as a source anchor definition and fail).
2. **Documentation Mandate:** Any anchor embedded in source code (excluding tests) MUST be referenced somewhere within the `docs/` folder (Runbooks, Stories, Journeys, or Modules). These documentation references MUST be placed inline, immediately adjacent to the relevant descriptive text, rather than grouped in a standalone list at the end of the document.
3. **The View-Tour Mandate:** Every `<template>` or `<record model="ir.ui.view">` MUST contain a UI Tour link: `<!-- Verified by [%ANCHOR: example_name] -->`.
4. **Tour Validation:** The corresponding JavaScript tour file MUST contain the matching anchor and explicitly utilize the `trigger:` keyword to prove it evaluates the DOM.
5. **Example Anchors (Documentation):** Any anchor name starting with `example_` (e.g., `[%ANCHOR: example_my_feature]`) is automatically ignored by the CI/CD verification linters. You MUST use this prefix when providing anchor examples in markdown documentation to prevent false-positive missing anchor failures.

---

## 8. 🤖 LLM Extraction Defenses & Parcel Features

To protect the codebase from LLM-specific failure modes (like hallucination, laziness, and truncation), the `parcel_extract.py` tool enforces the following automated defenses and operational behaviors.

**Meta-Tooling Exception:** Because the `parcel_extract.py` script powers these defenses, you MUST modify it exclusively using full-file `overwrite` operations. You are forbidden from using `search-and-replace` to patch `parcel_extract.py` to prevent self-referential AST corruption and indentation errors.

* **Anti-Corruption Guard (Laziness Traps):** The extractor actively scans payloads for laziness placeholders. If it detects `# ... rest of`, `// Code unchanged`, or HTML comments containing existing code placeholders, it instantly aborts the file write to prevent deleting valid code.
* **Semantic Token Matchers (Python, XML, Markdown):** The extraction engine uses semantic tokenization for `.py`, `.xml`, and `.md` files. For Python, it ignores non-semantic whitespace, comments, and quote types. For Markdown, it strips punctuation drift and normalizes list/header markers. For XML, it alphabetically sorts attributes and ignores tag whitespace spacing. This immunizes the patch against LLM formatting drift.
* **The Convergence Principle:** Patched Python files are automatically routed through the `black` formatter before saving, ensuring subsequent reads match the LLM's canonical style expectations.
* **Fuzzy & AST Fallbacks:** If token matching fails, the extractor falls back to stripping all whitespace. For Python, it also employs an Abstract Syntax Tree (AST) parser to identify and surgically replace target `FunctionDef` or `ClassDef` nodes by name.
* **Markdown Balance Checking:** For `.md` files, the extractor validates that all fenced and inline code blocks are perfectly balanced. Unclosed blocks will abort the write to prevent rendering corruption.
* **Strict URL-Encoding Mandate for XML Comments:** Web UI Markdown renderers will silently delete HTML/XML comments before the extraction script ever sees them. To prevent this data loss, LLMs MUST use the `Encoding: url-encoded` header in their Parcel block and percent-encode the angle brackets for any comments.
* **Automated Linting Hooks:** The extractor automatically pipes generated files through `flake8` (Python), `xml.etree` (XML), `json.load` (JSON), and the custom `check_burn_list.py` before committing the write, surfacing architectural failures immediately.

---

## 9. 🔒 Security Patterns & Native Idioms (Extended)

You MUST utilize one of the following native Odoo idioms when traversing or limiting boundaries:

* **The "Centralized Security Utility" Pattern:**
  * **Context:** The system needs to retrieve system parameters (`ir.config_parameter`) or resolve XML IDs (`ir.model.data`), which generally require escalated privileges.
  * **Mandate:** Delegate to `zero_sudo.security.utils` via `request.env['zero_sudo.security.utils']._get_system_param(key)` or `_get_service_uid(xml_id)`. The latter employs RAM caching (`@tools.ormcache`) to execute the database lookup securely once per boot cycle.

* **The "Service Account" Pattern (Dedicated Execution Context):**
  * **Context:** The system needs to perform an elevated background task, API token validation, or cryptographic operation triggered by an unauthenticated or under-privileged user.
  * **The Persona Capability Limit:** You MUST NOT use a Service Account simply to bypass read ACLs to display masked/aggregated data to an unprivileged user. For read-only data presentation, you MUST use a PostgreSQL View (`_auto = False`) and grant the user native read access to the View (See ADR-0069).
  * **Mandate:**
      1. Create an isolated `res.groups` with no human members.
      2. Create a dedicated internal `res.users` (the Service Account) belonging *only* to that group.
      3. **Separation of Privilege & Explicit Scoping:** Ensure the account is a *Micro-Service Account* dedicated to a single domain action. Service accounts must be explicitly granted the security groups of the external models they interact with, not just `base.group_user`. Do not bundle disparate permissions or fall back to `base.user_admin`.
      4. Flag the user with `is_service_account="True"` in the XML to permanently block interactive web logins (See ADR-0005).
      5. Grant that specific group the exact ACLs (`ir.model.access.csv`) and Record Rules (`ir.rule`) required for the task.
      6. In the controller or method, fetch the Service Account's ID securely via `env['zero_sudo.security.utils']._get_service_uid('module.user_xml_id')` and execute the logic using `.with_user(svc_uid)`.

* **The "Public Guest User" Idiom:**
  * **Context:** An unauthenticated guest needs to submit data (e.g., a contact form, an issue report).
  * **Mandate:** Define an Access Control List (`ir.model.access.csv`) granting `perm_create=1` to `base.group_public` for that specific model. Rely purely on the database layer to restrict read/write access.

* **The "Impersonation" Idiom (`with_user`):**
  * **Context:** An API webhook or background task identifies a specific user via a token, but the request arrives unauthenticated.
  * **Mandate:** Shift the environment context to the identified user: `request.env['target.model'].with_user(user).create(...)`. This ensures the action is strictly bound by the user's Record Rules.

* **The "Login As" Session Swap Idiom:**
  * **Context:** A System Administrator needs to investigate a user's isolated portal state.
  * **Mandate:** Swap the underlying `request.session.uid` directly in the HTTP controller. This action MUST ALWAYS be preceded by a `message_post` to the target user's chatter log to maintain an immutable audit trail.

* **The "Self-Writeable Fields" Idiom:**
  * **Context:** A user needs to update their own preferences on `res.users`.
  * **Mandate:** Override `SELF_WRITEABLE_FIELDS` (or `_get_writeable_fields` in Odoo 18+) on the `res.users` model to explicitly whitelist the specific preference fields.
