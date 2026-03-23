# Unified Deployment Guide

This guide provides a consolidated, step-by-step workflow for deploying and testing the complete Hams.com architecture. We utilize an intelligent, fully idempotent Python deployment wizard that seamlessly handles both containerized (Docker) and bare-metal (Debian 12) environments.

## 1. Architecture Highlights
* **Secrets Management:** All credentials (PostgreSQL, RabbitMQ, PowerDNS API) are completely abstracted out of the code and managed via a secure `.env` file.
* **Secure Password Hashing:** Adhering to ADR-0006, the Odoo UI Admin password is never stored in plaintext. It is cryptographically hashed and automatically injected into the vault.
* **Nginx Edge Routing:** Terminates SSL, enforces API Rate Limiting, and securely validates ARRL LoTW `.p12` certificates before passing them to the internal Odoo application.
* **CQRS PowerDNS:** The wizard dynamically provisions PowerDNS to read from an isolated SQLite backend, decoupling DNS resolution from the main ERP database.
* **Multi-Repository Architecture:** The system mounts all four core repositories (`hams_community`, `hams_private_primary`, `hams_private_secondary`, `hams_private_tertiary`) dynamically during Docker orchestration to ensure seamless interoperability across the full platform.

## 2. Execution
Navigate to the `deploy/` directory and run the deployment wizard:
```bash
cd deploy
pip install passlib cryptography
python3 deploy_wizard.py
```

The interactive wizard will:
1. Securely generate the `.env` vault.
2. Ask if you want to deploy via **Docker Compose** or **Bare-Metal Debian**.
3. Scaffold self-signed fallback certificates to ensure Nginx boots cleanly.
4. Auto-compile the Hamlib relay client packages (from the tertiary directory).
5. Provision the services and start the stack.

**Idempotency Guarantee:** If the installation halts due to network failure, simply re-run the command. The wizard detects its previous state via `.env`, skips secret generation, and flawlessly resumes exactly where it left off.

## 3. Post-Deployment SSL (Certbot/LoTW)
Once the stack is running with dummy certificates, you must replace them with real ones:
1. Place your actual Let's Encrypt or Cloudflare Origin certificates in `deploy/ssl/fullchain.pem` and `deploy/ssl/privkey.pem` (or `/etc/nginx/ssl/` for Bare-Metal).
2. Download the ARRL Root CA and save it as `lotw_root.pem` in the same directory.
3. Restart Nginx to apply the real certificates.

## 4. Running the Test Suite
If you are developing modules, utilize the `START.sh` testing tool from the repository root:
```bash
./tools/START.sh
```
This script automatically runs the Burn List linter, drops the test database, and runs the isolated Python `TransactionCase` suite across all synchronized namespaces.
