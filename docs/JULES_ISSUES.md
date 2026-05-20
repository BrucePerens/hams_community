# JULES ISSUES

## 2026-05-19 - manual_library
- `tools/run_linters.py` is not present in the repository, despite being mentioned in the instructions. Used `tools/run_linters.sh` instead.
- `ldap3` dependency was missing from the system Python environment, which caused the test runner to fail during global testing. Manually installed it.
- Provisioning the Jules environment (`--provision-jules`) takes a significant amount of time and occasionally times out or hits apt lock issues.
- Encountered `RuntimeError: object is not bound` in `cloudflare` module tests during global testing, which seems to be a pre-existing issue unrelated to `manual_library`.
- Odoo 19 QWeb does not support `t-while`, which was found in my initial Breadcrumbs implementation. Fixed it by using `t-foreach range(20)` as a workaround for hierarchy traversal.
