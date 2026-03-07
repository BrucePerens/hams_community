# Open Source Community Modules for Odoo 19

Welcome to a comprehensive suite of open-source modules designed for **Odoo 19 Community**. This repository provides tools for scaling horizontally, defending against automated attacks, and building decentralized user communities, all while maintaining rigorous security and developer ergonomics.

---

## 🤖 Deterministic AI Management & Tooling

Our platform is built to seamlessly integrate Large Language Models (LLMs) into a precise DevSecOps pipeline.

* **[Isolated Task Workspaces](tools/create_task_workspace.py):** Partition tasks to prevent LLM cognitive overload and context drift.
* **[MIME-Like Parcel Transport](docs/LLM_GENERAL_REQUIREMENTS.md):** Ensure flawless code modifications using a secure, multi-block transport schema.
* **[Semantic Token Matching](tools/parcel_extract.py):** A patching engine that ignores superficial formatting, ensuring AI-generated patches dock perfectly.
* **[AST Burn List Linters](docs/LLM_LINTER_GUIDE.md):** Deep AST Verification prevents AI agents from utilizing deprecated syntax or insecure anti-patterns.
* **[True Environment Parity](test_real_transaction/README.md) (`test_real_transaction`):** A testing facility that bypasses Odoo's test cursor wrapper for true database commits and cross-worker behavior testing.

---

## 🛡️ Security & Edge Defense

Security is mathematically enforced at the lowest levels of the architecture.

* **[Zero-Sudo Security Core](zero_sudo/README.md) (`zero_sudo`):** Replaces Odoo's `.sudo()` method with a centralized Micro-Service Account pattern for least-privilege execution.
* **[Binary Downloader](binary_downloader/README.md) (`binary_downloader`):** A database-backed module that securely provisions static executables at runtime, validating strict SHA-256 checksums to protect against Arbitrary File Write vulnerabilities.
* **[Cloudflare Edge Orchestration](cloudflare/README.md) (`cloudflare`):** Control your CDN directly from Odoo to deploy WAF bans, Zero Trust Tunnels, and Turnstile CAPTCHA.

---

## ⚡ Performance & Scale

Built to handle high traffic and distributed workloads efficiently.

* **[Caching PWA](caching/README.md) (`caching`):** A zero-config Service Worker that intercepts network requests to act as a client-side CDN for static assets.
* **[Distributed Redis Cache](distributed_redis_cache/README.md) (`distributed_redis_cache`):** A Redis-backed pub/sub bus ensuring fine-grained phase coherence and instant cache invalidation across all Odoo WSGI nodes.
* **[Database Management & APM](docs/modules/database_management.md) (`database_management`):** An in-GUI DBA toolkit to track table bloat, terminate hanging sessions, and generate HA configurations for Patroni and PgBouncer.

---

## 🚨 Site Reliability Engineering (SRE)

* **[Pager Duty](pager_duty/PROMO.md) (`pager_duty`):** An isolated, Datadog-level Python daemon running outside Odoo's web workers, featuring airgapped SMTP fallbacks, un-cached DNS lookups, and intelligent calendar-based routing.
* **[Backup & Disaster Recovery](backup_management/README.md) (`backup_management`):** A centralized GUI orchestrating `Kopia` and `pgBackRest` with automated restore drills to prove snapshot integrity.

---

## 🌐 Decentralized Community & Content

Empower users while maintaining legal compliance and moderation capabilities.

* **[User Websites](user_websites/README.md) (`user_websites`):** Allows users to build personal or group websites safely using a Proxy Ownership pattern and shared blog container.
* **[Manual Library](manual_library/README.md) (`manual_library`):** A clean-room, open-source replacement for the Knowledge app, enabling hierarchical instruction manuals.
* **[Global Compliance](compliance/README.md) (`compliance`):** Automatically provisions GDPR/CCPA privacy pages, terms of service, and enforces cookie consent across the ecosystem.

---

## 🚀 Ready to Deploy?

Use the interactive bare-metal wizard or the provided Docker Compose stack to get started:
```bash
python3 tools/deploy_wizard.py
```
@@
