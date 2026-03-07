# Unified SRE & DevSecOps Platform

This repository contains the enterprise-grade modules for Odoo 19 Community, focusing on high availability, security, decentralization, and robust disaster recovery.

## Key Capabilities

### 1. Zero-Sudo Privilege De-Escalation
Replaces brute-force `.sudo()` usage with precision Micro-Service Accounts, enforcing strict Least Privilege access constraints across all background tasks and automated cron jobs.

### 2. Pager Duty & Active Anomaly Hunting
A highly resilient, multi-threaded SRE daemon that monitors infrastructure health asynchronously.
* **Splunk-like Log Analytics:** Features a live, chrooted log analyzer daemon that drops all Linux kernel capabilities (`prctl`) and de-escalates to `nobody:adm` to safely tail `/var/log` for RegEx anomalies without exposing server shells to the UI. Includes a real-time, Redis-backed frontend web viewer.
* **Network Polling:** Executes L4/L7 health checks, SSL expiration calculations, and PostgreSQL query baseline evaluations.

### 3. Secure Binary Downloader (`binary_downloader`)
A dedicated, database-backed provisioning module. It prevents Arbitrary File Write hijack attacks by storing download URLs, extraction targets, and rigid SHA-256 cryptographic checksums directly in Odoo's restricted technical settings, securely distributing dependencies (like `kopia`, `etcd`, `cloudflared`) to requesting modules.

### 4. Backup & Disaster Recovery Orchestration
Leverages `Kopia` and `pgBackRest` for immutable, encrypted backups to S3/B2 endpoints. Features an automated "Restore Drill" capability that periodically executes full data validations to mathematically prove backup integrity.

### 5. PostgreSQL High Availability Configuration
Generates deterministic configurations for Patroni, etcd, and PgBouncer to orchestrate multi-node automated database failover.

## Installation

Use the interactive bare-metal wizard or the provided Docker Compose stack:
```bash
python3 tools/deploy_wizard.py
```

## Documentation

Detailed API boundaries, UI Tour mappings, and architectural Decision Records (ADRs) are embedded throughout the `docs/` directory. All modules natively hook into the `manual_library` system upon installation to distribute their end-user documentation contextually directly into the Odoo UI.
