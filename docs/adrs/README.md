# Architecture Decision Records (ADRs)

This directory contains the Architecture Decision Records (ADRs) that define the structural, security, and operational mandates for the platform.

## Master ADRs (Consolidated Paradigms)

* [MASTER 01: Security & Zero-Sudo Architecture](MASTER_01_SECURITY_ZERO_SUDO.md)
  Enforces the Service Account pattern, web isolation for daemons, strict limitations on `.sudo()`, View Abstraction, and OS-level Daemon Restrictions.
* [MASTER 02: Data Privacy, Location & Retention](MASTER_02_DATA_PRIVACY_RETENTION.md)
  Dictates GDPR erasure procedures, immutable public RF records, and geographic fuzzing.
* [MASTER 03: Edge Routing & Threat Mitigation](MASTER_03_EDGE_ROUTING_THREAT_MITIGATION.md)
  Defines Cloudflare edge orchestration, proactive caching, WAF bot verification, and dynamic Nginx tarpitting via silent honeypots.
* [MASTER 04: Modularity & Shared Services](MASTER_04_MODULARITY_SHARED_SERVICES.md)
  Mandates centralizing shared logic and Service Accounts into the `core_base` module to prevent monolithic cross-module entanglement.
* [MASTER 05: SWL Lifecycle & Automated Progression](MASTER_05_SWL_LIFECYCLE.md)
  Defines the SWL sandbox and automated correlation heuristics for licensing upgrades.
* [MASTER 06: DNS CQRS Architecture](MASTER_06_DNS_CQRS.md)
  Isolates DNS read infrastructure from Odoo state using RabbitMQ and PowerDNS SQLite.
* [MASTER 07: Zero-DB Architecture](MASTER_07_ZERO_DB_ARCHITECTURE.md)
  Prevents database bloat by caching real-time ephemeral data in Redis and broadcasting via WebSockets.
* [MASTER 08: Core Architecture & Performance](MASTER_08_CORE_ARCHITECTURE_PERFORMANCE.md)
  Details the hybrid monolith-daemon structure, distributed Redis caching, asynchronous bastions, and bounded chunking.
* [MASTER 09: API Integrations & Cryptography](MASTER_09_API_INTEGRATIONS.md)
  Defines HMAC Zero-Knowledge proofs, idempotency, ethical crawling, and strict headless API conventions.
* [MASTER 10: Core Identity & Access Control](MASTER_10_IDENTITY_ACCESS_CONTROL.md)
  Outlines the Proxy Ownership pattern, domain sandbox mandates, and secure admin password management.
* [MASTER 11: Agile Development & Documentation Workflow](MASTER_11_DEVELOPMENT_WORKFLOW_DOCS.md)
  Requires Semantic Anchor traceability, conversational documentation, fail-fast and Just-In-Time (JIT) dependencies, and strict log hygiene.
* [MASTER 12: QA & Automated Testing Mandates](MASTER_12_QA_TESTING_MANDATES.md)
  Enforces fast-fail CI/CD pipelines, deep AST test verification, strict syntactic parsing, and real-transaction testing methodologies.
* [MASTER 13: Frontend UX & Accessibility](MASTER_13_FRONTEND_UX.md)
  Governs ARIA live-regions and OLED burn-in protection for dashboards.
* [MASTER 14: LLM Context & Cognitive Load Management](MASTER_14_LLM_CONTEXT_MANAGEMENT.md)
  Establishes rules for AI agents, including prompt engineering, task workspaces, API contracts, and patching protocols.
* [MASTER 15: Domain Identity & Verification](MASTER_15_DOMAIN_IDENTITY.md)
  Defines identity verification fallbacks and the Shadow Profile indexing pattern.

## Standard ADRs

* [ADR 0073: Fail-Fast Dependency Resolution](0073_fail_fast_dependency_resolution.md)
  Mandates that all external Python dependencies must be declared in module manifests to trigger immediate startup halts instead of silent runtime failures.
