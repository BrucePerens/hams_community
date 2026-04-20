# 🧪 Real Transaction Testing Facility (`test_real_transaction`)

*Copyright © Bruce Perens K6BP. AGPL-3.0.*

**Context:** Technical documentation strictly for LLMs and Integrators.

## 1. Overview
Provides the `RealTransactionCase` class.
**Inheritance & Capabilities:** It inherits from Odoo's `HttpCase`, meaning it inherently supports full HTTP controller testing utilities like `self.authenticate()`, `self.url_open()`, and `self.make_jsonrpc_request()`.
It completely bypasses Odoo's test cursor wrapping, allowing tests to perform actual `env.cr.commit()` operations to correctly test cross-worker caches and daemons.

## 2. Features
* **Auto-Cleanup:** Instruments `BaseModel.create()` ([@ANCHOR: orm_instrumentation]) to track created records and unlinks them across multiple cascade passes in `tearDown()` ([@ANCHOR: automated_cleanup]).
* **Leak Detection:** Takes a SQL snapshot of all tables before ([@ANCHOR: leak_snapshotting]) and after the test ([@ANCHOR: leak_verification]) to guarantee pristine state.
* **Open Source Documentation:** Automatically installs documentation ([@ANCHOR: documentation_injection]) if either `manual_library` or Odoo's native `knowledge` module is present, triggered via a registry hook ([@ANCHOR: documentation_bootstrap]).
* **Cursor Management:** Bypasses test wrapping via cursor hijacking ([@ANCHOR: cursor_hijacking]).

## 3. Usage & Import Path
To use this facility, you MUST import it using the exact following path:
`from odoo.addons.test_real_transaction.tests.real_transaction import RealTransactionCase`
Do not assume the class is in a file named `test_real_transaction.py` or inside `ham_testing`.

## 4. Dependencies
* **Hard:** `base`, `zero_sudo`.
* **Soft:** `manual_library` or `knowledge` (for documentation).
