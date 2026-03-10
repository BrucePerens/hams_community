# 🛢 Database Management (`database_management`)

## Architecture
Provides an enterprise-grade Application Performance Monitoring (APM) and DBA suite directly within Odoo.
* **Stat Tracking:** Connects to native PostgreSQL stat views (`pg_stat_user_tables`, `pg_stat_activity`, `pg_statio_user_tables`, `pg_stat_statements`) to track bloat, cache hits, and slow queries.
* **Active Orchestration:** Exposes `pg_terminate_backend` and `VACUUM ANALYZE` commands to the GUI for immediate incident remediation.
* **Configuration & Tuning:** Evaluates `pg_settings` and provides wizards to dynamically write to `postgresql.auto.conf` via parameterized `ALTER SYSTEM` commands.
* **HA Generation:** Orchestrates exact configuration templates for Patroni and PgBouncer to facilitate horizontal scaling.
* **Self-Healing Dependencies:** Automatically downloads the `etcd` binary from GitHub if missing when generating HA configurations. Detects and utilizes the OS `vacuumdb` binary via `subprocess` for autovacuum overrides, preventing transaction block errors in the ORM.

## Security
* **Strict Access:** Because these tools offer direct, destructive command over the database engine, access is strictly hard-locked to the `base.group_system` (System Administrator) role in the CSV.
* **SQLi Defense:** The module strictly utilizes the `psycopg2.sql` module to safely format table names and parameter values before executing raw queries against the cursor.

---

## Semantic Anchors
* `[%ANCHOR: vacuum_analyze]`: Subprocess execution of `vacuumdb` to clear dead tuples.
* `[%ANCHOR: bloat_alert_synergy]`: Triggers Pager Duty incidents for high table bloat.
* `[%ANCHOR: db_terminate_backend]`: Issues `pg_terminate_backend` to kill queries.
* `[%ANCHOR: db_index_stats]`: Fetches index bloat and usage statistics.
* `[%ANCHOR: pg_optimize_wizard]`: Calculates and applies dynamic `postgresql.auto.conf` settings.
* `[%ANCHOR: pg_ha_wizard]`: Generates Patroni and PgBouncer configurations.
* `[%ANCHOR: test_dba_cron]` / `[%ANCHOR: test_dba_view]` / `[%ANCHOR: test_pg_config_views]`: Automated test verifications.
