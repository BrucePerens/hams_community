# Story: Automated Synchronization

This story describes how the system automatically synchronizes backup metadata from external engines (Kopia and pgBackRest).

## Background
To provide a unified view of the backup state, Odoo must regularly poll the external backup engines for new snapshots and their statuses.

## The Process
1. **Cron Trigger**: A global cron job `[@ANCHOR: cron_sync_all_backups]` runs periodically.
2. **Engine Identification**: The system iterates through all active backup configurations.
3. **Synchronization**:
   - For **Kopia**: It executes `kopia snapshot list --json` and parses the output `[@ANCHOR: backup_sync_kopia]`.
   - For **pgBackRest**: It executes `pgbackrest info --output=json` and parses the output `[@ANCHOR: backup_sync_pgbackrest]`.
4. **Data Ingestion**: New snapshots are created in Odoo, and existing ones are updated.
5. **Dashboard Update**: The aggregated data is made available for the NOC dashboard `[@ANCHOR: backup_board_data]`.

## Security
This operation is performed by the `user_backup_service_internal` service account, ensuring it has only the necessary permissions to read configurations and write snapshot data.
