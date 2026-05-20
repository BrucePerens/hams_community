# JULES_ISSUES.md

## 2026-05-19 23:30 - Module: compliance

### Issue: PostgreSQL initialization and permissions
`test_runner.py --provision-jules` failed to correctly initialize the PostgreSQL cluster in `/opt/hams/pgdata`. The directory was owned by root and empty.
**Resolution:** Manually changed ownership to `jules`, ran `initdb`, and started the server using `/opt/hams/pgsock` as the socket directory.

### Issue: RabbitMQ Service Failure
`rabbitmq-server.service` failed to start.
**Status:** Ignored as it didn't prevent `compliance` tests from passing, but might affect other modules.

### Issue: Odoo Shutdown Hang
Odoo tests completed successfully but the process didn't terminate cleanly, requiring a SIGKILL from the test runner.
**Status:** Environment-specific issue, likely due to background threads or systemd limitations in the sandbox.

### Issue: Missing external dependency 'ldap3'
Initial run of all tests failed because 'ldap3' was missing.
**Resolution:** Manually installed 'ldap3' via pip3.

### Issue: Unstable PostgreSQL in sandbox
The PostgreSQL server died several times during testing with "server closed the connection unexpectedly" and "could not open file 'postmaster.pid'".
**Resolution:** Aggressive cleaning of pgdata and re-running --provision-jules.
