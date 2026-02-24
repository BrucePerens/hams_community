# Runbook: Daemon Management

The platform intentionally shifts high-concurrency and heavy I/O operations away from the standard Odoo web workers into dedicated background processes.

**For tactical execution steps regarding starting, stopping, or viewing the logs of these daemons, please refer to the [Docker Deployment Guide](../../deploy/DOCKER_DEPLOYMENT.md) or the [Debian Deployment Guide](../../deploy/DEBIAN_DEPLOYMENT.md).**

## 1. Virtual Environment Provisioning
*(Reference: `daemons/setup_venvs.sh` and `daemons/run_daemon.sh`)*
All background services execute within isolated, PEP-668 compliant Python environments. These environments are initialized automatically to ensure system dependencies do not conflict with the host operating system.

## 2. Core Operational Workers
* **ADIF Processor:** *(Reference: `daemons/adif_processor/adif_processor.py`)* Listens to RabbitMQ to parse and ingest massive user-uploaded logbook files.
* **Live DX Firehose:** *(Reference: `daemons/dx_firehose/dx_firehose.py`)* A high-performance WebSocket server that connects directly to the PostgreSQL database. It bypasses the standard WSGI layer completely to handle massive concurrent subscriber loads.
* **PowerDNS Synchronization:** *(Reference: `daemons/pdns_sync/pdns_sync.py`)* Consumes domain update events and modifies the isolated PowerDNS infrastructure.

## 3. Scheduled Polling Services
* **NCVEC Exam Sync:** *(Reference: `daemons/ncvec_sync/ncvec_sync.py`)* Downloads official test pools. **Cost-Saving Cache:** It maintains a local `explanation_cache.json` to store AI-generated HTML explanations. This decouples the Gemini API costs from Odoo's test database, ensuring you don't re-bill API quotas when the database is rebuilt.
* **External QSL Fetcher:** *(Reference: `daemons/lotw_eqsl_sync/lotw_eqsl_sync.py`)* Executes daily to retrieve verified confirmations from third-party networks like the ARRL.
* **Regulatory Data Sync:** *(Reference: `daemons/fcc_uls_sync/fcc_sync.py`, etc.)* Downloads large, compressed archives from global telecommunications authorities to keep the local directory current.
* **Atmospheric Conditions:** *(Reference: `daemons/noaa_swpc_sync/noaa_swpc_sync.py`)* Retrieves solar flux and planetary K-index telemetry from federal weather APIs.
