# Jules Environment Issues

## PostgreSQL Connectivity
The standard `tools/test.py` script fails to rebuild the database because it encounters connection refused errors on `localhost:5432`.
This appears to be due to the PostgreSQL service being down or misconfigured in the Jules VM environment.
I have attempted to start the service using `pg_ctlcluster`, but it frequently shuts down or the socket becomes unavailable.

## Workaround
I have used a custom test runner that points to `PGHOST=localhost` and ensures the service is up before running tests.
Tests were verified using `sudo -E -u odoo /usr/bin/python3 /usr/bin/odoo ...` with the correct addons path.
