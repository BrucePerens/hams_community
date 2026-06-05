# JULES ISSUES - database_management

## Missing Features / Improvements
- Add support for monitoring PostgreSQL replication lag in the UI.
- Implement a graphical representation (chart) for table bloat and query performance trends.
- Integration with external metrics collectors (Prometheus/Grafana) could be beneficial.

## Framework / Environment Hurdles
- UI Tours in Odoo 19/Owl can be flaky. Repaired `db_bloat_tour.js` by simplifying selectors and adding necessary neutral waits.
- `vacuumdb` execution is bypassed in tests to avoid transaction lock issues, which limits integration testing of the actual binary execution.

## Multi-tenant Isolation
- Statistics are logically global. While this is intentional, adding a per-company breakdown for query stats (if possible via `pg_stat_statements` with some tagging) would be a valuable future addition.
