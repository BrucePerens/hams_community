# Changelog

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to strict Semantic Versioning.

## [Unreleased]
### Added
- **SRE Pager Duty Suite (`pager_duty`)**: Implemented an enterprise-grade monitoring daemon featuring ICMP, TCP, Docker, and HTTP/3 checks. Supports cascading failure suppression, maintenance silences, Heartbeat push-monitoring for backups, and Calendar-driven escalation routing. Includes an OWL-based NOC dashboard with OLED burn-in protection.
- **Unified Backup Orchestration (`backup_management`)**: Introduced an automated control plane for `kopia` and `pgbackrest`. Features anomaly detection for small snapshots, automated Weekly Restore Drills, and Pager Duty synergy for failures.
- **Database APM & Administration (`database_management`)**: Added an in-browser toolkit to track PostgreSQL index bloat, execute `vacuumdb` via subprocess to avoid transaction locks, kill active queries, and generate HA Patroni/PgBouncer cluster configurations.
- **Unified Deployment Wizard**: Replaced bash scripts with an interactive Python deployment wizard (`tools/deploy_wizard.py`) that scaffolds self-signed dummy SSL certs, orchestrates Docker builds, and natively handles bare-metal Debian systemd symlinking idempotently.
- **Just-In-Time (JIT) Dependencies**: Enabled Python daemons to automatically download pre-compiled static binaries (like `kopia`, `etcd`, `cloudflared`) from GitHub if they are missing from the host OS.
- **Administrative Impersonation**: Added a secure 'Login As' facility allowing admins to temporarily assume a user's session for troubleshooting, strictly gated by an immutable Chatter audit log.
### Changed
- **Extraction Resiliency**: Formalized the "Strict URL-Encoding Mandate for XML Comments" in the ADRs and General Requirements. LLMs must now URL-encode XML comments (`%3C!-- ... --%3E`) and use the `Encoding: url-encoded` Parcel header to prevent web chat UIs from silently stripping them before extraction.
- **String Formatting Mandate**: Instituted the "40-Character Rule" for Python strings. Strings exceeding 40 characters must now be extracted into variables/constants and formatted using multi-line triple quotes (`"""`) to strictly respect the 70-character line length target and prevent Flake8 E501 violations.
- **Architectural Codification**: Formalized the "Application vs. CMS Page Segregation" mandate in `LLM_ODOO_REQUIREMENTS.md` and `MASTER_10`, strictly reserving `website.page` records for editable CMS content while mandating `@http.route` and `<template>` views for system facilities.
- **Moderation Alerting**: Replaced per-report administrator spam with a daily email digest cron job and an asynchronous session-guarded Toast notification that alerts admins upon login.
- **Conversational Tone Mandate (ADR-0056)**: Formally banned "oblique," academic, and dense corporate-speak from documentation, READMEs, and code comments. Rewrote root documentation to explain the system plainly and directly.
- **Strict SQL Parameterization Mandate**: Updated the core instructions and Linter Guide to explicitly ban f-strings and mandate `psycopg2.sql` for all dynamic schema identifier injections (like `CREATE VIEW` statements) to permanently eliminate AST linter traps.
- **AST Linter Hardening (Burn List)**: Upgraded `check_burn_list.py` to recursively track SQL taints (e.g., intermediate f-strings passed to `cr.execute`), block universal attribute aliases for `.sudo()`, and evaluate `@http.route` controller context to drastically reduce false positives while making obfuscation and evasion impossible.
- **Linter Bypass Testing Mandate (ADR-0052)**: Formalized the rule that any use of a linter bypass tag (`burn-ignore` or `audit-ignore`) MUST be accompanied by an exhaustive automated unit test proving the safety and correctness of the bypassed operation.
- **ADR-0022 Refinement**: Formalized 'Bounded Chunking' requirements to prevent Out-Of-Memory (OOM) crashes and silent false-negatives during massive historical data array processing.
### Security
- **Separation of Privilege**: Extracted global email and chatter post permissions into a highly specialized `mail_service_internal` account, stripping arbitrary mailing rights from other domain-specific service accounts.
- **Separation of Privilege**: Eliminated the final authorized uses of `.sudo().unlink()` and `base.user_admin` escalations for GDPR operations by introducing dedicated micro-accounts (`gdpr_service_internal`), further hardening the Zero-Sudo architecture.
- **Linter Anti-Evasion Hardening**: Expanded `check_burn_list.py` Deep AST Verification to block dead code evasion (placing required assertions after `return`, `raise`, `break`, or `continue`) and loop evasion (wrapping `get_view` validations inside `for`/`while` loops).
- **SSTI & XSS Defense Automation**: Upgraded the Proxy Ownership QWeb sanitizer to use `lxml.etree` instead of regex. If malicious execution tags (`t-eval`, scripts) are detected, the system now automatically files a violation report and issues a formal moderation strike against the attacker.
- **Cross-Tenant Redis Isolation**: Prefixed ephemeral Redis cache keys with the active PostgreSQL database name to prevent data leakage between staging and production environments.
### Added
- **Cloudflare UI Control Plane**: Provisioned the native Odoo frontend UI for the `cloudflare` module, allowing system administrators to review honeypot IP Bans, construct WAF rules, and push/pull firewall configurations directly to the edge without leaving the ERP. Fully mapped with JS UI Tours and BDD Stories.
- **Generalized Cloudflare Edge Orchestrator**: Transitioned the `cloudflare` module to Open Source. Introduced Advanced Edge APIs (WAF IP Banning, Cache-Tag Purging, Turnstile Verification, and Edge Context Parsing) for consumption by proprietary modules. Generalized edge caching rules to dynamically adapt to public vs. authenticated states without requiring hardcoded dependencies on frontend apps.
- **Coherent Caching Rollout**: Expanded ADR-0047 memory caching to Group Websites and the Public Directory. Replaced synchronous PostgreSQL routing queries with O(1) `@tools.ormcache` lookups across all consumer endpoints, protected by distributed phase coherence.
- **Fast-Fail Testing Architecture (ADR-0044)**: Formally mandated that all test deployment scripts (`START.sh`) must execute syntax, XML, and Burn List validation, aborting instantly on failure prior to executing database rebuilds.
- **Solo-Maintainer Optimization (ADR-0043)**: Formalized the mandate for hyper-automation across testing, deployment, and administration. Requires self-healing systems and highly streamlined moderation queues to conserve cognitive load and time.
- **Cloudflare Bot Management (ADR-0041)**: Added API integration to leverage Cloudflare's Rulesets API. It dynamically provisions WAF rules to allow cryptographically verified bots (like Googlebot) while challenging unknown headless scrapers targeting API endpoints.
- **Dynamic Edge Tarpitting (ADR-0040)**: Public modules now push bot IP addresses into an ephemeral Redis cache when a silent honeypot is triggered. This sets the stage for Nginx to seamlessly apply 1-hour bandwidth tarpits to malicious scrapers.
- **Semantic Anchor CI Enforcement**: Added `tools/verify_anchors.py` to automatically scan and fail the pipeline if documented anchors (ADR-0004) detach from the codebase.
- **Parcel Extraction Resiliency**: Upgraded `tools/parcel_extract.py` to support whitespace-agnostic patching. Added the `--ignore-whitespace` flag to diff operations and a regex-based fallback for `search-and-replace` blocks to handle LLM indentation drift.
- **Strict Linter Improvement Mandate**: Clarified that AI/LLMs may only modify the linter (`check_burn_list.py`) to make it stricter, more accurate, or catch more errors. Relaxing rules, downgrading errors to warnings, or bypassing them for convenience is strictly forbidden.
- **Strict Patch Protocol**: Allowed targeted unified diffs and search-and-replace blocks for large files, while strictly maintaining the Zero-Guessing and exactness mandates (placeholders and truncation are strictly forbidden).
- **Framework Pattern Codification (ADRs 0013-0015)**: Formalized the Centralized Security Utility for safe `sudo` abstraction, Soft Dependency Injection for documentation hooks, and the Self-Writeable Fields idiom for user preference mutations.

## [1.0.0] - 2026-02-22
### Added
- **Semantic Anchor Architecture**: Implemented `[%ANCHOR: example_name]` traceability across the entire codebase to permanently link execution logic to Agile documentation.
- **Architecture Decision Records (ADRs)**: Formalized foundational system decisions (Hybrid Daemon, Zero-Sudo, Zero-DB, Semantic Anchors) in `docs/adrs/`.
- Comprehensive Operational Runbooks and User Journeys to guide deployments and workflows.
### Changed
- `LLM_GENERAL_REQUIREMENTS.md`: Refactored to act as a strict, lean checklist of operational rules, stripping out historical bloat.
- Security Paradigm: Enforced the **Zero-Sudo Architecture**, explicitly forbidding `.sudo()` in favor of the Service Account `with_user()` impersonation idiom.
