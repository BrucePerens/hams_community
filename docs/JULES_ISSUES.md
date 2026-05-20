# JULES_ISSUES.md

| Date | Time (UTC) | Module | Issue Description |
|------|------------|--------|-------------------|
| 2026-05-19 | 23:25 | binary_downloader | `test_runner --provision-jules` failed to start PostgreSQL because of permission issues on `/opt/hams/pgdata` and `/opt/hams/pgsock`. Manually fixed by changing ownership to `jules`. |
| 2026-05-19 | 23:25 | binary_downloader | `test_runner --provision-jules` failed because `ldap3` python package was missing. Manually installed via `apt-get install python3-ldap3`. |
