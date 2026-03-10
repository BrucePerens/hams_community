# Architecture Decision Records (ADRs)

This directory contains the Architecture Decision Records (ADRs) that define the structural, security, and operational mandates for the platform.

## Master ADRs (Consolidated Paradigms)

* [MASTER 01: Security & Zero-Sudo Architecture](MASTER_01_SECURITY_ZERO_SUDO.md)
  Enforces the Service Account pattern, web isolation for daemons, and strict limitations on `.sudo()` to prevent privilege escalation.
* [MASTER 02: Data Privacy, Location & Retention](MASTER_02_DATA_PRIVACY_RETENTION.md)
  Balances strict privacy laws with immutable public records, detailing GDPR erasure separation of privilege and geographic fuzzing.
* [MASTER 03: Edge Routing & Threat Mitigation](MASTER_03_EDGE_ROUTING_THREAT_MITIGATION.md)
  Defines edge orchestration, proactive caching, WAF bot verification, and dynamic tarpitting via silent honeypots.
* [MASTER 04: Modularity & Shared Services](MASTER_04_MODULARITY_SHARED_SERVICES.md)
  Mandates centralizing shared logic and Service Accounts into a core base module to prevent monolithic cross-module entanglement.
* [MASTER 05: Guest Lifecycle & Automated Progression](MASTER_05_SWL_LIFECYCLE.md)
  Outlines the Guest sandbox, identity trapping, and the correlation engine for automated user upgrades - much of this is relevant only a ham-radio-specific application.
* [MASTER 06: CQRS Architecture for External High-Load Services](MASTER_06_DNS_CQRS.md)
  Details the Command Query Responsibility Segregation architecture for isolating high-velocity reads from the core Odoo database.
* [MASTER 07: Zero-DB Architecture](MASTER_07_ZERO_DB_ARCHITECTURE.md)
  Explains ephemeral memory routing for high-velocity event ingestion using Odoo AbstractModels and Redis/Bus without PostgreSQL inserts.
* [MASTER 08: Core Architecture & Performance](MASTER_08_CORE_ARCHITECTURE_PERFORMANCE.md)
  Details the hybrid monolith-daemon structure, distributed Redis caching, asynchronous WSGI offloading, and bounded chunking for O(1) memory mapping.
* [MASTER 09: API Integrations & Cryptography](MASTER_09_API_INTEGRATIONS.md)
  Mandates HMAC-SHA256 zero-knowledge proofs, API idempotency, stateless tokens, and at-rest encryption for secrets.
* [MASTER 10: Core Identity & Access Control](MASTER_10_IDENTITY_ACCESS_CONTROL.md)
  Outlines the Proxy Ownership pattern, domain sandbox mandates (restricting community users from `base.group_user`), and secure admin password management.
* [MASTER 11: Agile Development & Documentation Workflow](MASTER_11_DEVELOPMENT_WORKFLOW_DOCS.md)
  Requires Semantic Anchor traceability, conversational documentation, Just-In-Time (JIT) self-healing dependencies, and a strict "no cybercrud" log policy.
* [MASTER 12: QA & Automated Testing Mandates](MASTER_12_QA_TESTING_MANDATES.md)
  Enforces fast-fail CI/CD pipelines, deep AST test verification for linter bypasses, JS UI tours for all views, and cache query counting.
* [MASTER 13: Frontend UX & Accessibility](MASTER_13_FRONTEND_UX.md)
  Covers accessible real-time DOM mutation (aria-live) and OLED burn-in protection for always-on NOC dashboards.
* [MASTER 14: LLM Context & Cognitive Load Management](MASTER_14_LLM_CONTEXT_MANAGEMENT.md)
  Establishes rules for AI agents, including the use of isolated task workspaces, API contracts over raw implementations, and granular search-and-replace patching.
* [MASTER 15: Domain Identity & Verification](MASTER_15_DOMAIN_IDENTITY.md)
  Defines identity verification fallbacks and shadow profile indexing to bypass internal ERP security constraints.

## Standard ADRs

* [ADR 0060: Strict Syntactic Parsing Mandate](0060_strict_syntactic_parsing_mandate.md)
  Bans the use of regular expressions for parsing structured data (XML, Python, JSON) in favor of proper AST parsers.
* [ADR 0061: Real Transaction Testing Facility](0061_real_transaction_testing_facility.md)
  Introduces the `RealTransactionCase` for tests requiring physical database commits (e.g., background daemons, pub/sub), restricting its use to prevent performance penalties.
* [ADR 0062: Micro-Service Account Pattern](0062_micro_service_account_pattern.md)
  Mandates breaking monolithic service accounts into hyper-specific proxy accounts dedicated to single operational flows.
* [ADR 0063: AST Linter Anti-Evasion Protocols](0063_linter_anti_evasion_protocols.md)
  Upgrades the linter to detect and block "dead code" or "loop" evasions used to bypass CI/CD test verification.
* [ADR 0064: Micro-Service Strict ACL Isolation](0064_micro_service_strict_acl_isolation.md)
  Forbids assigning broad internal ERP groups to Service Accounts just to bypass ORM cascade traps, requiring microscopic explicit ACLs instead.
* [ADR 0064: Shadow Profile Pattern](0064_shadow_profile_pattern.md)
  Decouples identity lookups from core ERP security by using isolated PostgreSQL views and a proxy account.
* [ADR 0065: Headless API Translation Ban](0065_headless_api_translation_ban.md)
  Bans the use of the `_()` translation wrapper around string literals in headless API JSON responses to prevent context crashes.
* [ADR 0066: Secure Cached Resolver Pattern](0066_secure_cached_resolver_pattern.md)
  Requires high-frequency cached lookups to accept an `override_svc_uid` parameter to execute database queries safely under the caller's specific micro-service context.
* [ADR 0067: Zero-Knowledge API Proofs (HMAC-SHA256)](0067_zero_knowledge_api_proofs.md)
  Mandates Proof-of-Possession cryptographic handshakes for authenticated connections to prevent credential leakage.
* [ADR 0068: PostgreSQL View Security & Optimization Pattern](0068_postgresql_view_security_pattern.md)
  Mandates using PostgreSQL views for SQL-level data masking and strict ACL isolation for public endpoints.
* [ADR 0069: Persona Capability Limit & View Abstraction](0069_persona_capability_limit.md)
  Forbids escalating privileges to present masked data; requires native reads against abstracted SQL views.
* [ADR 0070: OS-Level Daemon Restriction & Airgapped Hardware Spooling](0070_os_level_daemon_restriction.md)
  Mandates strict chrooted privilege de-escalation, systemd sandboxing for network daemons, and airgapped JSON spooling for hardware telemetry to prevent RCE escalation.
* [ADR 0071: Asynchronous Bastion Pattern for External I/O](0071_asynchronous_bastion_pattern.md)
  Mandates that high-I/O daemons use transactional message queue dispatches with XML-RPC callbacks to prevent Odoo WSGI workers from hanging.
* [ADR 0072: LLM Instruction & Prompt Engineering Standards](0072_llm_instruction_and_prompt_engineering.md)
  Codifies prompt engineering techniques (SYSTEM OVERRIDE, Positive Constraints, Recency Bias) to securely override the LLM's generic base instructions.
