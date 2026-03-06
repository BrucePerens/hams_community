# Odoo Core Modules & SRE Platform

Welcome to the foundational Odoo 19 ecosystem. This repository contains a suite of enterprise-grade, open-source modules designed to transform Odoo into a highly secure, heavily optimized, and decentralized community platform.

This repository is also the source of truth for our strict LLM-assisted development standards, ensuring all code remains secure, accessible, and architecturally sound.

## 🚀 The Module Ecosystem

We have engineered these modules to be perfectly isolated and drop-in ready for any Odoo project. They do not rely on proprietary external codebases.

### 🌐 Decentralized Community & Content
* **User Websites (`user_websites`)**: Empower your community with decentralized, multi-tenant web hosting.
  * **Personal & Group Sites**: Users get their own URLs (e.g., `/username/home`) with drag-and-drop page building.
  * **Shared Blogging**: A unified backend blog container dynamically filtered to give each user their own perceived personal blog.
  * **Automated Moderation**: Built-in 3-strike violation reporting, automatic suspensions, and an integrated appeals process.
  * **Community Directory**: An opt-in public directory for users to showcase their profiles.
* **User Websites SEO (`user_websites_seo`)**: Put your users on the front page of Google.
  * **Native SEO Fusion**: Injects Odoo's native SEO mixin directly into user profiles.
  * **Zero-Sudo Execution**: Allows standard users to interactively optimize their meta titles, descriptions, and OpenGraph images without requiring administrative privileges.
* **Manual Library (`manual_library`)**: A clean-room, open-source replacement for Odoo's Enterprise Knowledge app.
  * **Enterprise API Interoperability**: 100% drop-in compatibility with `knowledge.article`.
  * **Dynamic Architecture**: Infinite hierarchical folder nesting, auto-generated Tables of Contents, and rich-text editing.
  * **Granular Access**: Contextual access rights ranging from private admin notes to shared workspace drafts and public guides.

### 🛡️ Enterprise Security & Compliance
* **Zero-Sudo Security Core (`zero_sudo`)**: Bulletproof your architecture with strict least-privilege enforcement.
  * **The Micro-Service Account Pattern**: Completely eliminates dangerous `.sudo()` calls by securely proxying background tasks.
  * **Daemon Lockout**: Mathematically prevents service accounts from executing interactive web logins.
  * **SSTI Protection**: Strictly whitelists system parameter extraction to protect cryptographic keys from template injections.
* **Global Compliance (`compliance`)**: Automate the legal headaches of running a modern platform.
  * **Zero-Touch Enforcement**: Automatically activates Odoo's native ePrivacy cookie consent bar globally.
  * **Legal Boilerplates**: Auto-provisions non-destructive, AGPL-3 compatible templates for Privacy Policies, Terms of Service, and Cookie Policies.
  * **GDPR Workflows**: Native portals for instant data portability (JSON export) and permanent Right to Erasure cascade deletions.

### ⚡ Edge Orchestration & Performance
* **Cloudflare Edge Orchestration (`cloudflare`)**: Command your CDN and WAF directly from the Odoo backend.
  * **Automated Cache Purging**: Scans static files on boot and automatically invalidates stale assets globally via Cache-Tags.
  * **WAF Management**: Build, deploy, and backup Cloudflare Firewall rules from the UI.
  * **Silent Honeypots**: Traps malicious bots in hidden form fields and instantly bans their IPs at the network edge.
  * **Zero Trust**: Provision and deploy `cloudflared` edge tunnels with one click.
* **Aggressive Edge Caching (`caching`)**: Turn your user's browser into a lightning-fast CDN.
  * **Global Service Worker**: Intercepts requests for JS, CSS, and static assets, loading them locally with 0ms latency.
  * **Dynamic Quota Safety**: Mathematically calculates payload sizes during boot to prevent browser quota exhaustion.
  * **Zero-Config Integration**: Automatically caches assets for all installed custom modules.

### 📟 Site Reliability Engineering (SRE) & DBA
* **Pager Duty & Generalized Monitoring (`pager_duty`)**: Datadog-level reliability engineering natively integrated with your ERP.
  * **Airgapped Execution**: Standalone async Python daemons that alert you via SMTP/Webhooks even if Odoo crashes.
  * **Intelligent Routing**: Natively integrates with Odoo Calendar shifts to instantly ping whoever is on call.
  * **Deep Protocol Checks**: Monitors HTTP/3, DNS, PostgreSQL, Nginx syntax, Certbot dry-runs, and custom SQL anomaly detection.
* **Database Management & APM (`database_management`)**: An enterprise DBA toolkit built right into Odoo.
  * **Real-Time Telemetry**: Tracks autovacuum bloat, cache hit ratios, and slow queries directly from `pg_stat_statements`.
  * **Active Remediation**: GUI-driven `VACUUM ANALYZE` commands and live session kill-switches.
  * **Optimization Wizards**: Dynamically calculates and applies hardware-aware PostgreSQL tuning configurations.
  * **HA Orchestrator**: Generates exact deployment topologies for Patroni and PgBouncer.
* **Unified Backup Management (`backup_management`)**: A single pane of glass for disaster recovery.
  * **Hybrid Architecture**: Orchestrates both Kopia (file state) and pgBackRest (PostgreSQL WAL).
  * **Automated Drills**: Executes and validates automated restore drills to mathematically prove backup integrity.
  * **Anomaly Detection**: Triggers Pager Duty alerts if snapshots miss minimum expected file sizes.
* **Real Transaction Testing (`test_real_transaction`)**: Stop fighting the ORM test cache.
  * **True Commits**: Bypasses standard savepoints to allow actual database commits during test execution.
  * **Leak Detection**: Features a strict SQL leak detector to guarantee pristine test environments.

## 🤖 LLM-Assisted Development Standards

When we use AI to write code, we force it to follow strict rules. This keeps the code secure, accessible, and up to date with Odoo 19 standards.

* **`docs/LLM_GENERAL_REQUIREMENTS.md`**: Our global rules for the AI. It covers how the AI should talk to us (no fluff, conversational tone), how it should handle security, and the four-backtick `plaintext` Parcel format it must use to send us code.
* **`docs/LLM_ODOO_REQUIREMENTS.md`**: Our strict Odoo coding rules. This includes the "Burn List"—a list of old, bad Odoo habits and legacy syntax the AI is explicitly forbidden from using.
* **`docs/LLM_LINTER_GUIDE.md`**: The exhaustive reference sheet for the platform's DevSecOps pipeline and AST linter traps.

## ⚖️ License & Copyright

Copyright © Bruce Perens K6BP. This software is licensed under the **GNU Affero General Public License, version 3 (AGPL-3.0)**. See the `LICENSE` file for more details.
