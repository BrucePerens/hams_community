# Runbook: Disaster Recovery & Backups

**For CLI commands related to volume management or restoring database dumps, please refer to the [Docker Deployment Guide](../../deploy/DOCKER_DEPLOYMENT.md).**

## 1. Storage Persistence
*(Reference: `deploy/docker-compose.yml` -> `volumes`)*
The relational database records and binary filestore assets are permanently mapped to persistent Docker volumes (`db_data` and `odoo_data`).

## 2. Automated Archival
*(Reference: `deploy/docker-compose.yml` -> `pgbackups` service)*
A dedicated sidecar container executes automated dumps of the PostgreSQL state every 24 hours. The retention policy maintains a rolling window of 7 daily backups, 4 weekly backups, and 6 monthly archives. These files are accessible in the mapped host directory.

## 3. Ephemeral State Handling
*(Reference: `ham_dx_cluster/models/ham_dx_spot.py`)*
The system explicitly avoids writing real-time cluster spots to disk. This data is cached in a Redis Sorted Set and automatically purged after four hours. If the Redis container experiences a critical failure, the historical buffer is lost, but the system will immediately begin rebuilding the cache as new spots arrive.
