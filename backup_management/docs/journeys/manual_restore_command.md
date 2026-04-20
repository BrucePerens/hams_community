# Journey: Manual Restore Command Generation

This journey describes how an operator uses Odoo to generate the correct CLI command for a manual restore.

1. **Identify Snapshot**: The operator navigates to **Ham Admin > Backups > Snapshots** and finds the desired point-in-time recovery.
2. **View Details**: They open the snapshot record.
3. **Copy Command**: The "Restore Command" field `[@ANCHOR: backup_restore_command]` contains the pre-formatted CLI command (e.g., `kopia restore <snapshot_id> <target>`).
4. **Execution**: The operator copies this command and executes it on the target server's terminal for maximum safety and control.
