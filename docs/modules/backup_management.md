# 💾 Backup Management (`backup_management`)

## Architecture
* **Self-Healing Dependencies:** Uses `shutil.which` to detect tools. If `kopia` is missing from the system path, it automatically fetches and extracts the pre-compiled Linux binary into the `var/lib/odoo/hams_bin` local data directory to ensure uninterrupted operation.
Implements the Best-in-Class Hybrid Architecture proposed for unified backup management.
* **Kopia:** Used for file/system state. Parsed via `kopia snapshot list --json`.
* **pgBackRest:** Used for PostgreSQL WAL archiving. Parsed via `pgbackrest info --output=json`.
* **Orchestration:** Capable of pushing execution commands (`kopia snapshot create`, `pgbackrest backup`) directly to the underlying daemons via `subprocess` from the UI.

## Security
* **Service Account:** Utilizes `user_backup_service_internal` for background synchronization.
* **Encryption:** Kopia passwords are encrypted at rest using the system's `HAMS_CRYPTO_KEY` Fernet key via standard getter/setter properties.
* **Subprocess Execution:** Uses Python's `subprocess.run` to interrogate local CLIs.
* **Pager Duty Synergy:** Employs a soft-dependency on `pager_duty`. If a CLI command fails or a backup snapshot becomes stale (no new snapshots in >26 hours), the module directly invokes `pager.incident.report_incident()` using the `pager_service_internal` micro-account to instantly alert the on-call SRE.
* **Size Anomaly Detection:** The config model evaluates newly ingested snapshots against `minimum_size_mb`. If an empty or suspiciously small snapshot is generated (e.g., missing Docker volume mounts), it escalates a critical alert.

---

## Semantic Anchors
* `[%ANCHOR: backup_restore_command]`
* `[%ANCHOR: backup_trigger_execution]`
* `[%ANCHOR: backup_apply_policies]`
* `[%ANCHOR: backup_pager_synergy]`
* `[%ANCHOR: backup_board_data]`
* `[%ANCHOR: backup_sync_kopia]`
* `[%ANCHOR: backup_sync_pgbackrest]`
* `[%ANCHOR: cron_sync_all_backups]`
* `[%ANCHOR: test_backup_cron]`
* `[%ANCHOR: test_backup_view]`
* `[%ANCHOR: test_backup_orchestration]`
