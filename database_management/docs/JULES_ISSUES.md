# Jules Issues for database_management

## Provisioning Issues
- **Python Version Conflict**: Running `python3 tools/test.py --provision-jules` from the default environment (which might be a `.venv` or a pyenv-managed version like 3.12.13) fails to find system-level PostgreSQL binaries like `initdb`.
- **Solution**: As noted in `docs/TESTING_IN_JULES.md`, the system-installed Python (`/usr/bin/python3`) must be used: `IN_JULES_VM=1 /usr/bin/python3 tools/test.py --provision-jules`.

## Testing Issues (Standard Mode)
- **Chrome Initialization Flake**: `TestDatabaseTours.test_db_bloat_tour` occasionally fails to start Chrome (`Failed to detect chrome devtools port after 10.0s`).
    - This appears to be a transient environment issue as the subsequent tour (`test_db_slow_query_tour`) succeeded in the same run.
    - Errors in logs indicate D-Bus connection failures: `Failed to connect to the bus: Address does not contain a colon`.
- **Vacuum Permission Warnings**: `TestDatabaseManagement.test_01b_vacuum_analyze_failures` produces expected warnings: `Vacuum failed for res_users: Permission denied`. This is likely intentional as it's a "failure" test case.
- **Overall Result**: All 17 standard tests eventually passed or were skipped due to the Chrome initialization issue. The test runner reported "1 test failure(s) detected" but Odoo's internal summary showed "0 failed, 0 error(s)".
