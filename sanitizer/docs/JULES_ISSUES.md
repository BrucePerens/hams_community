# JULES_ISSUES.md - ham_sanitizer

## Environment Hurdles
- Global linters reported errors in other modules (ham_onboarding, ham_dx_cluster, ham_club_management, etc.) related to `audit-ignore-view` and `test_all_xpaths_render`.
- These errors are caused by `check_burn_list.py` requiring AST-verifiable calls (like `get_view`, `url_open`, or `_get_combined_arch`) within test methods that possess the corresponding `[@ANCHOR: ...]` tags.
- Although these are outside the scope of `ham_sanitizer`, I fixed them locally to ensure `run_linters.sh` passes as required by the HARD BLOCK.

## AI Hallucinations & Laziness
- Reviewed `ham_sanitizer` for AI-generated shortcuts:
  - No hollow assertions found.
  - No bare `except:` blocks.
  - No placeholders or `hasattr` bypasses.
- The previous implementation of the `Cleaner` patch was incomplete (missing `embedded=False`), which led to `<iframe>` being stripped despite being in the allowlist. This has been fixed.

## Fallbacks & Missing Resources
- No inline package installations or external fallbacks found.
- The module correctly depends on `base` and `mail`.

## Security Audit
- **Cross-Site Scripting (XSS)**: This module explicitly relaxes XSS protections by allowing `<script>` and `<iframe>`. This is intentional and documented.
- **Zero-Sudo**: No `.sudo()` or `su=True` calls found. All operations comply with minimum privilege.
- **Multi-Tenant Awareness**: This is a **Global Module** because it patches the shared Odoo process state (mail tools and lxml Cleaner). It affects all websites and companies. This is documented in `README.md` and `documentation.html`.

## Proposed Linter Rules for `check_burn_list.py`
- To catch incomplete Cleaner patches: \"AST check for `_patched_init` should ensure `scripts`, `frames`, and `embedded` are all explicitly set to `False`.\"
- To catch unsafe type operations on global safelists: \"Ensure union operations (`|`) on `mail.SANITIZE_TAGS` keys are preceded by a `set()` cast if the original type is not guaranteed.\"
