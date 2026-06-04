# Jules Issues & Observations

## Automated Verification Environment
- **PostgreSQL Authentication:** Default `peer` authentication failed for `odoo` and `jules` users when connecting via Unix socket. Resolved by updating `/etc/postgresql/18/main/pg_hba.conf` to use `trust` for local connections.
- **Chrome Startup Issue:** Encountered `Failed to connect to the bus: Address does not contain a colon` errors during UI tours. Resolved by installing `dbus-x11` in the VM environment.
