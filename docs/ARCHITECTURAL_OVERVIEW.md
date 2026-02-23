# System Architecture Overview

*Copyright © Bruce Perens K6BP. Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).*

This document provides a hierarchical, comprehensive overview of the community modules architecture.

---

## 1. Overall System Paradigm

These modules are designed for **Odoo 19 Community**, adapting it into a highly concurrent, multi-tenant community platform that allows individual users to securely manage their own spaces.

---

## 2. Core Architectural Choices

### A. Security & Privilege Isolation *(See ADR-0002, ADR-0005, ADR-0006)*
The system utilizes a strict **Zero-Sudo Architecture**. Automated tasks, background jobs, and permission escalations execute via `with_user()` bound to dedicated, non-human Service Accounts. These accounts possess surgically limited Access Control Lists (ACLs), ensuring least-privilege execution across all boundaries.

### B. Proxy Ownership *(See ADR-0008)*
To allow users to build personal websites without granting them backend "Website Designer" capabilities, an over-arching Admin system account "owns" the website records, while custom ACLs grant the specifically mapped user full CRUD rights over their designated web directory.

---

## 3. Module Hierarchy

* **`user_websites`**: Manages dynamic routing and personal web page provisioning securely. Includes blogging, team-based shared group sites, and community moderation tools.
* **`compliance`**: The global compliance enforcer. Ensures active websites natively respect ePrivacy/Cookie directives and provisions non-destructive boilerplate legal policies.
* **`manual_library`**: A clean-room hierarchical documentation tool providing API drop-in compatibility for standard `knowledge` integration without Enterprise requirements.

---

## 4. Documentation & Traceability Architecture

We employ a highly synchronized documentation strategy linking Agile planning, operational procedures, and execution logic.

### The Semantic Anchor Architecture *(See ADR-0004)*
To permanently map documentation directly to execution logic without relying on brittle line numbers, the codebase utilizes **Semantic Anchors** (e.g., `# [%ANCHOR: unique_name]`). Stories, Journeys, and Runbooks explicitly reference these anchors, creating an unbroken trace from product requirements to the exact line of execution logic.
