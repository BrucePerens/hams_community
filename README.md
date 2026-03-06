# Odoo Core Modules & Enterprise SRE Platform

Welcome to the foundational Odoo 19 ecosystem. This repository contains a suite of enterprise-grade, open-source modules designed to transform Odoo into a highly secure, heavily optimized, and decentralized community platform. 

While these modules offer features typically locked behind expensive enterprise SaaS subscriptions, this entire suite is **100% open-source and free**. They are engineered to be perfectly isolated, dropping seamlessly into any Odoo project without relying on proprietary external codebases.

---

## 🚀 The Ecosystem Portfolio

### 🌐 Decentralized Community & Content Management

#### **1. User Websites (`user_websites`)**
*Turn your Odoo instance into a decentralized web-hosting powerhouse.*
Give your community the keys to build their own corner of the internet safely and securely.
* **Personal & Group Sites:** Users receive their own dedicated URLs (e.g., `/username/home`) with full access to Odoo's drag-and-drop page builder.
* **Shared Blogging Engine:** A unified backend blog container dynamically filters content, giving each user their own perceived personal blog without bloating your database.
* **Automated Moderation & Trust:** Built-in "Report Violation" buttons, automated 3-strike suspensions, and a complete user appeals process.
* **Community Directory:** A beautiful, opt-in public directory for users to showcase their profiles and content.

#### **2. User Websites SEO (`user_websites_seo`)**
*Put your users on the front page of Google.*
* **Native SEO Fusion:** Seamlessly injects Odoo's native SEO mixin directly into user profiles.
* **Zero-Sudo Execution:** Safely allows standard users to interactively optimize their meta titles, descriptions, and OpenGraph images without requiring administrative privileges.

#### **3. Manual Library (`manual_library`)**
*A clean-room, open-source replacement for Odoo's Enterprise Knowledge app.*
* **Enterprise API Interoperability:** 100% drop-in compatibility with the `knowledge.article` API. Other modules can install their manuals here instantly.
* **Dynamic Architecture:** Features infinite hierarchical folder nesting, auto-generated sticky Tables of Contents, and standard rich-text editing.
* **Granular Access Control:** Contextual access rights ranging from highly private admin notes to shared workspace drafts and public guides.

---

### 🛡️ Enterprise Security & Privacy Compliance

#### **4. Zero-Sudo Security Core (`zero_sudo`)**
*Military-grade least-privilege architecture.*
* **The Micro-Service Account Pattern:** Completely eliminates Odoo's dangerous `.sudo()` calls by securely proxying background tasks through highly restricted, domain-specific accounts.
* **Daemon Lockout:** Mathematically prevents service accounts from executing interactive web logins, securing your system even if a daemon's credentials are leaked.
* **SSTI Protection:** Strictly whitelists system parameter extraction to protect cryptographic keys from Server-Side Template Injections.

#### **5. Global Compliance Engine (`compliance`)**
*Automate the legal headaches of running a modern platform.*
* **Zero-Touch Enforcement:** Automatically activates and enforces Odoo's native ePrivacy cookie consent bar globally upon installation.
* **Legal Boilerplates:** Auto-provisions non-destructive, AGPL-3 compatible templates for Privacy Policies, Terms of Service, and Cookie Policies.
* **GDPR Workflows:** Provides native portals for instant Data Portability (machine-readable JSON exports) and permanent Right to Erasure cascade deletions.

---

### ⚡ Edge Orchestration & Extreme Performance

#### **6. Cloudflare Edge Orchestration (`cloudflare`)**
*Command your CDN and Web Application Firewall directly from the Odoo backend.*
* **Automated Cache Purging:** Scans static files on boot and automatically invalidates stale assets globally via Cloudflare Cache-Tags.
* **Silent Honeypots & Tarpits:** Traps malicious bots in hidden form fields and instantly drops their IPs at the network edge before they ever reach your server.
* **Turnstile Integration:** Validates modern, invisible CAPTCHA tokens for unauthenticated public forms.
* **Zero Trust Tunnels:** Provision and deploy secure `cloudflared` edge tunnels directly from the Odoo settings menu.

#### **7. Aggressive Edge Caching (`caching`)**
*Turn your user's browser into a lightning-fast CDN.*
* **Global Service Worker:** Intercepts requests for JS, CSS, and static assets, loading them locally from the user's hard drive with true 0ms latency.
* **Dynamic Quota Safety:** Mathematically calculates payload sizes during boot to maximize cache hits without causing browser quota panics.
* **Zero-Config Integration:** Automatically caches assets for all installed custom modules without writing a single line of integration code.

#### **8. Distributed Redis Cache (`distributed_redis_cache`)**
*Fine-grained distributed caching for horizontally scaled Odoo clusters.*
* **Strict Phase Coherence:** Enforces cache invalidation across all WSGI worker nodes simultaneously via a centralized Redis pub/sub bus.
* **Zero-Stampede Architecture:** Invalidates specific model entries directly from RAM without triggering a global cache clear, preserving overall cluster performance.
* **Fail-Open Resilience:** Gracefully falls back to localized memory dictionaries if the Redis server goes offline, maintaining operations without crashing the web workers.

---

### 📟 Site Reliability Engineering (SRE) & DBA Tooling

#### **9. Pager Duty & Generalized Monitoring (`pager_duty`)**
*Datadog-level reliability engineering natively integrated with your ERP.*
* **Airgapped Execution:** Standalone asynchronous Python daemons monitor your system from the outside. If Odoo crashes, the daemon survives to alert you via SMTP or Slack/Discord Webhooks.
* **Intelligent Calendar Routing:** Natively integrates with Odoo Calendar shifts to instantly ping whoever is currently on call.
* **Deep Protocol & Nagios-Style Checks:** Monitors HTTP/3 (QUIC), un-cached DNS root traversals, PostgreSQL sockets, Nginx syntax, Certbot dry-runs, and native protocols including FTP, IMAP, POP3, MySQL, SNMP, and Host OS Load Averages.
* **Graphical Config Engine:** Bidirectionally pulls and pushes configurations between the standalone daemon's YAML file and the Odoo GUI, letting administrators build sophisticated monitoring rules without touching code.
* **Anomaly Detection:** Write custom SQL queries to establish baselines, and let the system page you if the data stops making sense.

#### **10. Database Management & APM (`database_management`)**
*Take absolute control of your PostgreSQL engine.*
* **Real-Time Telemetry:** Tracks autovacuum bloat, cache hit ratios, and slow queries directly from deep `pg_stat` views.
* **Active Remediation:** GUI-driven `VACUUM ANALYZE` commands and live session kill-switches to instantly resolve transaction locks.
* **Optimization Wizards:** Dynamically calculates and applies hardware-aware PostgreSQL tuning configurations (RAM, CPU cores, SSD specs) directly to `postgresql.auto.conf`.
* **HA Orchestrator:** Generates exact deployment topologies and YAML files for Patroni and PgBouncer high-availability clusters.

#### **11. Unified Backup Management (`backup_management`)**
*A single pane of glass for multi-engine disaster recovery.*
* **Hybrid Architecture:** Orchestrates both Kopia (for file and system state) and pgBackRest (for PostgreSQL WAL archiving).
* **Automated Drills:** Executes and validates automated restore shell scripts to mathematically prove backup integrity before disaster strikes.
* **Anomaly Detection:** Triggers Pager Duty alerts if snapshots miss minimum expected file sizes or if the system goes 26 hours without a successful sync.

#### **12. Real Transaction Testing Facility (`test_real_transaction`)**
*Stop fighting the ORM test cache.*
* **True Commits:** Bypasses standard Odoo `TransactionCase` savepoints to allow actual database commits during test execution—vital for testing Redis pub/sub and complex inverse relations.
* **Leak Detection:** Features a strict SQL leak detector that snapshots the schema before and after tests to guarantee pristine environments.

---

## 🤖 LLM-Assisted Development Standards

This repository acts as the source of truth for how we instruct Large Language Models (like AI coding assistants) to write software for us. When we use AI to write code, we force it to follow strict rules, ensuring the code remains secure, accessible, and up to date.

* **`docs/LLM_GENERAL_REQUIREMENTS.md`**: Our global rules for the AI. It covers tone, security paradigms, and the mandatory MIME-like Parcel format for code generation.
* **`docs/LLM_ODOO_REQUIREMENTS.md`**: Our strict Odoo coding rules.
* **`docs/LLM_LINTER_GUIDE.md`**: The exhaustive "Burn List"—a reference sheet of banned syntax, legacy Odoo habits, and DevSecOps AST linter traps.

## ⚖️ License & Copyright

Copyright © Bruce Perens K6BP. This software is licensed under the **GNU Affero General Public License, version 3 (AGPL-3.0)**. See the `LICENSE` file for more details.
