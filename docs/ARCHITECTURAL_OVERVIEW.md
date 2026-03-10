# System Architecture Overview

*Copyright © Bruce Perens K6BP. All Rights Reserved. This software is proprietary and confidential.*

This document explains the Hams.com architecture. Read this to understand how the system's design, data flow, and security work together.

---

## 1. Overall System Paradigm

Hams.com runs on **Odoo 19 Community**, but we tuned it to be a high-throughput, public-facing Amateur Radio portal rather than a standard ERP.

---

## 2. Core Architectural Choices

### A. The Daemon Offloading Pattern *(See ADR-0001)*
We offload heavy tasks to standalone Python daemons so they don't crash Odoo's web workers:
* **Batch Processing:** Parsing massive multi-megabyte ADIF log files.
* **High-Throughput Streaming:** The Ultimate DX Cluster Firehose utilizes `asyncio` + `websockets` connected directly to PostgreSQL to support tens of thousands of concurrent connections.

### B. Security & Privilege Isolation *(See ADR-0002, ADR-0005, ADR-0006)*
We enforce a strict **Zero-Sudo Architecture**. Daemons, APIs, and cron jobs authenticate using `with_user()` tied to specific Service Accounts. We limit these accounts with strict Access Control Lists (ACLs) so they only have the exact permissions they need. We flag them to block web logins, and we dynamically generate their passwords at runtime.

### C. Proxy Ownership
We let users build personal websites without giving them risky "Website Designer" access. A background Admin account physically owns the records, while custom ACLs give the actual user full control over their specific pages.

### D. GDPR & Privacy by Design
* **Immutable Public Records:** Amateur Radio contacts (QSOs) are exempt from right-to-erasure. During GDPR deletion, log entries are retained and anonymized using the ORM's `ondelete='set null'` constraint.
* **Geographic Fuzzing:** The mapping engine mathematically truncates Maidenhead Grid Squares to 4 characters for standard users, shifting map pins to the center of massive bounding boxes to obscure exact residential addresses.

---

## 3. Module Hierarchy

### Foundation Layer
* **`ham_base`:** The structural anchor. Centralizes shared UI elements to prevent cross-module dependency crashes.
* **`user_websites`**: Manages dynamic routing and personal web page provisioning.

### Identity & Onboarding Layer
* **`ham_onboarding`:** Handles multi-tiered identity verification (ARRL LoTW mTLS, QRZ bio scraping, FCC email OTP, Morse Code challenges).
* **`ham_callbook`:** The centralized regulatory directory. Syncs with external daemons.

### Application Layer
* **`ham_logbook`:** The core QSO tracker. Features automatic cross-indexing for platform confirmations.
* **`ham_dx_cluster` *(See ADR-0003)*:** Ingests live telnet DX spots utilizing a **Zero-DB I/O Architecture** to bypass PostgreSQL entirely.
* **`ham_classifieds`:** Peer-to-peer marketplace restricted strictly to verified operators.
* **`ham_shack`:** The Odoo Web Library (OWL) Operating Console SPA.
* **`ham_events`:** Manages active nets, rosters, and contests.
* **`ham_satellite`:** Provides live AMSAT satellite pass predictions calculated locally via `ephem`.
* **`ham_forum_extension`:** High-trust, spam-free Q&A platform utilizing Ham-CAPTCHA and Zero-Sudo moderation. See [ham_forum_extension.md](modules/ham_forum_extension.md).
* **`ham_propagation`:** Live HF propagation forecasting and MUF paths using an empirical ionospheric model. See [ham_propagation.md](modules/ham_propagation.md).

### SRE & DevOps Layer
* **`pager_duty`:** Enterprise alerting suite. Manages automated NOC dashboards, on-call calendar routing, and external push-monitoring (heartbeats).
* **`backup_management`:** Centralized GUI orchestrating Kopia and pgBackRest. Triggers automated restore drills and snapshot anomaly detection.
* **`database_management`:** PostgreSQL APM. Tracks dead tuples, slow queries, and provides wizards for memory optimization and High-Availability Patroni/PgBouncer cluster generation.

---

## 4. Daemons & The Service Account Registry

To protect Odoo from long-running tasks and respect our **Zero-Sudo Architecture (ADR-0002)**, we use external Python daemons and internal proxy accounts. 

We run every automated task or elevated action through a specific **Service Account**. We flag them with `is_service_account=True` to block web logins (ADR-0005) and use dynamic passwords to authenticate them (ADR-0006).

### A. The External Daemon Ring
*(These physical Python processes reside in `daemons/`, run in isolated `venv` wrappers, and communicate with Odoo via XML-RPC or RabbitMQ)*
* **`adif_processor`:** Consumes Base64 ADIF payloads from RabbitMQ, parses them, and batch-inserts QSOs.
* **`lotw_eqsl_sync`:** Gently polls ARRL and eQSL daily for new confirmations.
* **`noaa_swpc_sync`:** Fetches space weather metrics hourly.
* **`dx_firehose`:** Connects directly to PostgreSQL via `asyncpg` to broadcast real-time spots to WebSockets.
* **`pdns_sync`:** A CQRS worker that listens to RabbitMQ and pushes Odoo DNS updates to a PowerDNS SQLite backend.
* **`ham_dx_daemon`:** Maintains a persistent Telnet connection to global DX clusters to ingest live spots.
* **`amsat_tle_sync`:** Downloads daily orbital elements for satellite tracking.
* **`generalized_monitor` (Pager Duty):** External watchdog daemon that executes HTTP/TCP/ICMP checks and routes alerts independently of the Odoo WSGI workers.
* **Regulatory Syncs (`fcc_uls_sync`, `au_acma_sync`, etc.):** Nightly parsers for international callsign databases.
* **Event Syncs (`event_sync` tools):** Scrapes WA7BNM and ARRL portals for contest and hamfest data.

### B. Service Account & Proxy Role Mapping
The following internal Service Accounts execute the operations above (and internal UI escalations) with strict minimum privileges:

| Service Account Login | Target Module / Daemon | Role & Minimum Privilege |
| :--- | :--- | :--- |
| `mail_service_internal` | `ham_base` (Global) | Dedicated proxy for dispatching system emails and chatter posts to prevent bundling mail privileges into domain-specific accounts. |
| `gdpr_service_internal` | `ham_base` (Global) | Dedicated proxy for executing GDPR exports and anonymization across restricted tables, eliminating the need for `sudo().unlink()` exceptions. |
| `logbook_api_service_internal` | `ham_logbook` (`adif_processor`, `lotw_eqsl_sync`) | Validates HMAC API uploads, performs cross-matching, and batch-updates QSL statuses. Read/Write limited strictly to `ham.qso` and `ham.adif.queue`. |
| `fcc_sync_service` | `ham_callbook` (All Callbook syncs) | Bulk inserts regulatory data. Write access is restricted entirely to `ham.callbook`. |
| `dx_daemon_service` | `ham_dx_cluster` (`ham_dx_daemon`) | Pushes real-time Telnet spots into the Zero-DB memory router. |
| `dns_api_service_internal` | `ham_dns` (`pdns_sync`, ACME/DDNS) | Reads/Writes `ham.dns.zone` and `ham.dns.record` to provision domains and respond to automated Certbot/router IP updates. |
| `space_weather_service` | `ham_logbook` (`noaa_swpc_sync`) | Pushes SFI and K-Index metrics. Write access restricted to `ham.space.weather`. |
| `satellite_sync_service_internal` | `ham_satellite` (`amsat_tle_sync`) | Pushes daily orbital elements. Write access restricted to `ham.satellite.tle`. |
| `event_sync_service` | `ham_events` (Event Sync CLI) | Populates the calendar with contests and hamfests. Write access restricted to `event.event` and `ham.contest`. |
| `captcha_service_internal` | `ham_testing` (NCVEC Sync & UI) | Downloads NCVEC question pools and generates ephemeral session tokens for the frontend Ham-CAPTCHA. |
| `onboarding_service_internal` | `ham_onboarding` (Internal UI Proxy) | Safely handles Nginx mTLS headers, dispatches Official Email OTPs, and cascades callsign changes across the database without elevating the user's session. |
| `club_service_internal` | `ham_club_management` (Internal UI Proxy) | Allows authenticated club members to safely read active governance polls without granting them global `survey` read access. |
| `club_voter_service_internal` | `ham_club_management` (Internal UI Proxy) | Dedicated micro-privilege account strictly for casting votes securely, completely separated from the ability to read polls. |
| `public_router_internal` | `ham_base` (Internal UI Proxy) | Safely resolves `<callsign>.hams.com` vanity URLs to database IDs for unauthenticated visitors without exposing the `res.users` search matrix. |
| `system_provisioner_internal` | `ham_base` (Global) | Holds super privileges (`base.group_system`) and is assumed momentarily via `with_user()` to provision or edit core framework objects, immediately dropping the privilege thereafter to respect the micro-privilege architecture. |

---

## 5. Documentation & Traceability Architecture

Hams.com syncs its documentation directly with Agile planning, ops, and code. 

### The Semantic Anchor Architecture *(See ADR-0004)*
To permanently map documentation directly to execution logic without relying on brittle line numbers, the codebase utilizes **Semantic Anchors** (e.g., `# [ANCHOR: qso_cross_match]`). Stories, Journeys, and Runbooks explicitly reference these anchors, creating an unbroken trace from product requirements to the exact line of execution logic.

### Formal Agile & DevSecOps Suite
Developers and AI integrators MUST refer to and maintain the following directories:
* **`docs/adrs/` (Architecture Decision Records):** The immutable history of major architectural choices and their consequences.
* **`docs/stories/` (Agile User Stories):** Feature requirements implementing **Behavior-Driven Development (BDD)** criteria (Given/When/Then) to strictly guide unit testing.
* **`docs/journeys/` (User Journeys):** Macro-level overviews of end-to-end user experiences.
* **`docs/runbooks/` (Operational Runbooks):** Technical manuals for deployment, daemon management, and API integration.
* **`docs/security_models/` (Threat Models):** Formal **STRIDE** profiles identifying attack vectors and mitigations for distinct application boundaries.
* **`CHANGELOG.md`:** A structured timeline of additions, changes, and deprecations used to rapidly synchronize context across development sessions.
