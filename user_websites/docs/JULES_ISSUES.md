# Jules VM Testing Environment Issues

## Provisioning Issues

When running `./tools/test.py --provision-jules -u user_websites`, the provisioning step fails because the following packages cannot be found by `apt-get`:
- `postgresql-17-pgvector`
- `kopia`

The output from `apt-get install` is:
```
E: Unable to locate package postgresql-17-pgvector
E: Unable to locate package kopia
```

## Standard Run Issues

When running `./tools/test.py -u user_websites --already-provisioned` (or similar standard runs without provisioning), the tests fail with the following errors:

1. A PostgreSQL socket timeout error:
```
[*] Skipping full Jules provisioning; verifying local PostgreSQL...
[*] Waiting for PostgreSQL unix socket /opt/hams/pgsock/.s.PGSQL.5432 to open...
❌ ERROR: PostgreSQL socket /opt/hams/pgsock/.s.PGSQL.5432 did not open within 60.0 seconds.
```

2. A missing `psql` binary error:
```
[*] Dropping and Rebuilding Database Schema (hams_test)...
❌ ERROR: Could not find PostgreSQL binary: psql
```
