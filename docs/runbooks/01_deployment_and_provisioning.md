# Runbook: Deployment & Provisioning

This document serves as the high-level operational map for provisioning the Hams.com architecture. 

**For step-by-step execution, CLI commands, and server setup instructions, you MUST refer to the authoritative tactical guides:**
* 🐳 **[Docker Deployment Guide](../../deploy/DOCKER_DEPLOYMENT.md):** The primary, highly-secure orchestration method using containerized isolation.
* 🐧 **[Bare-Metal Debian Guide](../../deploy/DEBIAN_DEPLOYMENT.md):** Legacy/Alternative method for direct OS installations.
* ☁️ **[Cloudflare mTLS Guide](../../deploy/CLOUDFLARE_MTLS_GUIDE.md):** Network edge configuration for Zero-Touch authentication.

---

## 1. Environment Preparation & Secrets Management
*(Reference: `deploy/.env.template`)*
The application utilizes a centralized environment file for secrets management. External infrastructure tokens (such as PowerDNS, RabbitMQ, and Cloudflare API keys for Edge Orchestration) are fully abstracted from the Python source code.

**Securing the Odoo Admin Password (ADR-0006):**
To comply with strict DevSecOps mandates, the UI Admin password is never stored in plaintext within the `.env` vault. It must be cryptographically hashed (PBKDF2-SHA512) using the interactive `tools/hash_admin_password.py` utility before deployment. Please see the Docker Deployment Guide for exact execution steps.

## 2. Docker Orchestration (Production Standard)
*(Reference: `deploy/docker-compose.yml`)*
The platform is managed holistically via Docker Compose. The stack provisions:
* **PostgreSQL 16:** Core relational database.
* **Redis 7:** Ephemeral caching, API idempotency, and DX Cluster Zero-DB history.
* **RabbitMQ 3:** Asynchronous event bus for ADIF processing and DNS CQRS workers.
* **Nginx:** Edge routing, rate limiting, and ARRL mTLS certificate termination.
* **Odoo 19:** The core Python/WSGI application layer.
* **Background Daemons:** Isolated Python containers executing high-I/O background polling without blocking the primary UI workers.

## 3. PowerDNS CQRS Architecture
*(Reference: `daemons/pdns_sync/pdns_sync.py`)*
To shield the primary ERP database from massive external DNS query volumes, PowerDNS is configured to read from an isolated SQLite backend. The Odoo application acts exclusively as the command interface, pushing structural updates to a RabbitMQ queue. The external sync daemon retrieves these events and applies them to the authoritative nameserver via REST API.
