# Jules Provisioning and Testing Issues - daemon_key_manager

## Provisioning Issues
- Warnings about running pip as the 'root' user which can result in broken permissions.
- `initdb: warning: enabling "trust" authentication for local connections`.

## Testing Issues
- `PermissionError: [Errno 13] Permission denied: '/var/lib/odoo/daemon_keys'`: Multiple tests (`test_force_provision_all`, `test_key_ownership`, `test_register_daemon_api`, `test_security_constraints`) failed because the `jules` user lacks write permissions to `/var/lib/odoo/daemon_keys`.
- UI Tour Failure: `TestKeyRegistryTour.test_daemon_key_manager_tour` failed because Chrome headless could not start. Error: `Failed to detect chrome devtools port after 10.0s.` and DBus connection errors.
