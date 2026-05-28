# Jules VM Testing Issues - manual_library

## Test Execution Failure

**Date:** 2026-05-28
**Command:** `IN_JULES_VM=1 python3 tools/test.py -u manual_library --already-provisioned`

### Issue: Circular Dependency / Recursion Error
The test runner failed during the database initialization phase with a recursion error in module dependencies.

**Error Log Snippet:**
```
2026-05-28 18:39:51,964 22316 ERROR hams_test odoo.registry: Failed to load registry
2026-05-28 18:39:51,965 22316 CRITICAL hams_test odoo.service.server: Failed to initialize database `hams_test`.
Traceback (most recent call last):
...
  File "/usr/lib/python3/dist-packages/odoo/addons/base/models/ir_module.py", line 379, in _state_update
    raise UserError(_('Recursion error in modules dependencies!'))
odoo.exceptions.UserError: Recursion error in modules dependencies!
```

### Analysis
The `manual_library` module depends on both `zero_sudo` and `hams_test`.
A check of the manifests reveals a circular dependency between the prerequisite modules:
- `hams_test` depends on `zero_sudo`
- `zero_sudo` depends on `hams_test`

This circularity prevents the Odoo registry from loading when attempting to run tests for `manual_library`.
