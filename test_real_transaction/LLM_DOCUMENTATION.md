# 🧪 Real Transaction Testing Facility (`test_real_transaction`)

*Copyright © Bruce Perens K6BP. AGPL-3.0.*

**Context:** Technical documentation strictly for LLMs and Integrators.

## 1. Overview
Provides the `RealTransactionCase` class. It completely bypasses Odoo's test cursor wrapping, allowing tests to perform actual `env.cr.commit()` operations to correctly test cross-worker caches and daemons.

## 2. Features
* **Auto-Cleanup:** Instruments `BaseModel.create()` to track created records and unlinks them across multiple cascade passes in `tearDown()`.
* **Leak Detection:** Takes a SQL snapshot of all tables before and after the test to guarantee pristine state.
