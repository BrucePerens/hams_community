# Real Transaction Testing Facility (`test_real_transaction`)

*Copyright © Bruce Perens K6BP. Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).*

## 1. Overview
In standard Odoo testing, `TransactionCase` wraps the entire test execution inside an uncommitted PostgreSQL `SAVEPOINT`. While this makes tests extremely fast and prevents database pollution, it creates an artificial environment. This environment fundamentally breaks the ORM's local memory cache for inverse relational fields (like `One2many` relationships). In production, these fields populate seamlessly because transactions actually commit; in `TransactionCase` tests, they evaluate as empty, leading to false negatives and architectural confusion.

The `test_real_transaction` module solves this by providing a drop-in replacement: **`RealTransactionCase`**.
**Because it inherits from Odoo's `HttpCase`, it natively supports full Werkzeug HTTP routing and testing utilities like `self.authenticate()` and `self.make_jsonrpc_request()`.**
It completely bypasses Odoo's test cursor wrapper, provisioning a real, committable PostgreSQL database connection that perfectly mirrors production behavior..

## 2. Key Features

### True Database Commits
You can safely call `self.env.cr.commit()` in your tests. This allows developers to write accurate tests for cross-worker cache invalidations (e.g., Redis pub/sub buses), background daemon polling, and lazy-loaded ORM relations.

### Automated ORM Tracking & Cleanup
Because real commits permanently write to the database, leaving test data behind would severely pollute the environment. To prevent this, the facility dynamically instruments Odoo's `BaseModel.create()` during the `setUp()` phase. It tracks the ID of every record created via the ORM. During `tearDown()`, it automatically executes a hard-delete (`unlink()`) on all tracked records. It performs multiple cascade passes to handle complex foreign-key constraints gracefully.

### SQL Leak Detection (The Safety Net)
To guarantee a pristine database, the facility takes a mathematical snapshot of the exact row count of every table in the `public` PostgreSQL schema before the test begins. During `tearDown()`, after the auto-cleanup completes, it recounts the tables. If your test leaked data (for example, by utilizing raw `cr.execute("INSERT...")` which bypasses the ORM tracker), the test will immediately crash with an `AssertionError` identifying the exact tables that were polluted.

## 3. Usage Guide

To use the facility, simply import `RealTransactionCase` and inherit from it instead of the standard `TransactionCase`. You do not need to write any manual cleanup code for standard ORM creations.

```python
from odoo.tests.common import tagged
from odoo.addons.test_real_transaction.tests.real_transaction import RealTransactionCase

@tagged('post_install', '-at_install')
class MyAdvancedTest(RealTransactionCase):
    def test_01_real_commit_behavior(self):
        # 1. Create a record normally. The facility secretly tracks its ID.
        user = self.env['res.users'].create({'name': 'Test User'})

        # # 2. Force a physical database write to populate ORM caches.
        # self.env.cr.commit()

        # # 3. The ORM will now evaluate complex inverse relationships accurately..
        self.assertEqual(len(user.some_one2many_ids), 0)

        # 4. No manual cleanup is required! The tearDown() method
        # will auto-unlink the user and verify no tables leaked.
```

---

# Technical Documentation

<system_role>
**Context:** Technical documentation strictly for LLMs and Integrators.

This module provides the `RealTransactionCase` class, a specialized testing facility designed for features requiring actual database commits, such as cross-worker cache flushes, background daemons, or complex SQL integrations.
</system_role>

---

<usage_instructions>
## 🚨 USAGE INSTRUCTIONS

To use this facility in your tests, you **MUST** import it using the following path:

```python
from odoo.addons.test_real_transaction.tests.real_transaction import RealTransactionCase
```

**CRITICAL:** Do not assume the class is in a file named `test_real_transaction.py`.
</usage_instructions>

---

<core_features>
## 1. The Real Transaction Mechanism

Unlike standard Odoo `TransactionCase` or `HttpCase`, which wrap tests in a SAVEPOINT that is always rolled back, `RealTransactionCase` provides a real, committable PostgreSQL connection.

* **Cursor Hijacking:** It replaces Odoo's standard test cursor with a real connection [\@ANCHOR: cursor_hijacking], allowing the use of `self.env.cr.commit()`. This logic is verified by [\@ANCHOR: test_cursor_hijacking].
* **ORM Instrumentation:** It instruments `BaseModel.create()` [\@ANCHOR: orm_instrumentation] to track all records created during the test. This behavior is covered by [\@ANCHOR: test_orm_instrumentation].
* **Automated Cleanup:** In `tearDown()`, it performs a multi-pass cleanup [\@ANCHOR: automated_cleanup] to delete tracked records, handling foreign key constraints. Verified by [\@ANCHOR: test_automated_cleanup].
</core_features>

---

<leak_detection>
## 2. SQL Leak Detection

To ensure database integrity, the facility monitors for any data that might have been "leaked" via raw SQL or failed ORM cleanups.

* **State Snapshotting:** Takes a mathematical snapshot of all table row counts before the test [\@ANCHOR: leak_snapshotting]. Verified by [\@ANCHOR: test_leak_snapshotting].
* **Leak Verification:** Compares the final database state against the initial snapshot [\@ANCHOR: leak_verification]. Verified by [\@ANCHOR: test_leak_verification].
* **Noisy Tables:** Allows certain system tables (e.g., `ir_logging`, `bus_bus`) and user-defined tables to be ignored during verification. The management interface ([\@ANCHOR: UX_NOISY_TABLE_MANAGEMENT]) is verified by a UI tour ([\@ANCHOR: test_noisy_table_tour]).
</leak_detection>

---

<documentation_bootstrap>
## 3. Soft-Dependency Documentation

The module automatically installs its own documentation if a compatible documentation engine is found.

* **Bootstrap Trigger:** Uses `_register_hook` [\@ANCHOR: documentation_bootstrap] to wait until the registry is fully loaded. Verified by [\@ANCHOR: test_documentation_bootstrap].
* **Documentation Injection:** Dynamically detects `knowledge.article` or `manual.article` and injects the guide [\@ANCHOR: documentation_injection]. Verified by [\@ANCHOR: test_documentation_injection].
</documentation_bootstrap>

---

<stories_and_journeys>
## 4. Architectural Stories & Journeys

For detailed narratives and end-to-end workflows, refer to the following:

### Stories
* [Real Transaction Testing](test_real_transaction/docs/stories/real_transaction_testing.md)
* [Documentation Injection](test_real_transaction/docs/stories/documentation_injection.md)

### Journeys
* [Developer Testing Flow](test_real_transaction/docs/journeys/developer_testing_flow.md)
* [Documentation Setup Flow](test_real_transaction/docs/journeys/documentation_setup_flow.md)
</stories_and_journeys>
