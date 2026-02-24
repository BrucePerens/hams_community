# System Architecture Overview

*Copyright © Bruce Perens K6BP. All Rights Reserved. This software is proprietary and confidential.*

This document provides a hierarchical, comprehensive overview of the Hams.com platform architecture. It is intended for human developers, system administrators, and AI integrators to understand the structural design, data flow, and security paradigms of the system.

---

## 1. Overall System Paradigm

Hams.com is a specialized, high-throughput Amateur Radio portal built on top of **Odoo 19 Community**. It diverges from standard ERP usage by functioning as a highly concurrent, public-facing community platform.

---

## 2. Core Architectural Choices

### A. The Daemon Offloading Pattern *(See ADR-0001)*
Tasks that would typically cause Odoo web workers to timeout or consume excessive memory are strictly offloaded to standalone systemd-managed Python daemons:
* **Batch Processing:** Parsing massive multi-megabyte ADIF log files.
* **High-Throughput Streaming:** The Ultimate DX Cluster Firehose utilizes `asyncio` + `websockets` connected directly to PostgreSQL to support tens of thousands of concurrent connections.

### B. Security & Privilege Isolation *(See ADR-0002, ADR-0005, ADR-0006)*
The system utilizes a strict **Zero-Sudo Architecture**. External daemons, APIs, and background cron jobs authenticate and execute via `with_user()` bound to dedicated, non-human Service Accounts. These accounts possess surgically limited Access Control Lists (ACLs), ensuring least-privilege execution across all boundaries. They are explicitly flagged to deny interactive web logins, and their passwords are mathematically generated and injected dynamically at runtime.

### C. Proxy Ownership
To allow users to build personal websites without granting them backend "Website Designer" capabilities, an over-arching Admin system account "owns" the website records, while custom ACLs grant the specifically mapped user full CRUD rights over their designated web directory.

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

---

## 4. Daemons & The Service Account Registry

To ensure the Odoo WSGI workers are protected from long-running I/O tasks, and to adhere to the **Zero-Sudo Architecture (ADR-0002)**, the platform relies on external Python daemons and internal proxy accounts. 

Every automated task or elevated internal operation executes via a dedicated, strictly scoped **Service Account**. These accounts are flagged with `is_service_account=True` to mathematically prevent interactive web logins (ADR-0005) and are authenticated via dynamically generated environment passwords (ADR-0006).

### A. The External Daemon Ring
*(These physical Python processes reside in `daemons/`, run in isolated `venv` wrappers, and communicate with Odoo via XML-RPC or RabbitMQ)*
* **`adif_processor`:** Consumes Base64 ADIF payloads from RabbitMQ, parses them, and batch-inserts QSOs.
* **`lotw_eqsl_sync`:** Gently polls ARRL and eQSL daily for new confirmations.
* **`noaa_swpc_sync`:** Fetches space weather metrics hourly.
* **`dx_firehose`:** Connects directly to PostgreSQL via `asyncpg` to broadcast real-time spots to WebSockets.
* **`pdns_sync`:** A CQRS worker that listens to RabbitMQ and pushes Odoo DNS updates to a PowerDNS SQLite backend.
* **`ham_dx_daemon`:** Maintains a persistent Telnet connection to global DX clusters to ingest live spots.
* **`amsat_tle_sync`:** Downloads daily orbital elements for satellite tracking.
* **Regulatory Syncs (`fcc_uls_sync`, `au_acma_sync`, etc.):** Nightly parsers for international callsign databases.
* **Event Syncs (`event_sync` tools):** Scrapes WA7BNM and ARRL portals for contest and hamfest data.

### B. Service Account & Proxy Role Mapping
The following internal Service Accounts execute the operations above (and internal UI escalations) with strict minimum privileges:

| Service Account Login | Target Module / Daemon | Role & Minimum Privilege |
| :--- | :--- | :--- |
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
| `public_router_internal` | `ham_base` (Internal UI Proxy) | Safely resolves `<callsign>.hams.com` vanity URLs to database IDs for unauthenticated visitors without exposing the `res.users` search matrix. |
| `user_user_websites_service_account` | `user_websites` (Proxy Ownership) | Evaluates custom record rules, then temporarily escalates to provision/edit Website Pages, Blogs, and Classifieds on behalf of the verified owner. |

---

## 5. Documentation & Traceability Architecture

Hams.com employs a highly synchronized documentation strategy linking Agile planning, operational procedures, and execution logic. 

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
