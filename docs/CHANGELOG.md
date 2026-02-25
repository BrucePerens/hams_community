# Changelog

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to strict Semantic Versioning.

## [Unreleased]
### Changed
- **Conversational Tone Mandate (ADR-0056)**: Formally banned "oblique," academic, and dense corporate-speak from documentation, READMEs, and code comments. Rewrote root documentation to explain the system plainly and directly.
- **AST Linter Hardening (Burn List)**: Upgraded `check_burn_list.py` to recursively track SQL taints (e.g., intermediate f-strings passed to `cr.execute`), block universal attribute aliases for `.sudo()`, and evaluate `@http.route` controller context to drastically reduce false positives while making obfuscation and evasion impossible.
- **Linter Bypass Testing Mandate (ADR-0052)**: Formalized the rule that any use of a linter bypass tag (`burn-ignore` or `audit-ignore`) MUST be accompanied by an exhaustive automated unit test proving the safety and correctness of the bypassed operation.
- **ADR-0022 Refinement**: Formalized 'Bounded Chunking' requirements to prevent Out-Of-Memory (OOM) crashes and silent false-negatives during massive historical data array processing.
- **ADIF Compliance**: Fixed a bug where the ADIF Download API calculated string length by characters instead of UTF-8 byte length, causing external loggers to reject payloads containing Unicode characters.
- **Data Preservation**: Loosened the `ham.qso` idempotency SQL constraint to include `band` and `mode`, preventing data loss when older logging programs omit precise timestamps for same-day repeat contacts.
### Security
- **Hardware Relay CORS Hardening**: Locked down the Flask CORS origins in the generated `hams_local_relay.py` script to strictly allow `hams.com` domains, preventing local hardware hijacking by malicious third-party websites.
- **Zero-Sudo Enforcement**: Replaced illegal `.sudo()` escalations in the `ham_shack` module's award calculations with a dedicated, strictly scoped `award_service_internal` proxy account.
- **OOM Prevention**: Refactored the ADIF Upload API to stream file payloads through the HMAC validator in 64KB chunks rather than reading massive files entirely into WSGI memory.
### Added
- **Cloudflare UI Control Plane**: Provisioned the native Odoo frontend UI for the `cloudflare` module, allowing system administrators to review honeypot IP Bans, construct WAF rules, and push/pull firewall configurations directly to the edge without leaving the ERP. Fully mapped with JS UI Tours and BDD Stories.
- **Proposal 16 (Frictionless QRZ Verification)**: Upgraded the QRZ fallback verification flow with one-click clipboard copying, deep linking to the QRZ manager, and an AJAX auto-poller (`/api/v1/onboarding/qrz/status`) for seamless verification.
- **Proposal 15 (LoTW Golden Path UI)**: Replaced the text-heavy LoTW certificate installation instructions with an OS-aware interactive carousel containing visual GIF walkthroughs.
- **Proposal 14 (Hardware Setup Wizard)**: Added a local diagnostic UI (`/setup`) to the `hams_local_relay` daemon. It auto-discovers connected USB COM ports and saves configurations locally, allowing non-technical users to configure Hamlib without editing scripts.
- **Generalized Cloudflare Edge Orchestrator**: Transitioned the `cloudflare` module to Open Source. Introduced Advanced Edge APIs (WAF IP Banning, Cache-Tag Purging, Turnstile Verification, and Edge Context Parsing) for consumption by proprietary modules. Generalized edge caching rules to dynamically adapt to public vs. authenticated states without requiring hardcoded dependencies on frontend apps.
- **Proposal 09 (Coherent Caching Rollout)**: Expanded ADR-0047 memory caching to Group Websites and the Callbook Directory. Replaced synchronous PostgreSQL routing queries with O(1) `@tools.ormcache` lookups across all consumer endpoints, protected by distributed phase coherence.
- **Proposal 08 (Architectural Alignment)**: Enforced Reverse Traceability (ADR-0045) by injecting explicit `CONSUMERS:` mappings into core `ham_base` utilities (`security_utils`, `geo_utils`, `redis_pool`). Centralized all geographic mathematics (Maidenhead conversions and Haversine distances) into `ham.geo.utils` to satisfy the Deduplication Mandate (ADR-0046).
- **Fast-Fail Testing Architecture (ADR-0044)**: Formally mandated that all test deployment scripts (`START.sh`) must execute syntax, XML, and Burn List validation, aborting instantly on failure prior to executing database rebuilds.
- **Proposal 07 (ADR Alignment)**: Drafted refactoring requirements to enforce Redis pooling, eliminate data loss in paused Net Rosters, remove WSGI-blocking SMTP calls, and design a unified Moderation Command Center to satisfy the Solo-Maintainer mandate.
- **Solo-Maintainer Optimization (ADR-0043)**: Formalized the mandate for hyper-automation across testing, deployment, and administration. Requires self-healing systems and highly streamlined moderation queues to conserve the solo developer's cognitive load and time.
- **Cloudflare Bot Management (ADR-0041)**: Added API integration to leverage Cloudflare's Rulesets API. It dynamically provisions WAF rules to allow cryptographically verified bots (like Googlebot) while challenging unknown headless scrapers targeting API endpoints.
- **Dynamic Edge Tarpitting (ADR-0040)**: The `ham_events` module now pushes bot IP addresses into an ephemeral Redis cache when the silent honeypot is triggered. This sets the stage for Nginx to seamlessly apply 1-hour bandwidth tarpits to malicious scrapers.
- **Architectural Codification (ADRs 0036-0039)**: Formalized the Public Guest User Idiom (No-Sudo Forms), Edge-Enforced API Rate Limiting, Silent Honeypot Anti-Spam, and Strict Burn-Ignore Confinement.
- **SWL Collision Prevention & Study Heuristic**: Downgraded the automated SWL correlation engine (ADR-0018) to route Name/Zip matches to the Moderation Queue to prevent familial identity collisions. Introduced ADR-0035 to securely bypass this queue and automate the upgrade if the user has recently studied for the granted license class.
- **Semantic Anchor CI Enforcement**: Added `tools/verify_anchors.py` to automatically scan and fail the pipeline if documented anchors (ADR-0004) detach from the codebase.
- **Architectural Codification (ADRs 0032-0034)**: Formalized the Ephemeral Data UI Exemption, Infinite RF Record Retention, and implemented the automated DNS CQRS Reconciliation Loop.
- **Accessible DOM Syncing**: Upgraded the `ham_dx_cluster` OWL widget to securely queue background WebSocket updates when `aria-live` is paused, flushing them seamlessly upon resume to prevent screen reader data loss.
- **Ghost Record Prevention**: Updated documentation injection hooks (`ham_logbook` reference) to map dynamic `knowledge.article` entries to `ir.model.data`, ensuring clean uninstallation.
- **Architectural Codification (ADRs 0028-0031)**: Formalized additional implementation standards including At-Rest Fernet Encryption, the Local Hardware Relay Pattern, ARIA-Live Toggling for WebSockets, and Postgres Trigram Indexing.
- **Architectural Codification (ADRs 0022-0027)**: Formalized tactical implementation patterns into strict rules, including O(1) Memory Mapping, Async WSGI Offloading, Global Connection Pooling, Stateless HMAC Tokens, Ethical Crawling, and Postgres NOTIFY Truncation.
- **AEF Extraction Resiliency**: Upgraded `tools/aef_extract.py` to support whitespace-agnostic patching. Added the `--ignore-whitespace` flag to diff operations and a regex-based fallback for `search-and-replace` blocks to handle LLM indentation drift.
- **Shared Services & Soft Dependencies (ADR-0021)**: Formalized the mandate that shared service accounts must reside in `ham_base` and that cross-module integrations must utilize soft dependencies and `unittest.SkipTest` to guarantee isolated testability.
- **Location Data Precision (ADR-0017)**: Codified that location data is always stored at maximum precision. Grid squares generated from public RF records (DX spots, QSOs) are displayed at full resolution, while directory profile data is fuzzed for third-party viewing unless opted-in.
- **Elmering Forums (`ham_forum_extension`)**: Implemented a high-trust, spam-free educational Q&A platform extending Odoo's native forum, utilizing the Zero-Sudo architecture for moderation and CAPTCHA enforcement.
- **Live Propagation Maps (`ham_propagation`)**: Integrated real-time HF propagation forecasting using the VOACAP mathematical model, driven by the NOAA space weather daemon telemetry. Includes WCAG 2.1 AA compliant text-based forecasts.
- **Strict Linter Improvement Mandate**: Clarified that AI/LLMs may only modify the linter (`check_burn_list.py`) to make it stricter, more accurate, or catch more errors. Relaxing rules, downgrading errors to warnings, or bypassing them for convenience is strictly forbidden.
- **Strict Patch Protocol**: Allowed targeted unified diffs and search-and-replace blocks for large files, while strictly maintaining the Zero-Guessing and exactness mandates (placeholders and truncation are strictly forbidden).
- **Geographic Fuzzing Jitter**: Introduced a deterministic cryptographic jitter to the `ham_callbook` location algorithm. Fuzzed users in the same grid square now scatter around the regional center, preventing UI map marker stacking while preserving privacy bounds.
- **Framework Pattern Codification (ADRs 0013-0015)**: Formalized the Centralized Security Utility for safe `sudo` abstraction, Soft Dependency Injection for documentation hooks, and the Self-Writeable Fields idiom for user preference mutations.
- **Architectural Codification (ADRs 0008-0012)**: Formally documented existing architectural implementations including the Proxy Ownership Pattern, GDPR QSO Exemptions, Geographic Fuzzing Engine, HMAC API Idempotency, and the DNS CQRS architecture.
- **Documentation Boundaries (ADR-0007)**: Enforced strict separation between tactical deployment guides (`deploy/`) and strategic runbooks (`docs/runbooks/`). Runbooks are now stripped of CLI commands to prevent synchronization drift.
- **Secure Admin Password Management (ADR-0006)**: Eliminated plaintext admin passwords from configuration files. Introduced `tools/hash_admin_password.py` to auto-generate and inject PBKDF2-SHA512 hashes into `.env`, utilizing a raw SQL bypass in `ham_init` to prevent double-hashing.
- **Service Account Web Isolation (ADR-0005)**: Added `is_service_account` flag to `res.users` and intercepted the core `web_login` controller to permanently block daemons and service accounts from logging into the web UI.
- **Scoped Config Parameters**: Extended `ir.config_parameter` to allow service accounts to securely update `ham.` namespaced keys without requiring global system admin privileges.
- Behavior-Driven Development (BDD) Acceptance Criteria (Given/When/Then) applied to User Stories to drive unit testing.
- Formal DevSecOps STRIDE Threat Modeling profiles established in `docs/security_models/`.
### Fixed
- **AEF Extractor Permissions**: Fixed an issue in `tools/aef_extract.py` where atomic write operations stripped executable file permissions by ensuring `shutil.copymode` is applied.
- **Map Privacy Leak**: Fixed `ham_callbook` map API to properly truncate the grid square string in JSON payloads for users who have not opted into exact precision tracking.
- **Propagation Private Dashboard**: Fixed the `ham_propagation` API to successfully resolve the user's un-fuzzed 6-character grid from their linked `ham.callbook` profile instead of using an invalid missing model attribute.

## [1.0.0] - 2026-02-22
### Added
- **Semantic Anchor Architecture**: Implemented `[%ANCHOR: example_name]` traceability across the entire codebase to permanently link execution logic to Agile documentation.
- **Architecture Decision Records (ADRs)**: Formalized foundational system decisions (Hybrid Daemon, Zero-Sudo, Zero-DB DX Cluster, Semantic Anchors) in `docs/adrs/`.
- Comprehensive Operational Runbooks and User Journeys to guide deployments and workflows.
### Changed
- `LLM_GENERAL_REQUIREMENTS.md`: Refactored to act as a strict, lean checklist of operational rules, stripping out historical bloat.
- Security Paradigm: Enforced the **Zero-Sudo Architecture**, explicitly forbidding `.sudo()` in favor of the Service Account `with_user()` impersonation idiom.
- Database Integrity: Automated ADIF queue cleanup and orphaned QSO protections integrated into GDPR erasure hooks.
