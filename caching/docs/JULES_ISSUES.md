# Jules Environment Issues - Caching Module

## 2026-05-19 23:33:00 - Initial Environmental Blockers

### PostgreSQL Permission Denied & Connectivity Failure
While attempting to run tests using `tools/test_runner.py --provision-jules`, the following errors occurred:
- `pg_ctl: could not open PID file "/opt/hams/pgdata/postmaster.pid": Permission denied`
- `createdb: error: connection to server on socket "/opt/hams/pgsock/.s.PGSQL.5432" failed: No such file or directory`

**Resolution**: I identified a bug in `tools/test_runner.py` where `PGHOST` was not being correctly set for the `createdb` and `pg_restore` commands when running in the Jules VM environment (`HAMS_ISOLATED_NS=1`). I patched the test runner to explicitly use `/opt/hams/pgsock` for these operations. This fixed the connectivity issue and allowed tests to execute.

## 2026-05-20 02:20:00 - Remaining Hurdles

### 1. Website Context in HttpCase Tests
The test `test_02_force_invalidation` fails because the change to `caching_invalidation_version` on the `website` model is not reflected in the response from `/sw.js`.
- **Symptom**: The Service Worker always returns `-v1` instead of updating to `-v2` after the invalidation action is called.
- **Hypothesis**: In the `HttpCase` environment, `request.website` may not be resolving correctly to the same website record modified in the test, or the ORM cache is not being correctly invalidated across the test's transaction and the controller's request handling.

### 2. Chrome Headless Sandbox/DBus Errors
UI Tours (like `test_caching_service_worker_tour`) are being skipped because Chrome headless fails to start within the Jules VM.
- **Error**: `Failed to connect to the bus: Could not parse server address: Unknown address type`
- **Context**: This appears to be a systemic issue with the Chrome/Chromium installation or environment configuration in this specific VM image, involving DBus connectivity and sandbox restrictions.

## Summary of PR Scope
- Refactored `caching` module for Multi-Website support.
- Implemented Zero-Sudo architecture enhancements.
- Updated `tools/test_runner.py` to fix PostgreSQL connectivity in Jules VM.
- Improved documentation for both developers and users.
