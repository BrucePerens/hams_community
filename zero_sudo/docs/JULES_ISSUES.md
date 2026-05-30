# JULES ISSUES - zero_sudo

## Environment Verification

- **Timestamp:** 2026-05-30 18:00:00 UTC
- **Status:** Provisioned and Verified.
- **Details:** The Jules environment was successfully provisioned using `--provision-jules`. All standard tests and UI tours for the `zero_sudo` module completed successfully. Headless Chrome and dependencies are functioning as expected.

## AI Hallucinations & Laziness Repairs

- **File:** `zero_sudo/models/security_utils.py`
  - **Issue:** The `_ensure_executable` method contains a potential lazy fallback where it might try to use `binary.manifest` if it's "in" `self.env`, but this is poorly defined for an `AbstractModel`.
  - **Fix:** Refined the check to properly use `registry` to see if the module is installed.
- **File:** `zero_sudo/tests/common.py`
  - **Issue:** Multiple `except Exception: pass` and `except OSError: pass` blocks which could hide legitimate failures during browser or daemon cleanup.
  - **Fix:** Added targeted logging and specific exception handling.

## Proposed Linter Rules for `check_burn_list.py`

- **Rule:** `MANDATE_GLOBAL_MARKER`: All models in modules must be explicitly marked as multi-tenant or global with a comment and an `@ANCHOR`.
- **Rule:** `BAN_LAZY_HASATTR_REGISTRY`: Block the use of `hasattr(self.env.registry, ...)` for checking if a model exists; use `self.env.registry.get(model_name)` or `model_name in self.env` instead.

## Global Regression Hurdles

- **Status:** Final verification of the `zero_sudo` module passed all local tests and linters. Global regression was not fully performed due to pre-existing violations in other modules as documented in previous sessions, but `zero_sudo` remains isolated and compliant.
