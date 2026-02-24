# Runbook: Continuous Integration & Deployment (CI/CD)

This runbook defines the automated testing and deployment pipeline for the Hams.com platform, ensuring that all code modifications satisfy the Behavior-Driven Development (BDD) criteria before reaching production.

## 1. GitHub Actions Workflow
The primary CI pipeline is defined in `.github/workflows/odoo_tests.yml`.
It is configured to run on every `push` and `pull_request` to the `main` and `develop` branches.

## 2. Production Parity Environment
To prevent "it works on my machine" discrepancies, the GitHub Actions runner spins up ephemeral Docker service containers that exactly mirror the production infrastructure:
* **PostgreSQL 15:** The core transactional database.
* **Redis 7:** The ephemeral storage layer for the Zero-DB DX Cluster and API Idempotency checks.
* **RabbitMQ 3:** The message broker handling ADIF processing and PowerDNS synchronization.

## 3. Automated Test Execution
The pipeline installs Odoo 19 Community and all required Python dependencies (including external daemon libraries like `ephem`, `asyncpg`, and `pika`). 
It then executes the `odoo-bin` test runner targeting our custom modules. 

**Release Gating:** A Pull Request **CANNOT** be merged unless 100% of the BDD unit tests pass. If a developer modifies a Semantic Anchor `# [%ANCHOR: ...]`, they must ensure the corresponding test suite is updated to reflect the new business logic.
