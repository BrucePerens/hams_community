# Backup Management Module

## Overview
The Backup Management module provides a robust, multi-tenant aware system for managing automated backups using Kopia and pgBackRest. It is designed to work in a secure, non-sudo environment, offloading heavy tasks to background workers via RabbitMQ.

## Key Features

### 1. Multi-Engine Support
*   **Kopia:** Used for file-level backups. Supports local storage, AWS S3, and Backblaze B2.
*   **pgBackRest:** Used for high-performance PostgreSQL database backups.

### 2. Automated Volume Synchronization
The module automatically synchronizes snapshots from the backup repositories into the Odoo database for easy monitoring and management.
*   **Core Sync Anchor:** `[@ANCHOR: backup_management:backup_sync_kopia]`
*   **Database Target Sync Anchor:** `[@ANCHOR: backup_management:backup_sync_pgbackrest]`
*   **Cron Routine Orchestration:** `[@ANCHOR: backup_management:cron_sync_all_backups]`

### 3. Multi-Tenant Awareness
Backups can be isolated by website. Each `backup.config` can be linked to a specific `website_id`, ensuring that users only see and manage backups relevant to their assigned website.

### 4. Retention & Purge Governance
Retention policies (daily, weekly, monthly) can be defined per configuration and are enforced by the backup engine.
*   **Policy Application Engine:** `[@ANCHOR: backup_management:backup_apply_policies]`

### 5. Monitoring & Alerting
*   **Interactive Dashboard:** Provides a real-time overview of backup status and staleness alerts.
    *   **Interactive Dashboard Telemetry:** `[@ANCHOR: backup_management:backup_board_data]`
*   **Pager Duty Integration:** Automatically reports backup failures or anomalies (e.g., snapshots below a minimum size) to Pager Duty.
    *   **Pager Synergy:** `[@ANCHOR: backup_management:backup_pager_synergy]`

### 6. Automated Restore Drills
Supports scheduling automated restore drills using custom shell scripts to ensure backup integrity.

## Technical Specification

### 1. Asynchronous Execution
All backup and restore operations are offloaded to a background worker daemon (`backup_worker.py`) using RabbitMQ. This prevents long-running backup processes from blocking the Odoo web workers.
*   **Trigger Execution:** `[@ANCHOR: backup_management:backup_trigger_execution]`

### 2. Security
*   **Path Validation:** All target paths and scripts are validated against a strict blocklist of system directories and illegal characters.
    *   **Path Validation Anchor:** `[@ANCHOR: backup_path_validation]`
*   **Zero-Sudo Compliance:** No `sudo` operations are used. All actions are performed by dedicated service users with minimal required privileges.
*   **Encryption:** Sensitive data like Kopia passwords and S3 secret keys are encrypted at rest using Fernet encryption.

## Cross-Module Interfaces

### Compliance Monitoring
When multi-website context isolation checks detect data boundary leakage or cross-tenant contamination, logging structures communicate directly with the core website security system:
*   **Tenant Violation Reports:** For tracking frontend moderation workflow alerts, see `[@ANCHOR: user_websites:UX_REPORT_VIOLATION]`.
*   **Automated Escalation:** System telemetry monitors structural volume metrics and communicates alerts dynamically.
