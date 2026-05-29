
## Environment Issues

- **Timestamp:** 2026-05-29 20:13:40 UTC
- **Issue:** UI tours cannot be executed because the `websocket-client` Python module is missing in the Jules VM environment.
- **Impact:** `TestZeroSudoViews.test_02_zero_sudo_tour` is skipped.
- **Traceback/Logs:**
  ```
  2026-05-29 20:13:37,435 WARNING zero_sudo odoo.addons.zero_sudo.tests.test_views.TestZeroSudoViews.test_02_zero_sudo_tour: websocket-client module is not installed
  2026-05-29 20:13:37,435 WARNING zero_sudo odoo.addons.zero_sudo.tests.common: TRACING: Chrome init failed on attempt 1 (websocket-client module is not installed). Retrying...
  ```

## AI Hallucinations & Laziness Repairs

- **File:** `zero_sudo/models/ir_module_module.py`
  - **Issue:** Defensive `hasattr` check on `self.env.registry` used to mask the initialization state of documentation bootstrapping.
  - **Fix:** Replaced with a more robust initialization flag check using `getattr`.
- **File:** `zero_sudo/tests/common.py`
  - **Issue:** Empty `except OSError: pass` blocks in Chrome browser management logic.
  - **Fix:** Added debug logging to track why process termination might fail.

## Proposed Linter Rules for `check_burn_list.py`

- **Rule:** `BAN_EMPTY_EXCEPT_OSError`: Detect and block `except OSError: pass` patterns, especially in test cleanup code.
- **Rule:** `MANDATE_CONSTRAINT_OBJECTS`: Disallow the use of `_sql_constraints` list in favor of `models.Constraint` objects to ensure Odoo 19 architectural compliance.

## Global Regression Hurdles

- **Issue:** Pre-existing linter violations in modules `cloudflare`, `user_websites`, `backup_management`, `daemon_key_manager`, `hams_helpdesk`, `binary_downloader`, and `manual_library` prevent the completion of a clean global test run.
- **Action:** Documented the failures. My changes to `zero_sudo` have been verified in isolation and do not contribute to these violations.
