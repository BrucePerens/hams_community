# Jules Issues for pager_duty

## AI Hallucinations & Laziness
- **Shortcut detected**: `pager_duty/daemon/pager_log_analyzer.py` uses `hasattr(os, "chroot")` to conditionally execute chroot. On Linux, `os.chroot` is standard. If the environment requires chroot for security, it should fail if it's not available.
- **Shortcut detected**: `pager_duty/daemon/pager_log_analyzer.py` uses `hasattr(os, "chroot")` in `translate_path` which can lead to inconsistent path resolution if it's missing.

## Fallbacks & Missing Resources
- **Resource Fallback**: `pager_duty/daemon/generalized_monitor.py` contains `verify_and_install_dependencies` which attempts to "provision" missing binaries (like `dig`, `snmpget`, etc.) by calling an RPC method `rpc_ensure_executable` on the Odoo server. This violates the "FAIL FAST" principle. The environment should be properly prepared with all necessary dependencies before the daemon starts.

## Multi-Tenant Awareness
- **Model Isolation**: `calendar.event` (extended in `pager_duty/models/schedule.py`) lacks a `website_id` field, making it difficult to have per-website on-duty schedules.
- **Logic Isolation**: `action_escalate_unacknowledged` in `pager_duty/models/incident.py` does not group by `website_id` or `company_id` when escalating, which could lead to cross-tenant data exposure in notifications or incorrect escalation logic in a multi-tenant environment.
- **Logic Isolation**: `get_current_on_duty_admin` in `pager_duty/models/schedule.py` does not filter by `website_id`.

## Security
- **RPC Privileges**: `rpc_ensure_executable` in `pager_check.py` allows requesting any command name. While it has some checks (no `/`), it's a powerful tool that might be abused if not strictly controlled.
- **Daemon Connectivity**: The daemon uses a bearer token (password) for Odoo JSON-2 API. Ensure this is handled as a micro-privilege service account.

## Suggested Linter Rules for `check_burn_list.py`
- Disallow `hasattr(os, 'chroot')` - assume POSIX environment.
- Disallow logic that attempts to install or provision OS-level binaries at runtime.
