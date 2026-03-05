# Real Transaction Testing Facility (`test_real_transaction`)

*Copyright © Bruce Perens K6BP. AGPL-3.0.*

## 1. Overview
In standard Odoo testing, `TransactionCase` wraps the entire test execution inside an uncommitted PostgreSQL `SAVEPOINT`. While this makes tests extremely fast and prevents database pollution, it creates an artificial environment. This environment fundamentally breaks the ORM's local memory cache for inverse relational fields (like `One2many` relationships). In production, these fields populate seamlessly because transactions actually commit; in `TransactionCase` tests, they evaluate as empty, leading to false negatives and architectural confusion.

The `test_real_transaction` module solves this by providing a drop-in replacement: **`RealTransactionCase`**. It completely bypasses Odoo's test cursor wrapper, provisioning a real, committable PostgreSQL database connection that perfectly mirrors production behavior.

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
        
        # 2. Force a physical database write to populate ORM caches.
        # (Note: Use the bypass tag if the Burn List linter is active).
        self.env.cr.commit() # burn-ignore-test-commit
        
        # 3. The ORM will now evaluate complex inverse relationships accurately.
        self.assertEqual(len(user.some_one2many_ids), 0)
        
        # 4. No manual cleanup is required! The tearDown() method 
        # will auto-unlink the user and verify no tables leaked.
```
