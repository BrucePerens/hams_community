# 🧪 Real Transaction Testing Facility (`test_real_transaction`)

*Copyright © Bruce Perens K6BP. AGPL-3.0.*

**Context:** Technical documentation strictly for LLMs and Integrators.

## 1. Overview
Provides the `RealTransactionCase` class.

**Inheritance & Capabilities:** It inherits from Odoo's `HttpCase`, meaning it inherently supports full HTTP controller testing utilities like `self.authenticate()`, `self.url_open()`, and `self.make_jsonrpc_request()`.
It completely bypasses Odoo's test cursor wrapping, allowing tests to perform actual `self.env.cr.commit()` operations to correctly test cross-worker caches, background daemons, and Redis pub/sub integrations without relying on mocks.

## 2. Features
* **Auto-Cleanup:** Instruments `BaseModel.create()` to track created records and unlinks them across multiple cascade passes in `tearDown()`. You do not need to manually delete ORM records.
* **Leak Detection:** Takes a SQL snapshot of all tables before and after the test to guarantee a pristine state. If you use raw SQL `INSERT` statements, you MUST manually delete them, or the leak detector will crash the test.

## 3. Usage & Integration Mandates

**A. Manifest Dependency**
If you use this class, you MUST add `test_real_transaction` to your module's `__manifest__.py` `depends` array, or the import will fail during CI/CD.

**B. Import Path**
You MUST import it using the exact following path:
`from odoo.addons.test_real_transaction.tests.real_transaction import RealTransactionCase`

**C. The Linter Trap (No Burn-Ignore)**
The AST linter is natively aware of this class. You are strictly FORBIDDEN from using the legacy `# burn-ignore-test-commit` tag when calling `self.env.cr.commit()`. Using that tag will trigger an UNAUTHORIZED BYPASS build failure.

## 4. Code Example

```python
from odoo.tests.common import tagged
from odoo.addons.test_real_transaction.tests.real_transaction import RealTransactionCase

@tagged('post_install', '-at_install')
class MyAdvancedTest(RealTransactionCase):

    def test_01_real_commit_behavior(self):
        # 1. Create a record normally. The facility secretly tracks its ID for auto-cleanup.
        user = self.env['res.users'].create({'name': 'Test User'})

        # 2. Force a physical database write to populate ORM caches and trigger daemons.
        # DO NOT append # burn-ignore-test-commit here.
        self.env.cr.commit()

        # 3. Perform assertions (e.g., check if a Redis daemon picked up the commit)
        self.assertTrue(user.exists())
```
