# Runbook: Daemon Management

We shift heavy, high-concurrency tasks away from Odoo's web workers and into dedicated background daemons.

**For tactical execution steps regarding starting, stopping, or viewing the logs of these daemons, please refer to the [Docker Deployment Guide](../../deploy/DOCKER_DEPLOYMENT.md) or the [Debian Deployment Guide](../../deploy/DEBIAN_DEPLOYMENT.md).**

## 1. Virtual Environment Provisioning
*(Reference: `daemons/setup_venvs.sh` and `daemons/run_daemon.sh`)*
Daemons run inside isolated, PEP-668 compliant Python virtual environments. We initialize these automatically so they never break the host operating system.

## 2. Core Operational Workers
* **ADIF Processor:** *(Reference: `daemons/adif_processor/adif_processor.py`)* Listens to RabbitMQ to parse and ingest massive user-uploaded logbook files. APIs trigger `[%ANCHOR: api_enqueue_adif_task]` and `[%ANCHOR: web_enqueue_adif_task]`, which are consumed by `[%ANCHOR: consume_adif_task]`.
* **Live DX Firehose:** *(Reference: `daemons/dx_firehose/dx_firehose.py`)* A high-performance WebSocket server that connects directly to the PostgreSQL database. It bypasses the standard WSGI layer completely to handle massive concurrent subscriber loads.
* **PowerDNS Synchronization:** *(Reference: `daemons/pdns_sync/pdns_sync.py`)* Consumes domain update events via `[%ANCHOR: pdns_rabbitmq_consumer]` and modifies the isolated PowerDNS infrastructure.

## 3. Scheduled Polling Services
* **NCVEC Exam Sync:** *(Reference: `daemons/ncvec_sync/ncvec_sync.py`)* Downloads official test pools. **Cost-Saving Cache:** It maintains a local `explanation_cache.json` to store AI-generated HTML explanations. This decouples the Gemini API costs from Odoo's test database, ensuring you don't re-bill API quotas when the database is rebuilt.
* **External QSL Fetcher:** *(Reference: `daemons/lotw_eqsl_sync/lotw_eqsl_sync.py`)* Executes daily to retrieve verified confirmations from third-party networks (`[%ANCHOR: daemon_sync_lotw_batch]` and `[%ANCHOR: daemon_sync_eqsl_batch]`).
* **Regulatory Data Sync:** *(Reference: `daemons/fcc_uls_sync/fcc_sync.py`, etc.)* Downloads large archives from global telecommunications authorities. Triggered via `[%ANCHOR: daemon_sync_fcc_batch]` which calls `[%ANCHOR: odoo_sync_fcc_batch]`.
* **Atmospheric Conditions:** *(Reference: `daemons/noaa_swpc_sync/noaa_swpc_sync.py`)* Retrieves solar flux and planetary K-index telemetry via `[%ANCHOR: fetch_solar_metrics]`.
* **Satellite TLE Sync:** Executes `[%ANCHOR: daemon_sync_tles]` which cascades to `[%ANCHOR: odoo_sync_tles]`.
