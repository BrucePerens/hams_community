# JULES ISSUES - daemon_key_manager

## AI Hallucinations & Laziness Audit
- **Hollow Assertions**: None found. Assertions in `test_key_registry.py` target actual result variables.
- **Lazy Exception Handling**:
  - `_cron_rotate_all_keys` uses `# audit-ignore-catch-all` for its main loop, which is acceptable for a cron job that must not crash on a single failure, but should be monitored.
  - Tests use `except OSError: pass` for cleanup, which is standard but could be more specific.
- **Missing Methods / hasattr**: No `hasattr` or bypassed method calls detected.

## Multi-Tenant Awareness
- **Finding**: The `daemon.key.registry` model was missing a `company_id` field.
- **Resolution**: Added `company_id` field, updated uniqueness constraint to `(name, company_id)`, added multi-company record rule, and ensured `register_daemon` handles cross-company registration securely.

## Zero-Sudo Compliance
- **Elevation Refactoring**: Replaced all `.sudo()` calls except for the core `res.users.apikeys._generate()` method. This remaining `.sudo()` is necessary to bypass hardcoded 0-day duration limits for service accounts and is explicitly exempted.
- **Micro-Privilege Elevation**: Used `with_user(odoo_facility_service_internal)` for all administrative escalations (e.g., searching for users, unlinking keys).
- **ACL Hardening**: Added explicit `res.users.apikeys` access for `group_daemon_key_manager` in `ir.model.access.csv`.

## Proposed Linter Rules (for `check_burn_list.py`)
1.  **Strict Sudo Verification**: A rule to flag any `.sudo()` call that doesn't have a mandatory `# burn-ignore-sudo` comment AND a detailed justification for why `with_user()` cannot be used.
2.  **Multi-Company Constraint Check**: A rule to verify that any model with a `company_id` field also has a corresponding multi-company record rule in `security/*.xml` and that all `UNIQUE` constraints include `company_id`.
3.  **API Key Allocation Audit**: A rule to ensure `res.users.apikeys._generate` is ONLY called within the `daemon_key_manager` module or by the `odoo_facility_service_internal` user.

## Environment Verification
- Environment successfully provisioned.
- All tests pass (including new multi-company tests).
- UI tour passes with `debug=1`.
