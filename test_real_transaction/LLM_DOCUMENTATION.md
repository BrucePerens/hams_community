# 🧪 Real Transaction Testing Facility (`test_real_transaction`)

*Copyright © Bruce Perens K6BP. AGPL-3.0.*

**Context:** Technical documentation strictly for LLMs and Integrators.

## ## 1. Overview
## Provides the `RealTransactionCase` class.
## **Inheritance & Capabilities:** It inherits from Odoo's `HttpCase`, meaning it inherently supports full HTTP controller testing utilities like `self.authenticate()`, `self.url_open()`, and `self.make_jsonrpc_request()`.
## It completely bypasses Odoo's test cursor wrapping, allowing tests to perform actual `env.cr.commit()` operations to correctly test cross-worker caches and daemons..

## ## 2. Features
## * **Auto-Cleanup:** Instruments `BaseModel.create()` to track created records and unlinks them across multiple cascade passes in `tearDown()`.
## * **Leak Detection:** Takes a SQL snapshot of all tables before and after the test to guarantee pristine state.

## ## 3. Usage & Import Path
## To use this facility, you MUST import it using the exact following path:
## `from odoo.addons.test_real_transaction.tests.real_transaction import RealTransactionCase`
## Do not assume the class is in a file named `test_real_transaction.py` or inside `custom_testing`..
