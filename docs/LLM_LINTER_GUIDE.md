# 🚨 LLM LINTER GUIDE & ANTI-EVASION REFERENCE

*Copyright © Bruce Perens K6BP.*

**Purpose:** This document is the ultimate reference sheet for the Hams.com DevSecOps pipeline. It exhaustively details every syntax pattern, AST structure, and architectural anti-pattern that the custom linters (`check_burn_list.py`, `verify_anchors.py`) will physically reject. 

You MUST consult this guide to understand the *intent* of the rules and format your code to pass the CI/CD pipeline on the first attempt.

**CRITICAL ANTI-EVASION MANDATE:** This document is a blueprint for *architectural alignment and secure design*, NOT a recipe book for bypassing security checks. You are strictly forbidden from using this guide to engineer semantic tricks, obfuscations, or workarounds that evade the AST linters without fixing the underlying architectural flaw. You MUST resolve the root cause of any flagged error by adopting the approved, secure platform idioms described herein.

---

## 1. 🛡️ Privilege Escalation & Security (Zero-Sudo)

The AST linter recursively tracks assignments and function calls to block absolute privilege escalation. You MUST use the **Service Account Pattern** (`with_user(svc_uid)`) or the **Public User Idiom**.

* **`sudo()` is Blocked:** Any use of `.sudo()` on recordsets, environments, or intermediate variables is physically blocked. 
  * *Exception:* Fetching cryptographic keys (`.sudo().get_param('database.secret')`) or GDPR hard-deletes (`.sudo().unlink()`) are permitted ONLY if tagged with `# burn-ignore-sudo: Tested by [%ANCHOR: example_name]`.
* **Obfuscation is Caught:** The linter tracks `getattr(..., 'sudo')` and intermediate variable assignments (e.g., `AdminEnv = env.sudo()`). Do not attempt to evade the AST.
* **Shell Injection:** `subprocess.run` MUST explicitly use `shell=False` and pass arguments as lists.
* **Code Execution:** `eval()`, `exec()`, `pickle.loads/dumps`, and `yaml.load` are strictly banned. Use `ast.literal_eval()`, `odoo.tools.safe_eval()`, or `json`.
* **Weak Cryptography:** `md5`, `sha1`, and the `random` module are banned for security tokens. Use `hashlib.sha256` and the `secrets` module.

---

## 2. 🗄️ Database & ORM Integrity

The AST linter defends PostgreSQL from lock exhaustion, OOM crashes, and SQL injection.

* **SQL Injection (SQLi):** You MUST use parameterized queries (`cr.execute("SELECT * FROM table WHERE id = %s", (my_id,))`). The linter recursively traces string concatenation (`+`), `%` formatting, `.format()`, and `f-strings` applied to `cr.execute()`. Formatting strings into variables before execution will still trigger the ban.
* **N+1 Loops:** Calling `.search()`, `.search_count()`, or `.read_group()` inside a `for` loop is banned. You MUST pre-fetch data into memory-mapped dictionaries outside the loop (O(1) lookups).
* **Unbounded Searches:** Calling `.search()` without a `limit=` keyword argument is flagged as a potential Out-Of-Memory (OOM) vector. You MUST paginate or limit bulk searches.
* **Cursor Mismanagement:** Using `env.cr.commit()` or `env.cr.rollback()` directly inside a `with registry.cursor():` block breaks psycopg2 state. You MUST use `cr = registry.cursor()` followed by `try/except/finally`.
* **Proxy Ownership Constraints:** When assigning proxy ownership to a dictionary payload in Python, assigning BOTH `owner_user_id` and `user_websites_group_id` simultaneously will trigger an AST trap. They are mutually exclusive.
* **RPC Mass Assignment:** Passing `kwargs` directly into `.create(**kwargs)` or `.write(kwargs)` inside a controller routes is blocked. You MUST explicitly map and whitelist fields into a new dictionary.
* **Non-Deterministic Hashes:** Using Python's native `hash()` is banned because it is salted per-process. You MUST use `env['zero_sudo.security.utils']._get_deterministic_hash(val)`.
* **Cache Purging:** `.clear_caches()` is deprecated in Odoo 19. You MUST use `self.env.registry.clear_cache()`.
* **Controller Caching:** Using `@tools.ormcache` on an `@http.route` controller method is banned because controllers lack the required `pool` attribute.

---

## 3. 🐍 Python Odoo 19 Core Deprecations

* **Constraints:** `_sql_constraints = [...]` is banned. Use `models.Constraint(...)` class attributes.
* **File Reading:** `get_module_resource` is banned. Use `odoo.tools.file_open`.
* **Security Groups Mapping:** When mapping users to groups in Python dictionaries or XML, you MUST use `group_ids` (for `res.users`) and `user_ids` (for `res.groups`). Legacy `groups_id` and `users` strings are hard-blocked as bias traps.
* **Hierarchy Recursion:** `_check_recursion()` is banned. Use `_has_cycle()`.
* **Field Attributes:** `oldname=...` is banned. `select=True` is banned (use `index=True`).
* **Trigram Indexes:** `index='trgm'` is banned. Use `index='trigram'`.
* **API Decorators:** `@api.returns` is deprecated and banned.
* **HTTP Routes:** `type='json'` is banned for routes. Use `type='jsonrpc'`.
* **Thread Blocking:** `time.sleep()` in main application code is banned. If used in a background daemon for rate-limiting, it MUST be appended with `# audit-ignore-sleep`.
* **Thread Spawning:** `threading.Thread` is banned as a DoS vector. Use `concurrent.futures.ThreadPoolExecutor`.

---

## 4. 🎨 XML, QWeb, and UI Elements

* **XSS Prevention:** `<t t-raw="...">` is banned. Use `<t t-out="...">`.
* **SSTI Prevention:** Using `request.env` anywhere inside an XML QWeb template is a critical Server-Side Template Injection vector and is banned. Compute values in Python controllers and pass them to the rendering context.
* **Legacy View Tags:** `<tree>` is banned (use `<list>`). `t-name="kanban-box"` is banned (use `t-name="card"`).
* **Deprecated Directives:** `t-esc` is banned. Use `t-out`.
* **Search Views:** `<group expand="0">` and `<group string="...">` are banned. Odoo 19 requires clean group tags.
* **Snippet Anchors:** Targeting `id="snippet_structure"` via XPath is banned as fragile. Target `/*` instead.
* **Security Categories:** Using `name="category_id"` in `<record model="res.groups">` is banned. Use `privilege_id`.
* **Cron Infinity:** Specifying `numbercall` in an `ir.cron` XML record is banned. Odoo 18+ runs crons indefinitely when `active="True"`.

---

## 5. 🖥️ Frontend JavaScript

* **jQuery Ban:** The `$` identifier is banned. You MUST use Vanilla JS or modern OWL components.
* **DOM XSS:** Passing template literals (`\`...\``) into `.innerHTML` or `.bindPopup` is flagged. Ensure all dynamic data injected into the DOM is sanitized.
* **Deprecated Services:** `useService('company')` is banned.

---

## 6. 🚥 CI/CD Bypasses & Automated Test Audits (The `ignore` Protocol)

The linter outputs `[AUDIT]` warnings for specific architectural patterns. You MUST silence these by appending specific `audit-ignore` tags, but **ONLY** if you write an automated Python test to mathematically verify the constraint.

The AST parser physically reads your test files to verify the assertions exist.

| Audit Target | Bypass Tag | Required AST Assertion in Test |
| :--- | :--- | :--- |
| `ir.cron` XML | `` | The test MUST execute `_trigger()` to prove batching. |
| `send_mail()` | `# audit-ignore-mail: Tested by [%ANCHOR: example_name]` | The test MUST execute `send_mail` or `message_post`. |
| `.search()` | `# audit-ignore-search: Tested by [%ANCHOR: example_name]` | The test MUST utilize `with self.assertQueryCount()` or pass `limit=`. |
| `<xpath>` | `` | The test MUST execute `get_view`, `url_open`, or `_get_combined_arch` to prove DOM injection. |
| `time.sleep()` | `# audit-ignore-sleep` | (Visual check only; indicates daemon rate-limiting). |
| `ir.ui.view` | `` | (Alternative to JS Tours). Test MUST execute `get_view` or `url_open`. |
| Sudo Override | `# burn-ignore-sudo: Tested by [%ANCHOR: example_name]` | Exclusively for `database.secret` extraction and GDPR `unlink()` cascades. |

---

## 7. ⚓ Semantic Anchors & UI Tour Mandate

The `verify_anchors.py` script enforces strict documentation traceability:

1. **Bidirectional Verification:** Any execution logic marked with `# Verified by [%ANCHOR: example_name]` MUST possess a corresponding test file containing `# Tests [%ANCHOR: example_name]`. 
2. **Documentation Mandate:** Any anchor embedded in source code (excluding tests) MUST be referenced somewhere within the `docs/` folder (Runbooks, Stories, Journeys, or Modules).
3. **The View-Tour Mandate:** Every `<template>` or `<record model="ir.ui.view">` MUST contain a UI Tour link: ``. 
4. **Tour Validation:** The corresponding JavaScript tour file MUST contain the matching anchor and explicitly utilize the `trigger:` keyword to prove it evaluates the DOM.

---

## 8. 🤖 LLM Extraction & Runner Defenses

To protect the codebase from LLM-specific failure modes (like hallucination, laziness, and truncation), the infrastructure tools (`aef_extract.py` and `gemini_runner.py`) enforce the following automated defenses:

* **Anti-Corruption Guard (`aef_extract.py`):** The extractor actively scans replacement blocks for LLM "laziness" placeholders (e.g., `// ...`, `# ... rest of method`, `[Code unchanged]`). If an LLM hallucinates a truncation placeholder instead of writing the full required code block, the extractor immediately aborts the file patch to prevent deleting existing valid code.
* **Fuzzy Fallbacks (`aef_extract.py`):** If search blocks fail to match due to LLM indentation drift or whitespace hallucinations, the extractor employs flexible whitespace fallbacks and sequence matchers to safely identify the target code and apply the patch.
* **Automated Self-Correction Loop (`gemini_runner.py`):** If the JSON extraction fails or the Anti-Corruption Guard trips, the runner catches the stdout/stderr stack trace and automatically feeds it back to the LLM as a new prompt. This forces the LLM to analyze its own formatting failure and regenerate a syntactically whole, compliant patch without human intervention.
