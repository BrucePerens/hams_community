# JULES ISSUES - manual_library

## Environment Verification
- **Date:** 2026-05-29
- **Environment:** Jules VM (Ubuntu 24.04)
- **Status:** Provisioned successfully.
- **Test Execution:** Standard and UI tours are functional.

## Issues Found

### 1. Test Incompatibility: `test_04_parent_deletion_restriction`
- **Error:** `TypeError: issubclass() arg 1 must be a class`
- **Description:** Odoo 19's `_assertRaises` override in `odoo/tests/common.py` does not correctly handle tuples of exceptions.
- **Resolution:** Modified the test to manually catch and verify the exceptions (`ForeignKeyViolation` or `RestrictViolation`).

### 2. AI Laziness: Empty Exception Handler
- **File:** `manual_library/controllers/main.py`
- **Error:** Empty `except (ValueError, AccessError): pass` block.
- **Resolution:** Added debug logging to satisfy "Burn List" requirements while maintaining security obscurity for the feedback endpoint.

### 3. Multi-Tenant Enhancement
- **Description:** Added `company_id` to `knowledge.article` and updated record rules to ensure strict multi-company isolation, complementing the existing `website_id` isolation.

### 4. Global Regression Blocked by Sibling Linters
- **Description:** Standard `tools/test.py` runner halts on pre-existing linter errors in other modules (e.g., `cloudflare`, `user_websites`). Per directive, sibling modules were NOT modified in the final PR to avoid merge conflicts. Global regression was attempted by running targeted module tests.
