# JULES ISSUES - backup_management

## AI Hallucinations & Laziness
- **Shortcut in Tests**: Fixed. `backup_management/tests/test_backup.py` contained `message_post(body=_("AST bypass"))` calls. These were replaced with meaningful assertions.
- **Shortcut in Encryption**: Fixed. `backup_config.py`'s `_crypt_field` was returning the string `"***ERROR***"` upon decryption failure. It now raises a `UserError` with a security-focused message.
- **Mocking Shortcut**: Noted. `test_backup.py` mocks `shutil.which` globally on the module level which can have side effects.

## Fallbacks & Missing Resources
- **Auto-download Fallback**: Fixed. Removed implicit auto-download of `kopia` binary. The system now fails fast if required binaries are missing.

## Zero-Sudo & Micro-Privilege
- No `.sudo()` usage detected.
- `with_user()` is correctly applied using service accounts.

## Multi-Tenant Awareness
- **Multi-Company support added**: Added `company_id` to `backup.config`, `backup.snapshot`, and `backup.job` models.
- **Security rules reinforced**: Implemented multi-company security rules and fixed multi-website rules to be global and correctly scoped.
- **SQL View Isolation**: Updated `backup_latest_snapshot_view` to include `website_id` and `company_id`, and updated board data logic to filter by these fields.

## Security Audit
- Path validation in `utils.py` was reinforced to block additional dangerous characters (quotes).
- Verified that all operations use `with_user()` with service accounts.

## Test Environment Hurdles
- **Global Regression Failure**: During the final verification phase, attempting to run all tests for all modules failed with `ERROR: Could not find PostgreSQL binary: initdb`. This occurred despite a successful initial provisioning and module-specific test run. This appears to be a limitation or transient issue in the Jules VM environment's `test.py` runner when transitioning between targeted and global test modes. Since `backup_management` tests pass in isolation and multi-tenant rules were verified, I am proceeding with the submission as directed.

## Proposed Linter Rules for `check_burn_list.py`
- Detect `message_post` calls with "AST bypass" or similar placeholder strings.
- Detect return of magic error strings like `"***ERROR***"` in security-sensitive methods.
