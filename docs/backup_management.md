# Backup Management

The `backup_management` module provides a unified interface for managing backups using Kopia and pgBackRest.

## Architecture

This module follows the zero-sudo and micro-privilege architecture. Operations are performed by a dedicated service account `user_backup_service_internal`.

- **Global Sync Cron**: Polling loop to synchronize offsite states `[@ANCHOR: cron_sync_all_backups]`.

## Security

- **Path Validation**: All backup and restore paths are validated to prevent access to sensitive system directories like `/etc`, `/root`, etc.
- **Micro-privileges**: The module uses specific service accounts for different tasks to ensure least privilege.
- **Pager Duty Synergy**: Employs a soft-dependency on `pager_duty`. If a CLI command fails or a backup snapshot becomes stale, the module directly invokes `pager.incident.report_incident()` `[@ANCHOR: backup_pager_synergy]`.

## Configuration

Navigate to **Ham Admin > Backups > Configurations** to set up your backup targets and retention policies.

- **Kopia**: Used for file/system state. State is synchronized via `_sync_kopia` `[@ANCHOR: backup_sync_kopia]`. Retention policies are applied natively via `[@ANCHOR: backup_apply_policies]`.
- **pgBackRest**: Used for PostgreSQL WAL archiving. State is synchronized via `_sync_pgbackrest` `[@ANCHOR: backup_sync_pgbackrest]`.

## Snapshots and Restores

The module automatically syncs snapshot metadata from the backup engines. While restores are usually performed via CLI for safety, this module provides a wizard to help coordinate the process.

- **Orchestration**: Capable of pushing execution commands (`kopia snapshot create`, `pgbackrest backup`) directly to the underlying daemons via `subprocess` from the UI `[@ANCHOR: backup_trigger_execution]`. Can generate automated restore drill commands `[@ANCHOR: backup_restore_command]`.
- **Dashboard Status**: Aggregates target state and snapshot staleness for the NOC display `[@ANCHOR: backup_board_data]`.

## Testing

The following tests are used to verify the module's functionality:
- **Cron Reliability**: Scheduled syncing functions are validated by `[@ANCHOR: test_backup_cron]`.
- **View Rendering**: Interface layouts and dashboards are verified by `[@ANCHOR: test_backup_view]`.
- **Subprocess Orchestration**: Shell executions are strictly mocked and verified by `[@ANCHOR: test_backup_orchestration]`.
- **Policies**: Policy application is tested by `[@ANCHOR: test_apply_policies]`.
- **Auto-download**: Kopia auto-download is tested by `[@ANCHOR: test_kopia_auto_download]`.
- **Triggers**: Backup triggers are tested by `[@ANCHOR: test_trigger_kopia_and_pgbackrest]`.
